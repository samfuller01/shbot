import importlib
import os
import re

from definitions import *
import src.utils.message as msg

def CreateComponentFromQualified(parent = None, context = None, slot = None, name = "default"):
    #
    realpath = "{root}/{s}/{p}.py".format(root=COMP_PATH, s=slot, p=name)

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
    _module_name = "src.game.components.{s}.{n}".format(s=slot, n= name)
    _module      = importlib.import_module(_module_name)
    _class       = getattr(_module, "SHGameComponent{s}{p}".format(s=slot.upper(), p=name.upper()))

    #
    #   Create an instance.
    #
    _instance = _class(parent=parent, client=client)
    return _instance

