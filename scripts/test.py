import os
import subprocess
from .lib import LAMBDA_PATH
from .lib import log, error, info

def test(dirpath: str) -> None:
    dirname = os.path.basename(dirpath)
    log(f"Running tests for lambda function '{dirname}'...")
    
    try:
        result = subprocess.run(
            ['pytest', '-v'],
            cwd=dirpath,
            capture_output=True,
            text=True,
            check=True,
        )
        info(f"Results for lambda function '{dirname}':")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        error(f"Tests failed for lambda function '{dirname}':")
        print(e.stdout)
        if e.stderr:
            print('Errors during pytest execution:')
            print(e.stderr)

