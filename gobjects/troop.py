import gobject
import globals
import weapon

class Troop(gobject.BoxGobject):    
  
    def __init__(self, initialWeapon, physics, bl, tr):
        self.texture_filename = 'bazookaTroop.png'
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_filename)
        super(Troop,self).__init__(physics,bl,tr,self.tc)
        self.currentWeapon = initialWeapon(physics, bl, tr)
    
        self.body.SetMassFromShapes()
        if not self.static:
            physics.AddObject(self)
            
        self.selected = False
        
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon 
        
    def select(self):
        self.selected = True
         
