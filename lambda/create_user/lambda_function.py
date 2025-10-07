import bcrypt
import boto3
import json
import os
import secrets
import smtplib
import string
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from uuid import uuid4

region_name = 'us-east-1'
email_address = os.environ['EMAIL_ADDRESS']
app_password = os.environ['APP_PASSWORD']
table_name = os.environ['TABLE_NAME']

db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)

# Lambda handler 'create_user'
def lambda_handler(event, context):
    try:
        print("This is a change made by the CI/CD pipeline..")
        body = json.loads(event['body'])
        data = {}
        try:
            data['firstName'] = body['firstName']
            data['lastName'] = body['lastName']
            data['email'] = body['email']
            data['permissions'] = body['permissions']
        except KeyError:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing required information for user creation.'
                })
            }
        else:
            partition_key =  str(uuid4())
            data['id'] = partition_key
            initial_password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))

            hashed_pw = bcrypt.hashpw(initial_password.encode(), bcrypt.gensalt()).decode()
            data['password'] = hashed_pw
            table.put_item(Item={
                **data, 
                'initialPassword': hashed_pw
            })

            message = MIMEMultipart('alternative')
            message['Subject'] = 'TypeCrafters HQ Admin Credentials'
            message['From'] = f"TypeCrafters<{email_address}>"
            message['To'] = data['email']
            
            env = Environment(loader=FileSystemLoader('.'))
            mail = env.get_template('template.html')

            message.attach(MIMEText('Welcome to our service! Please use a modern email client to view the full message.', 'plain'))
            message.attach(MIMEText(mail.render({**data, 'initialPassword': initial_password, 'currentYear': datetime.now().year}), 'html'))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(email_address, app_password)
                server.send_message(message)

            return {
                'statusCode': 201,
                'body': json.dumps({
                    'message': 'User created',
                    'id': partition_key
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