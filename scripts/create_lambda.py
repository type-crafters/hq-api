import os
import subprocess
import re
from typing import TypedDict
from .console import log, error, info

tab = " " * 4

class FileTemplate(TypedDict):
    name: str
    content: list[str]

def minor_version(package: str) -> tuple[str, str, str]:
    output = subprocess.run(
        ['pip', 'index', 'versions', package],
        capture_output=True,
        text=True,
        check=True
    )

    if output.stderr:
        raise ValueError(f"An error occured trying to get the version list for package '{package}'.")
    
    stdout = output.stdout

    version = re.search(r"\(([^)]+)\)", stdout.splitlines()[0])

    if not version:
        raise ValueError(f"No correctly formatted version for package '{package}' was found.")
    
    semver = version.group(1).split('.')
    major, minor, _ = semver

    return (major, minor, '0')

def lambda_function(name: str) -> FileTemplate:
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

def requirements_txt() -> FileTemplate:
    boto3_minor = '.'.join(minor_version('boto3'))
    botocore_minor = '.'.join(minor_version('botocore'))
    pytest_minor = '.'.join(minor_version('pytest'))

    return {
        'name': 'requirements.txt',
        'content': [
            f"boto3>={boto3_minor}",
            f"botocore>={'.'.join(botocore_minor)}",
            f"pytest>={'.'.join(pytest_minor)}"
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
