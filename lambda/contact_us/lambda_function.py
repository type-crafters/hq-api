import json
import boto3
import os
from datetime import datetime

region_name = 'us-east-1'
table_name = os.environ['MESSAGES_TABLE_NAME']

db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)

# Lambda handler 'contact_us'
def lambda_handler(event, context):
    try:
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Check fields required
        first_name = body.get('firstName', '').strip()
        last_name = body.get('lastName', '').strip()
        email = body.get('email', '').strip()
        subject = body.get('subject', '').strip()
        message = body.get('message', '').strip()
        
        # Basic validation
        if not all([first_name, last_name, email, subject, message]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'All fields are required'
                })
            }
        
        # Check email format
        if '@' not in email or '.' not in email:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid email format'
                })
            }
        
        # Generate unique ID
        timestamp = datetime.utcnow().isoformat()
        message_id = f"{timestamp}_{email}"
        
        # Save data to DynamoDB
        table.put_item(
            Item={
                'messageId': message_id,
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'subject': subject,
                'message': message,
                'timestamp': timestamp,
                'status': 'pending'
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Mensaje enviado exitosamente',
                'messageId': message_id
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid JSON format'
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"An unknown error of type {e.__class__.__name__} caused the server to return 500 Internal Server Error",
                'details': str(e)
            })
        }