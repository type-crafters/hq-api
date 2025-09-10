import json

# Lambda handler 'update_message'
def handler(event, context):
    return {
        'statusCode': 200,
        'message': json.dumps('Hello from lambda!')
    }