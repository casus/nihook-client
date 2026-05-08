import argparse
from . import __version__

def main():
    parser = argparse.ArgumentParser(description="Nihook Client CLI")
    parser.add_argument("-v", "--version", action="version", version=f"nihook-client {__version__}")
    
    # You can add more subcommands here later, e.g. for table_from_schema
    # subparsers = parser.add_subparsers(dest="command")
    
    args = parser.parse_args()

if __name__ == "__main__":
    main()
