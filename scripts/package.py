import os
import sys
import subprocess
import tempfile
import zipfile
from .lib import LAMBDA_FILENAME, LAMBDA_PATH, DIST_PATH, VENV_NAME, log, info, error

def package(dirpath: str) -> None:
    dirname = os.path.basename(dirpath)
    log(f"Packaging lambda function '{dirname}' into a .zip file...")
    os.makedirs(DIST_PATH, exist_ok=True)

    fn_path = os.path.join(dirpath, LAMBDA_FILENAME)
    req_path = os.path.join(dirpath, 'requirements.txt')

    if not os.path.exists(fn_path):
        error(f"Error: Provided path {dirpath} does not contain a '{LAMBDA_FILENAME}' file.")
        return

    with tempfile.TemporaryDirectory() as build_dir:
        build_path = os.path.abspath(build_dir)

        if os.path.exists(req_path):
            log('Installing packages...')
            subprocess.run(
                [
                    sys.executable,
                    '-m',
                    'pip',
                    'install',
                    '-r',
                    req_path,
                    '-t',
                    build_path,
                ],
                capture_output=True,
                text=True,
            )
            log('Packages installed!')

        log('Copying files...')
        for root, dirs, files in os.walk(dirpath):
            dirs[:] = [d for d in dirs if d not in {VENV_NAME, '__pycache__'}]

            for file in files:
                if not file == 'requirements.txt':
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, dirpath)
                    dest_file = os.path.join(build_path, rel_path)

                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    with open(src_file, 'rb') as src, open(dest_file, 'wb') as dest:
                        dest.write(src.read())

        zip_path = os.path.join(DIST_PATH, f"{dirname}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(build_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, build_path)
                    zipf.write(file_path, arcname)

        log('Files copied!')
        info(
            f"Lambda function '{dirname}' successfully packed into "
            f"{os.path.relpath(zip_path, os.path.dirname(DIST_PATH)).replace('\\', '/')}!"
        )
