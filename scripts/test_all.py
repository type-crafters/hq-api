import os
import subprocess
from .lib import LAMBDA_PATH
from .lib import log, error, info

def test_all() -> None:
    for dir in [entry.name for entry in os.scandir(LAMBDA_PATH) if entry.is_dir()]:
        dir_path = os.path.abspath(os.path.join(LAMBDA_PATH, dir))

        is_lambda = "function.py" in [
            entry.name for entry in os.scandir(dir_path) if entry.is_file()
        ]

        if not is_lambda:
            continue

        log(f"Running tests for lambda function '{dir}'...")
        
        try:
            result = subprocess.run(
                ['pytest', '-v'],
                cwd=dir_path,
                capture_output=True,
                text=True,
                check=True,
            )
            info(f"Results for lambda function '{dir}':")
            print(result.stdout)

        except subprocess.CalledProcessError as e:
            error(f"Tests failed for lambda function '{dir}':")
            print(e.stdout)
            if e.stderr:
                print('Errors during pytest execution:')
                print(e.stderr)
