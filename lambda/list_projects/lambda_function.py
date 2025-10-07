import boto3
import json
import os

region_name = 'us-east-1'
bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']

s3 = boto3.client('s3', region_name=region_name)
db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)

# Lambda handler 'list_projects'
def lambda_handler(event, context):
    try:
        print("This is a change made by the CI/CD pipeline.....")
        res = table.scan()
        items = res.get('Items', [])
        if items:
            while 'LastEvaluatedKey' in res:
                res = table.scan(ExclusiveStartKey = res['LastEvaluatedKey'])
                items.extend(res.get('Items', []))
            items = [{**row,
                        'image': s3.generate_presigned_url('get_object', Params={
                            'Bucket': bucket_name,
                            'Key': row['image']
                        }, ExpiresIn=3600) if 'image' in row else None
                    } for row in items]
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"An unknown error of type {e.__class__.__name__} caused the server to return 500 Internal Server Error",
                'details': str(e)
            })
        }