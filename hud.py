import ui
import drawing
import globals
from globals.types import Point
import globals

class HelpScreen(ui.UIElement):
    help_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
    def __init__(self,parent,pos,tr):
        super(HelpScreen,self).__init__(parent,pos,tr)
        self.backdrop = ui.Box(parent = self,
                               pos = Point(0,0),
                               tr = Point(1,1),
                               colour=(0,0,0,0.85))
        self.ok = ui.TextBoxButton(parent=self,
                                   pos=Point(0.45,0.05),
                                   tr=Point(0.55,0.1),
                                   text='OK',
                                   textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                   colour=(1,1,1,1),
                                   callback=self.dismiss,
                                   size=8,
                                   )
        self.title = ui.TextBox(parent = self,
                                bl     = Point(0,0.8),
                                tr     = Point(1,0.95),
                                text   = "Instructions" ,
                                textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                colour = (1,1,1,1),
                                alignment = drawing.texture.TextAlignments.CENTRE,
                                scale  = 8)
        self.blurb = ui.TextBox(parent = self,
                                bl     = Point(0.1,0.1),
                                tr     = Point(0.8,0.9),
                                text   = self.help_text ,
                                textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                colour = (1,1,1,1),
                                alignment = drawing.texture.TextAlignments.LEFT,
                                scale  = 8)
        print self.ok

    def dismiss(self,pos):
        self.Disable()


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
                                                       callback=self.show_help,
                                                       size=8,
                                                       )

        self.help_screen = HelpScreen(parent = self.parent_ui_object,
                                      pos = Point(0.1,0.2),
                                      tr = Point(0.9,0.9))
        self.help_screen.Disable()

        self.level_bar = ui.TextBox(parent = self.parent_ui_object,
                                     bl     = Point(0.25,0),
                                     tr     = None,
                                     text   = "??" ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     colour = (1,1,1,1),
                                     scale  = 8)

    def show_help(self,pos):
        self.help_screen.Enable()

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

        num_rows = 2 #have 4 boxes, for bazooka, grenade, lazer, satalite
        num_columns = 2

        current_row = 0
        current_column = 0
        next_box_top_right = Point(maxX, maxY)
        next_box_bottom_left = next_box_top_right - box_size

        box_no = 0
        while current_row < num_rows:
            while current_column < num_columns:

                if box_no < num_boxes:
                    current_detail = box_details[box_no]
                    self.addWeaponSelectionButton(current_detail, next_box_bottom_left, next_box_top_right)
                else:
                    self.addEmptySelectionButton(next_box_bottom_left, next_box_top_right)


                current_column += 1
                next_box_top_right = next_box_top_right - Point(box_size[0], 0)
                next_box_bottom_left = next_box_bottom_left - Point(box_size[0], 0)
                box_no += 1

            next_box_top_right = Point(maxX, maxY - box_size[1])
            next_box_bottom_left =  next_box_top_right - box_size
            current_row += 1
            current_column = 0

    def addWeaponSelectionButton(self, current_detail, bottom_left, top_right):
        wpn_image = current_detail.image
        wpn_size = current_detail.image_size
        wpn_callback = current_detail.callback
        wpn_callback_args = current_detail.callback_args
        wpn_has_ammo = current_detail.limited_ammo

        if wpn_has_ammo:
            wpn_ammo_amount = str(current_detail.current_ammo)
        else:
            wpn_ammo_amount = "*"



        imageBtn = ui.ImageBoxButton(self.parent_ui_object, bottom_left, top_right, wpn_image, wpn_callback, wpn_callback_args)
        btnSize = imageBtn.absolute.size
        imageBtn.ResizeImage(Point(wpn_size[0] / btnSize[0], wpn_size[1] / btnSize[1]))

        ammoLbl = ui.TextBox(imageBtn, Point(0.85, 1), Point(1, 0.85), wpn_ammo_amount, 4, drawing.constants.colours.red)#, textType, alignment, level)

        self.weaponSelectionBoxes.append(imageBtn)
        self.weaponSelectionBoxes.append(ammoLbl)

    def addEmptySelectionButton(self, bottom_left, top_right):
        lightGrey = 1,1,1,0.5
        self.weaponSelectionBoxes.append(ui.Border(self.parent_ui_object, bottom_left, top_right, lightGrey, buffer=globals.ui_buffer))

    def clearWeaponSelectionBoxs(self):
        for existing_box in self.weaponSelectionBoxes:
            existing_box.Delete()

        self.weaponSelectionBoxes = []



