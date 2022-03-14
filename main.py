import typer, time, json, asyncio
from pathlib import Path

from utils.websocket import RaceWebsocket
from utils.arduino import Arduino, PortException, select_port
from utils.race import Race
from utils.notify import Notify

app = typer.Typer()


@app.command()
def web(port: int = typer.Option(8765, "--port", "-p"), host: str = typer.Option('localhost', "--host", "-h")):
    try:
        arduino = Arduino(select_port("Select Arduino COM Port"))
        RaceWebsocket(arduino, typer).serve(host, port)

    except PortException as msg:
        typer.echo(msg)


@app.command()
def usb(lanes_file: Path):
    try:
        arduino = Arduino(select_port("Select Arduino COM Port"))
        lanes = json.loads(lanes_file.read_text())
        logger = Notify(typer)

        race = Race(arduino, lanes, logger)
        asyncio.run(race.go())

    except PortException as msg:
        typer.echo(msg)


if __name__ == "__main__":
    app()







