import logging
import argparse

from orgmaild.server import OrgmailForwarder


parser = argparse.ArgumentParser()
parser.add_argument('receiver_host', default='127.0.0.1')
parser.add_argument('receiver_port', default=9002, type=int)


def main():
    server = OrgmailForwarder(**vars(parser.parse_args()))
    server.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main()
