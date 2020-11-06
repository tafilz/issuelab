import argparse

from .cli import init_command, cleanup_command, push_command, pull_command
from .cli.init import SupportedTracker

parser = argparse.ArgumentParser(prog='issuelab')
subparsers = parser.add_subparsers(title='subcommands',
                                   description='valid subcommands')

# init
parser_init = subparsers.add_parser('init', help='init project')
parser_init.add_argument(
    'name', type=str, help='Name', default='issuelab_project')
parser_init.add_argument(
    '--source', type=SupportedTracker, choices=list(SupportedTracker), help='Source tracker', required=True)
parser_init.add_argument(
    '--target', type=SupportedTracker, choices=list(SupportedTracker), help='Target tracker', required=True)
parser_init.set_defaults(func=init_command)

# pull
parser_pull = subparsers.add_parser('pull', help='Pull from source')
parser_pull.set_defaults(func=pull_command)

# push
parser_migrate = subparsers.add_parser('push', help='Pull from source')
parser_migrate.set_defaults(func=push_command)

# cleanup
parser_cleanup = subparsers.add_parser('cleanup', help='Pull from source')
parser_cleanup.set_defaults(func=cleanup_command)


args = parser.parse_args()
args.func(args)
