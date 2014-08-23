import gobject
import globals
import weapon

class Troop(gobject.BoxGobject):    
  
    def __init__(self, initialWeapon, physics, bl, tr):
        self.texture_name = 'bazookaTroop.png'
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_filename)
        super(Troop,self).__init__(physics,bl,tr,self.tc)
        self.currentWeapon = initialWeapon
    
        self.body.SetMassFromShapes()
        if not self.static:
            physics.AddObject(self)
        
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon 
         
