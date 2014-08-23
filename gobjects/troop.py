import gobject
import globals
from weapon import weapon

class Troop(gobject.BoxGobject):    
  
    def __init__(self, initialWeapon, physics, bl, tr):
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_name)
        super(Troop,self).__init__(physics,bl,tr,self.tc)
        self.currentWeapon = initialWeapon
        self.texture_name = 'bazookaTroop.png'

        
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon 
         
