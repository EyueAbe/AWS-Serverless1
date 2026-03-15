import json
import boto3
import os

# Initialize Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.environ.get("AWS_REGION", "us-east-1")
)


def lambda_handler(event, context):
    """
    AWS Lambda handler for a serverless chatbot backend.

    Flow:
    1. Receives a POST request from API Gateway
    2. Extracts the user's prompt and optional conversation history
    3. Sends the request to Amazon Bedrock
    4. Returns the model response back through API Gateway
    """

    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))

        input_text = body.get("prompt", "").strip()
        conversation_history = body.get("conversation_history", "[]")

        # Validate required input
        if not input_text:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": "Missing required field: prompt"
                })
            }

        # Use environment variable if provided, otherwise default model ID
        model_id = os.environ.get(
            "BEDROCK_MODEL_ID",
            "us.anthropic.claude-opus-4-20250514-v1:0"
        )

        # Build message content
        user_message = (
            "Here is the conversation history:\n"
            f"{conversation_history}\n\n"
            "Here is the new user input:\n"
            f"{input_text}"
        )

        # Prepare Bedrock request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }

        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )

        # Parse model response
        response_body = json.loads(response["body"].read())
        generated_text = response_body["content"][0]["text"]

        # Return successful response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "response": generated_text,
                "model_id": model_id
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }
