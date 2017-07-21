import logging
import argparse

from orgmaild.server import OrgmailForwarder


parser = argparse.ArgumentParser()


def main():
    parser.parse_args()  # Handle --help
    server = OrgmailForwarder('0.0.0.0', 9002)
    server.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main()
