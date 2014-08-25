import ui
import drawing
import globals
from globals.types import Point
import globals

class Hud(object):
    #screen root
    def __init__(self, parent_ui_object):
        self.parent_ui_object = parent_ui_object
        self.weapon_power_bar = None
        self.setupWeaponPowerBar()
        self.weaponSelectionBoxes = []
        #self.createWeaponSelectionBoxs(4)  #Bazooka, lazer, grenade, orbital satalite

        self.bottom_bar = ui.Box(parent = self.parent_ui_object,
                                 pos = Point(0,0),
                                 tr = Point(1,0.1),
                                 colour=(0,0,0,0.7))

        self.bottom_bar.help_button = ui.TextBoxButton(parent=self.bottom_bar,
                                                       pos=Point(0.9,0.2),
                                                       tr=Point(1.0,0.8),
                                                       text='HELP',
                                                       textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                                       colour=(1,1,1,1),
                                                       callback=self.show_help
                                                       size=8,
                                                       )
        #self.help_screen =

        self.level_bar = ui.TextBox(parent = self.parent_ui_object,
                                     bl     = Point(0.5,0),
                                     tr     = None,
                                     text   = "??" ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     colour = (1,1,1,1),
                                     scale  = 8)

    def show_help(self,pos):
        print 'help'

    def setupWeaponPowerBar(self):
        barColours = [drawing.constants.colours.light_green, drawing.constants.colours.yellow, drawing.constants.colours.red]
        barBorder = drawing.constants.colours.blue

        self.weapon_power_bar = ui.PowerBar(self.parent_ui_object, Point(0,0), Point(0.1,0.05), 0, barColours, barBorder)

    def SetLevelBar(self, text):
        self.level_bar.SetText(text);


    def setWeaponPowerBarValue(self, newValue):
        self.weapon_power_bar.SetBarLevel(newValue)


    def createWeaponSelectionBoxs(self, box_details):
        #this does not work if you have an odd number of weapons, probably ought to fix that.
        #takes a list of pairs with text and
        self.clearWeaponSelectionBoxs()

        num_boxes = len(box_details)

        box_size = Point(0.05, 0.05)
        maxX = 1
        maxY = 1

        num_rows = 2
        num_columns = num_boxes / num_rows

        current_row = 0
        current_column = 0
        next_box_top_right = Point(maxX, maxY)
        next_box_bottom_left = next_box_top_right - box_size

        box_no = 0
        while current_row < num_rows:
            while current_column < num_columns:
                current_detail = box_details[box_no]

                wpn_image = current_detail.image
                wpn_size = current_detail.image_size
                wpn_callback = current_detail.callback
                wpn_callback_args = current_detail.callback_args


                current_column += 1
                #def __init__(self,parent,pos,tr,texture_name,callback,args,buffer=None,level=None):
                self.weaponSelectionBoxes.append(ui.ImageBoxButton(self.parent_ui_object, next_box_bottom_left, next_box_top_right, wpn_image, wpn_callback, wpn_callback_args))

                next_box_top_right = next_box_top_right - Point(box_size[0], 0)
                next_box_bottom_left = next_box_bottom_left - Point(box_size[0], 0)
                box_no += 1

            next_box_top_right = Point(maxX, maxY - box_size[1])
            next_box_bottom_left =  next_box_top_right - box_size
            current_row += 1
            current_column = 0

    def clearWeaponSelectionBoxs(self):
        for existing_box in self.weaponSelectionBoxes:
            existing_box.Delete()

        self.weaponSelectionBoxes = []


    def science(self, stuff):
        print stuff
        print "you clicked a button!"



