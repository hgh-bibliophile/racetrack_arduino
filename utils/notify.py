import asyncio
from datetime import datetime
import json


class Notify:
    def __init__(self, typer, websocket=None):
        self.typer = typer
        self.websocket = websocket

    async def log(self, type, msg, data=None):
        """Send to both stdout and websocket"""
        event = Event(type, msg, data)

        self.typer.echo(f'[{datetime.now().replace(microsecond=0)}] ({type}) {msg}')

        if self.websocket:
            await self.websocket.send(event.getJson())
        elif data:
            self.typer.echo(event.getJsonData())

class Event:
    def __init__(self, type, msg, data=''):
        self.setType(type)
        self.setMsg(msg)
        self.setData(data)

    def getType(self):
        return self.__type
    def setType(self, type):
        self.__type = type

    def getMsg(self):
        return self.__msg
    def setMsg(self, msg):
        self.__msg = msg

    def getData(self):
        return self.__data
    def setData(self, data):
        self.__data = data

    def get(self):
        return {
            'type': self.getType(),
            'msg': self.getMsg(),
            'data': self.getData()
        }

    def getJson(self):
        return json.dumps(self.get())

    def getJsonData(self):
        return json.dumps(self.getData(), indent=4)

    def __repr__(self):
        return str(self.get())

class JsonEvent(Event):

    type_error = 'type_error'
    data_error = 'data_error'
    types = ['start_race', 'type_error', 'data_error']

    def __init__(self, json_event):
        try:
            self.event = json.loads(json_event)
            type = self.event.get('type', JsonEvent.type_error)
            msg = self.event.get('msg', '')
            data = self.event.get('data', '')

            super().__init__(type, msg, data)

        except json.decoder.JSONDecodeError as e:
            type = JsonEvent.data_error
            msg = str(e)
            data = ''

        super().__init__(type, msg, data)

    def setType(self, type):
        if type not in JsonEvent.types:
            type = JsonEvent.type_error
            self.setMsg('Invalid or missing event type')
        super().setType(type)