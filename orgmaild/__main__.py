import logging
import argparse

from orgmaild.server import OrgmailForwarder


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true',
                    help='Enable debug logging')


def configure_logging(debug):
    from emailtunnel import logger
    root = logging.getLogger()

    file_handler = logging.FileHandler('orgmaild.log', 'a')
    fmt = '[%(asctime)s %(levelname)s] %(message)s'
    datefmt = None
    file_formatter = logging.Formatter(fmt, datefmt, '%')
    file_handler.setFormatter(file_formatter)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        stream_formatter = logging.Formatter('%(message)s', None, '%')
        stream_handler = logging.StreamHandler(None)
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def main():
    args = parser.parse_args()
    configure_logging(args.debug)
    server = OrgmailForwarder('0.0.0.0', 9002)
    server.run()


if __name__ == '__main__':
    main()
