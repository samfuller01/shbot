import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

ASSET_PATH   = PROJECT_ROOT + "/assets"
PRESET_PATH  = PROJECT_ROOT + "/presets"
SRC_PATH     = PROJECT_ROOT + "/src"

COMP_PATH    = SRC_PATH + "/game/components"

DEFAULT_PRESETS = {
    5: PRESET_PATH + "/classic/stock/5p.json",
    6: PRESET_PATH + "/classic/stock/5p.json",
    7: PRESET_PATH + "/classic/stock/7p.json",
    8: PRESET_PATH + "/classic/stock/7p.json",
    9: PRESET_PATH + "/classic/stock/9p.json",
    10: PRESET_PATH + "/classic/stock/9p.json"
}
