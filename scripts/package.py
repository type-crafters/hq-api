import os
import sys
import subprocess
import tempfile
import zipfile
from .lib import LAMBDA_PATH, DIST_PATH, log, info, error


def package(name):
    log(f"Packaging lambda function '{name}' into a .zip file...")
    dir_path = os.path.abspath(os.path.join(LAMBDA_PATH, name))
    os.makedirs(DIST_PATH, exist_ok=True)

    fn_path = os.path.join(dir_path, 'function.py')
    req_path = os.path.join(dir_path, 'requirements.txt')

    if not os.path.exists(fn_path):
        error(f"Error: Provided path {dir_path} does not contain a 'function.py' file.")
        return

    with tempfile.TemporaryDirectory() as build_dir:
        build_path = os.path.abspath(build_dir)

        if os.path.exists(req_path):
            log('Installing packages...')
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    req_path,
                    "-t",
                    build_path,
                ],
                capture_output=True,
                text=True,
            )
            log('Packages installed!')
            
        log('Copying files...')
        with open(fn_path, 'rb') as source, open(
            os.path.join(build_path, 'function.py'), 'wb'
        ) as dest:
            dest.write(source.read())

        zip_path = os.path.join(DIST_PATH, f"{name}.zip")

        with zipfile.ZipFile(os.path.join(zip_path), 'w', zipfile.ZIP_DEFLATED) as zip:
            for root, _, files in os.walk(build_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, build_path)
                    zip.write(file_path, arcname)
        log('Files copied!') 
        info(f"Lambda function '{name}' successfully packed into {os.path.relpath(zip_path, os.path.dirname(DIST_PATH)).replace("\\", "/")}!")
