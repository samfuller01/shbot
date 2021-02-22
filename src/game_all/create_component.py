import importlib
import os
import re

from definitions import *
import src.utils.message as msg

def CreateComponentFromQualified(parent = None, context = None, game = None, slot = None, name = "default"):
    #
    realpath = "{root}/{g}/components/{s}/{p}.py".format(root=SRC_PATH, g=game, s=slot, p=name)
    print(realpath)
    #
    #   We need to see if the path actually exists.
    #
    if (os.path.isfile(realpath) == False):
        parent.client.loop.create_task(
            msg.send(tag="warning", location=__file__, channel=context.channel, msg_type="plain", delete_after=None,
                       content="Not using component '{s}.{c}' - doesn't exist!".format(s=slot, c=name)))
        name = "default"

    #
    #   Get our dot-representation of the component's module.
    #
    _module_name = "src.{g}.components.{s}.{n}".format(g=game, s=slot, n= name)
    _module      = importlib.import_module(_module_name)

    _modified_game_name = game if game == "SH" else game.capitalize()
    _class       = getattr(_module, "{g}GameComponent{s}{p}".format(g=_modified_game_name, s=slot.capitalize(), p=name.capitalize()))

    #
    #   Create an instance.
    #
    _instance = _class(parent=parent, client=parent.client)
    return _instance

