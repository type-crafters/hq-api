import boto3
import json
import os

region_name = 'us-east-1'
bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']

s3 = boto3.client('s3', region_name=region_name)
db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)


# Lambda handler 'delete_project'
def lambda_handler(event, context):
    try:
        print("This is a change made by the CI/CD pipeline.....")
        try:
            project_id = event['pathParameters']['id']
        except KeyError:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'No appropriate project id was sent in the request.'
                })
            }
        else:
            response = table.delete_item(Key={'id': project_id}, ReturnValues='ALL_OLD')
            if 'Attributes' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'message': f"The project with the provided id ({project_id}) was not found."
                    })
                }
            
            object_key = response['Attributes'].get('image')
            if object_key:
                s3.delete_object(Bucket=bucket_name, Key=object_key)

            return {
                'statusCode': 204
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"An unknown error of type {e.__class__.__name__} caused the server to return 500 Internal Server Error",
                'details': str(e)
            })
        }