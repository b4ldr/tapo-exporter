import logging
import time

from argparse import ArgumentParser
from pathlib import Path

import yaml

from prometheus_client import start_http_server
from PyP100 import PyP110

from tapo_exporter.metrics import MetricsRender


def get_args():
    """Parse arguments"""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--config-file', type=Path, required=True)
    parser.add_argument('-v', '--verbose', action='count')
    return parser.parse_args()


def get_log_level(args_level):
    """Configure logging"""
    return {
        None: logging.ERROR,
        1: logging.WARN,
        2: logging.INFO,
        3: logging.DEBUG}.get(args_level, logging.DEBUG)


def main() -> None:
    args = get_args()
    logging.basicConfig(level=get_log_level(args.verbose))
    start_http_server(8000)
    config = yaml.load(args.config_file.read_text())
    plugs = {}
    for plug in config['plugs']:
        try:
            plug = PyP110.P110(plug, config['email'], config['password'])
            plug.handshake()
            plug.login()
            plugs[plug.getDeviceName()] = plug
        except Exception as error:
            logging.error('failed to connet to %s: %s', plug, error)
    while True:
        metrics = MetricsRender(plugs=plugs)
        metrics.start()
        time.sleep(15)
        metrics.join()


if __name__ == '__main__':
    main()
