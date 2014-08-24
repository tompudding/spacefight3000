import ui
import drawing
from globals.types import Point

class Hud(object):
    #screen root
    def __init__(self, parent_ui_object):
        self.parent_ui_object = parent_ui_object
        self.weapon_power_bar = None
        self.setupWeaponPowerBar()
        
    
    def setupWeaponPowerBar(self):
        barColours = [drawing.constants.colours.light_green, drawing.constants.colours.yellow, drawing.constants.colours.red]
        barBorder = drawing.constants.colours.blue
        
        self.weapon_power_bar = ui.PowerBar(self.parent_ui_object, Point(0,0), Point(0.1,0.05), 0, barColours, barBorder)
        
    def setWeaponPowerBarValue(self, newValue):
        self.weapon_power_bar.SetBarLevel(newValue)