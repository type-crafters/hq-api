import base64
import boto3
import io
import json
import os
from typing import Any
from multipart import MultipartParser
from uuid import uuid4

region_name = 'us-east-1'
bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']

s3 = boto3.client('s3', region_name=region_name)
db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)

# Lambda handler 'create_project'
def lambda_handler(event: dict[str, Any], context):
    try:
        body = event['body']

        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body)
        else:
            body = body.encode()

        body = io.BytesIO(body)
        content_type = event.get('headers', {}).get('content-type', 'text/plain')

        if not content_type.startswith('multipart/form-data'):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f"Expected 'Content-Type' header to be 'multipart/form-data' but got '{content_type}'."
                })
            }
        if 'boundary=' not in content_type: 
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing boundary in Content-Type header'
                })
            }
        
        form_data = MultipartParser(body, boundary=content_type.split('boundary=')[1].encode())

        partition_key = str(uuid4())
        data = { 'id': partition_key }


        for part in form_data.parts():
            filename = part.filename
            if filename is not None:
                if 'image' in data:
                    continue

                ext = os.path.splitext(filename)[1]
                file_path = f"projects/{partition_key}{ext}"

                s3.put_object(
                    Bucket=bucket_name,
                    Key=file_path,
                    Body=part.file.read(),
                    ContentType=part.headers.get('content-type', 'application/octet-stream')
                )
                data['image'] = file_path
                
            elif part.value is not None:
                    data[part.name] = part.value

        table.put_item(Item=data)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Project added to database',
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