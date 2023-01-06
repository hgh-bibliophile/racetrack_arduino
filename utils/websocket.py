import asyncio
import websockets
import time
import json
from .race import Race
from .notify import Notify, JsonEvent, Event

class RaceWebsocket:

    def __init__(self, arduino, typer):
        self.arduino = arduino
        self.typer = typer

    def serve(self, host='localhost', port=8765):
        self.host = host
        self.port = port

        asyncio.run(self.async_serve())

    async def async_serve(self):
        async with websockets.serve(self.recieve, self.host, self.port):
            self.typer.echo(f'Running @ ws://{self.host}:{self.port}')
            await asyncio.Future()  # run forever

    async def recieve(self, websocket):
        try:
            notify = Notify(self.typer, websocket)

            async for msg in websocket:
                event = JsonEvent(msg)
                if event.getType() == 'start_race':
                    await self.run_race(event, notify)  # race.go() logs data
                else:
                    await notify.log('error', event.getData())
        except websockets.exceptions.WebSocketException as e:
            print(e)

    async def run_race(self, event: JsonEvent, notify: Notify):
        lanes = event.getData()
        race = Race(self.arduino, lanes, notify)

        await race.go()

