from src.bot import SHBot

import json

f = open('config.json')
_config = json.load(f)

_inst = SHBot(_config)
_inst.Setup()
_inst.Start()
_inst.Shutdown()
