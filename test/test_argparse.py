from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('command', choices=['start'], nargs='?', help='Command')
args = parser.parse_args()

print(args)
