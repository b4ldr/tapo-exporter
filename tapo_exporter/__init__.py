import asyncio
import logging
import time

from argparse import ArgumentParser
from pathlib import Path

import yaml

from prometheus_client import Gauge, start_http_server
from kasa import Discover, Credentials


PLUG_GAUGE = Gauge(
    'tapo_plug_power', 'The power the plug', labelnames=['device_name']
)


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
        3: logging.DEBUG,
    }.get(args_level, logging.DEBUG)


async def get_metricts(plug) -> None:
    await plug.update()
    power = plug.internal_state['energy']['current_power']
    PLUG_GAUGE.labels(device_name=device_name).set(power)


async def main() -> None:
    args = get_args()
    logging.basicConfig(level=get_log_level(args.verbose))
    config = yaml.load(args.config_file.read_text())
    port = config.get('port', 8000)
    addr = config.get('listen', '')
    start_http_server(port, addr)
    plugs = {}
    credentials = Credentials(username=config['email'], password=config['password'])
    for plug in config['plugs']:
        try:
            plug = await Discover.discover_single(plug, credentials)
            await plug.update()
            plugs[plug.alias] = plug
        except Exception as error:
            logging.error('failed to connet to %s: %s', plug, error)
    while True:
        for device_name, plug in plugs.items():
            await get_metricts(plug)
        time.sleep(15)


if __name__ == '__main__':
    asyncio.run(main())
