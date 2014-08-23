import gobject
import globals
import weapon
from globals.types import Point
import math

class Troop(gobject.BoxGobject):    
  
    def __init__(self, initialWeapon, physics, bl):
        tr = bl + Point(50,50)
        self.texture_filename = 'bazookaTroop.png'
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_filename)
        super(Troop,self).__init__(physics,bl,tr,self.tc)
        self.currentWeapon = initialWeapon(physics, bl, tr)
    
        self.body.SetMassFromShapes()
        if not self.static:
            physics.AddObject(self)
        
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon

    def PhysUpdate(self,gravity_sources):
        super(Troop,self).PhysUpdate(gravity_sources)

        if hasattr(globals.current_view.mode, "planets"):
            for planet in globals.current_view.mode.planets:
                diff_vector = planet.body.position - self.body.position
                if diff_vector.Length() <  12:
                    self.body.angle = math.tan(float(diff_vector.x) / -diff_vector.y) + math.pi

