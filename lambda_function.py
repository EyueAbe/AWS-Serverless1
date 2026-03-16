import json
import boto3
import os
import time
import base64

# Connect to AWS services
bedrock = boto3.client(service_name='bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cloudy-chat-history')

SYSTEM_PROMPT = """You are Cloudy, a friendly and knowledgeable AWS guide and tutor. Your personality is warm, encouraging, and casual. Like a senior engineer who genuinely loves helping people learn AWS.

Your expertise covers:
- **Getting Started with AWS**: Helping complete beginners understand what AWS is, how to create an account, navigate the console, and understand core concepts like regions, availability zones, and the free tier.
- **Hands-on Projects**: Walking users through real AWS projects step by step — serverless apps, static websites, databases, APIs, containers, CI/CD pipelines, and more.
- **AWS Certifications**: Guiding users through all AWS certification paths (Cloud Practitioner, Solutions Architect, Developer, SysOps, DevOps, Specialty certs). Explaining what to study, recommending resources, sharing exam tips, and helping with practice questions.
- **Troubleshooting**: Helping debug common AWS errors, IAM permission issues, networking problems, and service misconfigurations.
- **Best Practices**: Advising on cost optimization, security, scalability, and the Well-Architected Framework.

Guidelines:
- Always be encouraging, AWS can be overwhelming and users need confidence.
- Use simple analogies to explain complex concepts.
- When walking through steps, be specific and clear.
- If a user seems to be a beginner, slow down and explain fundamentals.
- If a user is advanced, match their level and go deeper.
- Always be honest if you're unsure about something — AWS updates frequently.
- Occasionally add a friendly tip or fun fact about AWS.
- Keep responses focused and not too long unless a detailed explanation is needed.

Remember: Your goal is to make AWS accessible, fun, and learnable for everyone, from total beginners to engineers studying for advanced certs."""



MAX_MESSAGES = 200

CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def get_user_id(token):
    # Decode the Cognito JWT to get the user's unique ID
    try:

        middle = token.split('.')[1]
        middle += '=' * (4 - len(middle) % 4)
        user_info = json.loads(base64.urlsafe_b64decode(middle))
        return user_info.get('sub')
        
    except Exception as e:
        print('Token error:', str(e))
        return None


def load_history(user_id, session_id):
    # Get chat history from DynamoDB
    try:

        result = table.get_item(Key={'userId': user_id, 'sessionId': session_id})
        item = result.get('Item')
        return item['messages'] if item and 'messages' in item else []
    except Exception as e:
        print('Load error:', str(e))
        return []



def save_history(user_id, session_id, messages):
    # Save chat history to DynamoDB
    try:
        if len(messages) > MAX_MESSAGES:
            messages = messages[-MAX_MESSAGES:]
        table.put_item(Item={
            'userId': user_id,
            'sessionId': session_id,
            'messages': messages,
            'updatedAt': int(time.time())
        })
    except Exception as e:
        print('Save error:', str(e))


def lambda_handler(event, context):

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', event)

        user_message = body.get('prompt') or body.get('message')
        session_id   = body.get('sessionId', 'default')
        auth_token   = body.get('authToken')
        is_guest     = body.get('isGuest', False)

        if not user_message:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': 'No message provided'})
            }

        # Check if user is logged in or a guest
        user_id    = None
        save_to_db = False

        if not is_guest and auth_token:
            user_id = get_user_id(auth_token)
            if user_id:
                save_to_db = True

        # Load history from DynamoDB for logged in users, or use what the frontend sent for guests
        chat_history = load_history(user_id, session_id) if save_to_db else body.get('messages', [])
        chat_history.append({'role': 'user', 'content': user_message})


        # Call Bedrock
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1024,
                'system': SYSTEM_PROMPT,
                'messages': chat_history
            })
        )

        reply = json.loads(response['body'].read())['content'][0]['text']
        chat_history.append({'role': 'assistant', 'content': reply})

        if save_to_db:
            save_history(user_id, session_id, chat_history)


        return {

            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'response': reply,
                'messageCount': len(chat_history),
                'savedToCloud': save_to_db
            })
        }


    except Exception as e:
        print('Error:', str(e))
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
