import asyncio
import logging

from argparse import ArgumentParser
from pathlib import Path

import yaml

from aioprometheus import Gauge
from aioprometheus.service import Service
from kasa import Discover, Credentials


logger = logging.getLogger(__name__)


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


async def main() -> None:
    await svr.start(port=8000)
    args = get_args()
    logging.basicConfig(level=get_log_level(args.verbose))
    plug_gauge = Gauge('tapo_plug_power', 'The power the plug')

    config = yaml.load(args.config_file.read_text())
    plugs = []
    credentials = Credentials(username=config['email'], password=config['password'])
    for plug in config['plugs']:
        try:
            plug = await Discover.discover_single(plug, credentials=credentials)
            await plug.update()
            plugs.append(plug)
        except Exception as error:
            logging.error('failed to connet to %s: %s', plug, error)
    try:
        while True:
            if len(plugs) == 0:
                logging.error("No more devices")

            for plug in plugs:
                await plug.update()
                plug_gauge.set(
                    {'device_name': plug.alias},
                    plug.internal_state['energy']['current_power'],
                )

            await asyncio.sleep(15)
    except Exception as Error:
        raise
    finally:
        for plug in plugs:
            plug.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    svr = Service()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(svr.stop())
    loop.stop()
    loop.close()
