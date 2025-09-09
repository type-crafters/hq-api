import os
import subprocess
import re
from typing import Literal
from .console import log, error, info

tab = " " * 4


def lambda_function(name: str) -> dict[Literal['name', 'content'], str | list[str]]:
    return {
        'name': 'function.py',
        'content': [
            "import json",
            "",
            f"# Lambda handler '{name}'",
            "def handler(event, context):",
            tab + "return {",
            tab * 2 + "'statusCode': 200,",
            tab * 2 + "'message': json.dumps('Hello from lambda!')",
            tab + "}",
        ],
    }

def requirements_txt() -> dict[Literal['name', 'content'], str | list[str]]:
    boto3_version = re.search(r"\(([^)]+)\)", subprocess.run(
            ['pip', 'index', 'versions', 'boto3'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.splitlines()[0]).group(1)
    boto3_minor = boto3_version.split('.')
    boto3_minor[2] = '0'
    botocore_version = re.search(r"\(([^)]+)\)", subprocess.run(
            ['pip', 'index', 'versions', 'botocore'],
            capture_output=True,
            text=True,
            check=True
        ).stdout.splitlines()[0]).group(1)
    botocore_minor = botocore_version.split('.')
    botocore_minor[2] = '0'

    return {
        'name': 'requirements.txt',
        'content': [
            f"boto3>={'.'.join(boto3_minor)}",
            f"botocore>={'.'.join(botocore_minor)}"
        ]
    }


def create_lambda(name: str) -> None:
    log(f"Creating lambda function '{name}'...")
    try:
        os.makedirs(os.path.abspath(name))
    except FileExistsError:
        error(f"Error: directory '{name}' already exists")
        return
    else:
        req = requirements_txt()
        with open(os.path.join(name, req['name']), 'w', encoding='utf-8') as file:
            file.write('\n'.join(req['content']))
        fn = lambda_function(name)
        with open(os.path.join(name, fn['name']), 'w', encoding='utf-8') as file:
            file.write('\n'.join(fn['content']))
        info(f"Lambda function '{name}' successfully created!")
