import os
import subprocess
import venv
from .lib import LAMBDA_PATH, log, info, warn


def restore_all():
    for dir in [entry.name for entry in os.scandir(LAMBDA_PATH) if entry.is_dir()]:

        dir_path = os.path.abspath(os.path.join(LAMBDA_PATH, dir))

        is_lambda = 'function.py' in [
            entry.name for entry in os.scandir(dir_path) if entry.is_file()
        ]

        if not is_lambda:
            continue


        venv_path = os.path.join(dir_path, '.venv')
        rel_venv_path = os.path.relpath(venv_path, LAMBDA_PATH).replace('\\', '/')
        if not os.path.exists(venv_path):
            log(f"Creating virtual environment at {rel_venv_path}...")
            venv.create(venv_path, with_pip=True)
            log(f"Created virtual environment at {rel_venv_path}")

        log(f"Restoring packages for lambda function '{dir}' (using virtual environment {rel_venv_path})...")
        
        pip = os.path.join(venv_path, 'Scripts' if os.name == 'nt' else 'bin', 'pip')
        requirements_txt = os.path.join(dir_path, 'requirements.txt')
        
        if os.path.exists(requirements_txt):
            subprocess.run([pip, 'install', '-r', requirements_txt], capture_output=True, text=True)
            info(f"Packages for '{dir}' successfully installed!")
        else:
            warn(f"No requirements.txt found for '{dir}'.")
