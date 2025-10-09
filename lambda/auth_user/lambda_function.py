from typing import Literal
import bcrypt
import boto3
from datetime import datetime, timedelta, UTC
import json
import jwt
import os
import traceback

region_name = 'us-east-1'
table_name = os.environ['ADMIN_USERS_TABLE_NAME']
secret_key = os.environ['SECRET_KEY']

db = boto3.resource('dynamodb', region_name=region_name)
table = db.Table(table_name)


def write_cookie(
    name: str,
    value: str,
    http_only: bool = False,
    secure: bool = False,
    domain: str | None = None,
    path: str = '/',
    same_site: Literal['Strict', 'Lax', 'None'] = 'Strict',
    expires: datetime | None = None,
    max_age: int = 3600,
) -> str:
    if expires is None:
        expires = datetime.now(UTC) + timedelta(seconds=max_age)
    return (
        f"{name}={value}; "
        f"{f"Domain={domain}; " if domain else ''}"
        f"Path={path}; "
        f"SameSite={same_site}; "
        f"Expires={expires.strftime('%a, %d-%b-%Y %H:%M:%S GMT')}; "
        f"Max-Age={max_age}; "
        f"{'HttpOnly; ' if http_only else ''}"
        f"{'Secure;' if secure else ''}"
    )


# Lambda handler 'auth_user'
def lambda_handler(event, context):
    try:
        try:
            body = json.loads(event['body'])
            email = body['email']
            password = body['password']
        except KeyError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing or inappropriate request body'}),
            }
        else:
            response = table.query(
                IndexName='email-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email),
            )
            try: 
                row = response['Items'][0]
            except IndexError:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'User not found'}),
                }
            else:
                try:
                    pw_hash = row['password']
                except KeyError:
                    return {
                        'statusCode': 500,
                        'body': json.dumps({
                            'message': 'Malformed user data. Please contact the organization.'
                        }),
                    }
                else:
                    if bcrypt.checkpw(password.encode('utf-8'), pw_hash.encode('utf-8')):
                        payload = {
                            'id': row['id'],
                            'email': email,
                            'exp': int((datetime.now(UTC) + timedelta(hours=1)).timestamp())
                        }

                        token = jwt.encode(payload, secret_key, algorithm='HS256')

                        return {
                            'statusCode': 200,
                            'body': json.dumps({ 'message': 'User authenticated' }),
                            'cookies': [
                                write_cookie(name='token', value=token, path='/', http_only=True, secure=True, max_age=3600)
                            ]
                        }
                    else:
                        return {
                            'statusCode': 401,
                            'body': json.dumps({'message': 'Unauthorized'}),
                        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"An unknown error of type {e.__class__.__name__} caused the server to return 500 Internal Server Error",
                'details': str(e),
                'traceback': traceback.format_exc()
            }),
        }