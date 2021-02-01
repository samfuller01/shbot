import discord
from datetime import datetime

from definitions import *

COLORS = {
    "info": "\033[38;5;255m\033[48;5;24m",
    "debug": "\033[38;5;255m\033[48;5;98m",
    "warning": "\033[1m\033[38;5;255m\033[48;5;130m",
    "success": "\033[38;5;255m\033[48;5;70m",
    "error": "\033[1m\033[38;5;255m\033[48;5;124m",
    "content": "\033[38;5;255m\033[48;5;236m",
    "default": "\033[0m"
}

async def send (
    tag="info", location=None, channel=None, msg_type="plain",
    delete_after=None, content=None
):
    if location == None:
        print("{date} {coltag} {thetag} {coldef} {coltent} {content} {coldef}".format(
                date=datetime.utcnow().strftime('%I:%M:%S %p - %f').ljust(19),
                coltag=COLORS[tag], thetag=tag.upper().ljust(7), coldef=COLORS["default"],
                coltent=COLORS["content"], content=content))
    else:
        print("{date} {coltag} {thetag} {coldef} {coltent} {content} {coldef} ({file})".format(
                date=datetime.utcnow().strftime('%I:%M:%S %p - %f').ljust(19),
                coltag=COLORS[tag], thetag=tag.upper().ljust(7), coldef=COLORS["default"],
                coltent=COLORS["content"], content=content, file=os.path.relpath(location, PROJECT_ROOT)))

    _response = None
    if (channel != None):
        if (msg_type == "plain"):
            if (delete_after != None):
                _response = await channel.send(content=content, delete_after=delete_after)
            else:
                _response = await channel.send(content=content)
        elif (msg_type == "embed"):
            if (delete_after != None):
                _response = await channel.send(embed=content, delete_after=delete_after)
            else:
                _response = await channel.send(embed=content)
        return _response

