Cloudy — Serverless AWS Guide Chatbot

Cloudy is a fully serverless AI chatbot built on AWS that helps users learn AWS concepts, explore projects, and prepare for certifications.
The application runs entirely on managed AWS services and demonstrates how modern cloud architectures can deliver scalable AI applications without managing servers. 
Users can sign in to save their conversation history across sessions or use the chatbot as a guest for a temporary chat experience.


Live Demo: (https://main.d3n29xe3zzcmii.amplifyapp.com/)
Tech Stack: AWS Lambda, API Gateway, Amazon Bedrock, Cognito, DynamoDB, Amplify


Preview

<img width="520" height="691" alt="image" src="https://github.com/user-attachments/assets/367f83e5-4dd2-45a5-8def-b8e90c44a0ef" />
<img width="1818" height="808" alt="image" src="https://github.com/user-attachments/assets/c470d7e1-aaec-4a1c-8593-8462dae4b490" />





Architecture Overview

<img width="1236" height="652" alt="image" src="https://github.com/user-attachments/assets/7567daba-b1f3-4e8c-8907-6b04598283ca" />
This architecture allows the application to scale automatically while minimizing operational overhead.







AWS Services Used:
- AWS Amplify: Hosts the frontend and delivers the static website globally through AWS infrastructure. Deployments can be triggered directly from a GitHub repository.
- Amazon Cognito: Provides authentication for users. Registered users can log in and have their chat history associated with their account.
- Amazon API Gateway: Acts as the entry point for all API requests. It receives chat messages from the frontend and forwards them to the Lambda backend.
- AWS Lambda: Runs the backend logic in Python. Lambda processes incoming requests, retrieves chat history when needed, invokes the Bedrock model, and returns responses to the client.
- Amazon Bedrock: Provides access to foundation models. Cloudy uses the Claude Haiku model to generate responses to AWS related questions.
- Amazon DynamoDB: Stores conversation history for authenticated users. Each conversation session is stored using the user ID and session ID as keys.
- AWS IAM: Manages permissions between services. Lambda is granted permission to invoke Bedrock and read and write data in DynamoDB.
- Amazon CloudWatch: Automatically captures logs from Lambda executions for debugging and monitoring.





Key Features:
- User authentication using Amazon Cognito
- Guest mode for one time chat sessions
- Conversation history stored in DynamoDB
- AI responses generated using Amazon Bedrock
- Serverless architecture with no infrastructure management
- Clean chat interface with Markdown formatted responses





Deployment Overview:
1. Create DynamoDB Table
  - Create a table named cloudy-chat-history.
  - Partition key (userId)
  - Sort key (sessionId)

2. Configure Cognito
  - Create a Cognito User Pool and configure an application client without a client secret.
  - Record:
    - User Pool ID
    - Client ID
These values are required by the frontend.

3. Deploy Lambda Function
  - Create a Lambda function using the Python runtime and upload the backend code.
  - Configure environment variables and ensure the execution role has permission to:
     - Invoke Bedrock models
     - Access DynamoDB

4. Configure API Gateway
  - Create a REST API connected to the Lambda function using Lambda proxy integration.
  - Deploy the API and copy the generated Invoke URL.

5. Update Frontend Configuration
  - Update the frontend configuration with:
    - API Gateway Invoke URL
    - Cognito User Pool ID
    - Cognito Client ID

6. Host with Amplify
  - Upload the frontend files to a GitHub repository and connect the repository to AWS Amplify for deployment.
  - Amplify will host the application and provide a public URL.






Cost Considerations:
The application is designed to run primarily within AWS Free Tier limits for development and demonstration purposes. Most services such as Lambda, API Gateway, and DynamoDB have generous free usage tiers. The main cost comes from Amazon Bedrock inference, which charges per request to the model. For light usage the cost remains minimal.






Conversation Flow:
User sends message from browser
        ↓
Frontend sends request to API Gateway
        ↓
API Gateway triggers Lambda function
        ↓
Lambda retrieves user history from DynamoDB
        ↓
Lambda sends prompt to Amazon Bedrock
        ↓
Bedrock generates response
        ↓
Lambda stores updated history in DynamoDB
        ↓
Response returned to frontend





  
- Layer	             │         Technology
////////////////////////////////////////////////////
- Frontend	         │         HTML, CSS, JavaScript
- Authentication	   │         Amazon Cognito
- Hosting	           │         AWS Amplify
- API Layer	         │         Amazon API Gateway
- Backend	           │         AWS Lambda 
- Database	         │         Amazon DynamoDB
- AI Model	         │         Amazon Bedrock (Claude Haiku)
- Monitoring	       │         Amazon CloudWatch



