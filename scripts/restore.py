import os
import subprocess
import venv
from .lib import LAMBDA_PATH, log, info, try_create_venv, warn


def restore(dirpath: str) -> None:
    dirname = os.path.basename(dirpath)
    venv_path, rel_venv_path = try_create_venv(at=dirpath)

    log(f"Restoring packages for lambda function '{dirname}' (using virtual environment {rel_venv_path})...")

    pip = os.path.join(venv_path, 'Scripts' if os.name == 'nt' else 'bin', 'pip')
    requirements_txt = os.path.join(dirpath, 'requirements.txt')
    
    if os.path.exists(requirements_txt):
        subprocess.run([pip, 'install', '-r', requirements_txt], capture_output=True, text=True)
        info(f"Packages for '{dirname}' successfully installed!")
    else:
        warn(f"No requirements.txt found for '{dirname}'.")
