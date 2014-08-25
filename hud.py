import ui
import drawing
from globals.types import Point
import globals

class Hud(object):
    #screen root
    def __init__(self, parent_ui_object):
        self.parent_ui_object = parent_ui_object
        self.weapon_power_bar = None
        self.setupWeaponPowerBar()

        self.level_bar = ui.TextBox(parent = self.parent_ui_object,
                                     bl     = Point(0.5,0),
                                     tr     = None,
                                     text   = "??" ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     colour = (1,1,1,1),
                                     scale  = 8)

        self.blob = ui.ImageBox(parent = globals.screen_root,
                                pos = Point(0.2,0.2),
                                tr = Point(0.8,0.8),
                                texture_name = 'gate0.png',
                                level = 8)



    def setupWeaponPowerBar(self):
        barColours = [drawing.constants.colours.light_green, drawing.constants.colours.yellow, drawing.constants.colours.red]
        barBorder = drawing.constants.colours.blue

        self.weapon_power_bar = ui.PowerBar(self.parent_ui_object, Point(0,0), Point(0.1,0.05), 0, barColours, barBorder)

    def SetLevelBar(self, text):
        self.level_bar.SetText(text);


    def setWeaponPowerBarValue(self, newValue):
        self.weapon_power_bar.SetBarLevel(newValue)
