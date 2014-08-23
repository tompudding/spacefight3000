import gobject
import globals
import weapon
import drawing
from globals.types import Point

class Troop(gobject.BoxGobject):    
  
    def __init__(self, initialWeapon, physics, bl, tr):
        self.texture_filename = 'bazookaTroop.png'
        self.selectedBoxFilename = 'selectionBox.png'
        self.selected = False
        self.selectionBoxQuad = None
        self.selectedBoxtc = globals.atlas.TextureSpriteCoords(self.selectedBoxFilename)
        
        
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_filename)
        super(Troop,self).__init__(physics,bl,tr,self.tc)
        self.currentWeapon = initialWeapon(physics, bl, tr)
    
        self.body.SetMassFromShapes()
        if not self.static:
            physics.AddObject(self)
            
        self.selectionBoxQuad.Disable()
            

        
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon 
        
    def select(self):
        self.selected = True
        self.selectionBoxQuad.Enable()
    
    def unselect(self):
        self.selected = False
        self.selectionBoxQuad.Disable()
         

    def InitPolygons(self,tc):
        super(Troop,self).InitPolygons(self.tc)
        
        if self.dead:        #drawing.Translate(-self.viewpos.pos.x/2,-self.viewpos.pos.y/2,0)
            return
        self.selectionBoxQuad = drawing.Quad(globals.quad_buffer, tc = self.selectedBoxtc)
     
     
    def PhysUpdate(self,gravity_sources):
        super(Troop,self).PhysUpdate(gravity_sources)
        if self.dead or self.static:
            return
        #Just set the vertices
        vertices = []
        for i,vertex in enumerate(self.shape.vertices):
            screen_coords = Point(*self.body.GetWorldPoint(vertex))/self.physics.scale_factor
            vertices.append( screen_coords )
            
        self.selectionBoxQuad.SetAllVertices(vertices, self.z_level+0.1)
 
        self.doGravity(gravity_sources)
