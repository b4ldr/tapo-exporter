from threading import Thread
from typing import Dict

from prometheus_client import Gauge

PLUG_GAUGE = Gauge(
    'tapo_plug_power', 'The power the plug', labelnames=['device_name']
)


class MetricsRender(Thread):
    def __init__(self, plugs: Dict) -> None:
        Thread.__init__(self)
        self.plugs = plugs

    def run(self) -> None:
        for device_name, plug in self.plugs.items():
            power = plug.getEnergyUsage()['result']['current_power']
            PLUG_GAUGE.labels(device_name=device_name).set(power)
