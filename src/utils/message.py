import discord

async def send (
    tag="info", location=None, channel=None, msg_type="plain",
    delete_after=None, content=None
):
    _response = None

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
