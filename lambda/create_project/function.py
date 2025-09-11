import base64
import json
import os
from typing import Any
from email.parser import BytesParser
from email.policy import default
from uuid import uuid4
import boto3

region_name = 'us-east-1'
bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']

s3 = boto3.client('s3', region_name=region_name)
db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)

# Lambda handler 'create_project'
def handler(event: dict[str, Any], context):
    body = event['body']

    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body)
    else: 
        body = body.encode('utf-8')

    parser = BytesParser(policy=default)
    message = parser.parsebytes(body)

    partition_key = str(uuid4())
    data = {'id': partition_key}

    for part in message.iter_parts():
        if part.get_content_disposition() == 'form-data':
            name = part.get_param('name', header='content-disposition')
            filename = part.get_filename()
            content = part.get_payload(decode=True)
            if isinstance(content, str):
                content = content.encode('utf-8')

            if name == 'image' and filename:
                ext = os.path.splitext(filename)[1]
                file_path = '/'.join('projects', f"{partition_key}{ext}")
                s3.put_object(
                    Bucket=bucket_name,
                    Key=file_path,
                    Body=content,
                    ContentType=part.get_content_type()
                )
                data['image'] = file_path
            else: 
                text = content.decode('utf-8')
                try:
                    data[name] = json.loads(text)
                except json.JSONDecodeError:
                    data[name] = text

    table.put_item(Item=data)

    return {
        'statusCode': 201,
        'body': json.dumps({
            'message': 'Project added to database',
            'id': partition_key
        })
    }
