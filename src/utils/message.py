import discord

def send (
    tag="info", location=None, channel=None, msg_type="plain",
    delete_after=None, content=None
):
    if (msg_type == "plain"):
        if (delete_after != None):
            channel.send(content=content, delete_after=delete_after)
        else:
            channel.send(content=content)
    elif (msg_type == "embed"):
        if (delete_after != None):
            channel.send(embed=content, delete_after=delete_after)
        else:
            channel.send(embed=content)
