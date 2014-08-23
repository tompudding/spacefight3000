import gobject
import globals
import weapon
import drawing
from globals.types import Point

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
        self.selectionBoxQuad = None
        
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon 
        
    def select(self):
        self.selected = True
         

    def InitPolygons(self,tc):
        super(Troop,self).InitPolygons(tc)
        
        if self.dead:
            return
        self.selectionBoxQuad = drawing.Quad(globals.quad_buffer,tc = tc)
     
     
    def PhysUpdate(self,gravity_sources):
        super(Troop,self).PhysUpdate(gravity_sources)
        if self.dead or self.static:
            return
        #Just set the vertices
 
        for i,vertex in enumerate(self.shape.vertices):
            screen_coords = Point(*self.body.GetWorldPoint(vertex))/self.physics.scale_factor
            self.selectionBoxQuad.vertex[self.vertex_permutation[i]] = (screen_coords.x,screen_coords.y,self.z_level)
 
        self.doGravity(gravity_sources)
