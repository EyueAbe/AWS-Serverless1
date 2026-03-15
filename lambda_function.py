import json
import boto3
import os

# Initialize the Bedrock client
bedrock = boto3.client(service_name='bedrock-runtime')

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


def lambda_handler(event, context):
    try:
        # Parse the incoming request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)

        # Support both single prompt and conversation history
        messages = body.get('messages', None)
        prompt = body.get('prompt', None)

        # Build messages array
        if messages:
            formatted_messages = messages
        elif prompt:
            formatted_messages = [{"role": "user", "content": prompt}]
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'error': 'No prompt or messages provided'})
            }

        # Call Bedrock
        model_id = os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001')

        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": formatted_messages
            })
        )

        response_body = json.loads(response['body'].read())
        reply = response_body['content'][0]['text']

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'response': reply})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)})
        }
