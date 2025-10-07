import argparse
import os
from scripts.lib import LAMBDA_PATH, apply_to_all, error
from scripts.new import new
from scripts.restore import restore
from scripts.test import test
from scripts.package import package

def main():
    parser = argparse.ArgumentParser(description='Basic AWS Lambda project utility scripts')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # python manage.py new <name>
    lambda_parser = subparsers.add_parser('new', help='Create a new lambda function with the provided name')
    lambda_parser.add_argument('name', type=str, help='Name for the lambda command')

    # python manage.py package <name> 
    package_parser = subparsers.add_parser('package', help='Package the lambda function into a ready-to-use .zip file.')
    package_parser.add_argument('name', type=str, nargs='?', help="The name of the lambda function's directory")
    package_parser.add_argument('--all', action='store_true', help="Package all functions in lambda/")


    # python manage.py test <name> <flags>
    test_parser = subparsers.add_parser('test', help='Run the test command')
    test_parser.add_argument('name', type=str, nargs='?', help="The name of the lambda function's directory")
    test_parser.add_argument('--all', action='store_true', help="Test all functions in lambda/")

    # python manage.py restore <name> <flags>
    restore_parser = subparsers.add_parser('restore', help='Run the restore command')
    restore_parser.add_argument('name', type=str, nargs='?', help="The name of the lambda function's directory")
    restore_parser.add_argument('--all', action='store_true', help="Restore all functions in lambda/")


    args = parser.parse_args()

    if args.command == 'new':
        new(os.path.abspath(os.path.join(LAMBDA_PATH, args.name)))
    elif args.command == 'test':
        if args.all:
            apply_to_all(test)
        elif args.name: 
            test(os.path.abspath(os.path.join(LAMBDA_PATH, args.name)))
        else:
            error('Please provide either the dir name or the --all flag.')
            return
    elif args.command == 'restore':
        if args.all:
            apply_to_all(restore)
        elif args.name: 
            restore(os.path.abspath(os.path.join(LAMBDA_PATH, args.name)))
        else:
            error('Please provide either the dir name or the --all flag.')
            return
    elif args.command == 'package':
        if args.all:
            apply_to_all(package)
        elif args.name: 
            package(os.path.abspath(os.path.join(LAMBDA_PATH, args.name)))
        else:
            error('Please provide either the dir name or the --all flag.')
            return
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
