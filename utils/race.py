from .arduino import Arduino, ArduinoException
from .notify import Notify

class Race:
    def __init__(self, arduino: Arduino, lane_data: str, notify: Notify=None):
        self.arduino = arduino
        self.lane_data = lane_data
        self.notify = notify

    async def go(self, websocket=None):
        """Notifies directly via `self.websocket` and/or `self.typer`"""

        try:
            self.arduino.connect()  # Connect to arduino
            self.arduino.start_race()  # Send START RACE command & check for ACK

            await self.notify.log('arduino_ready', 'Listening for USB COM Arduino data')

            heat = self.arduino.get_race()
            heat_data = heat.get_results(self.lane_data)

            await self.notify.log('heat_data', 'Arduino data received', heat_data)

        except ArduinoException as msg:
            await self.notify.log('error', str(msg))

