import argparse
from scripts.create_lambda import create_lambda
from scripts.restore_all import restore_all
from scripts.test_all import test_all
from scripts.package import package

def main():
    parser = argparse.ArgumentParser(description='Basic AWS Lambda project utility scripts')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # python manage.py lambda <name>
    lambda_parser = subparsers.add_parser('new', help='Create a new lambda function with the provided name')
    lambda_parser.add_argument('name', type=str, help='Name for the lambda command')

    # python manage.py package <name>
    package_parser = subparsers.add_parser('package', help='Package the lambda function into a ready-to-use .zip file.')
    package_parser.add_argument('name', type=str, help="The name of the lambda function's directory")

    # python manage.py test
    test_parser = subparsers.add_parser('test', help='Run the test command')

    # python manage.py restore
    restore_parser = subparsers.add_parser('restore', help='Run the restore command')

    args = parser.parse_args()

    if args.command == 'lambda':
        create_lambda(args.name)
    elif args.command == 'test':
        test_all()
    elif args.command == 'restore':
        restore_all()
    elif args.command == 'package':
        package(args.name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()