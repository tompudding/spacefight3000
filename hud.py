import ui
import drawing
from globals.types import Point

class Hud(object):
    def __init__(self, parent_ui_object):
        self.parent_ui_object = parent_ui_object
        self.weapon_power_bar = None
        self.setupWeaponPowerBar()
        
    
    def setupWeaponPowerBar(self):
        barColours = [drawing.constants.colours.red, drawing.constants.colours.yellow, drawing.constants.colours.light_green]
        barBorder = drawing.constants.colours.blue
        
        ui.PowerBar(self.parent_ui_object, Point(0,0), Point(10,10), 0, barColours, barBorder)