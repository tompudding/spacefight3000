import gobject
import globals
import weapon
import math
from globals.types import Point
import math
import drawing

class Troop(gobject.BoxGobject):    
  
    def __init__(self, initialWeapon, physics, bl):
        tr = bl + Point(50,50)
        self.texture_filename = 'bazookaTroop.png'
        self.selectedBoxFilename = 'selectionBox.png'
        self.selected = False
        self.selectionBoxQuad = None
        self.selectedBoxtc = globals.atlas.TextureSpriteCoords(self.selectedBoxFilename)
        self.currentWeaponAngle = 0
        self.currentWeaponPower = 0
        
        self.maxWeaponPower = 100
        self.maxWeaponAngle = (2 * math.pi)
        self.minWeaponAngle = 0
        
        
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
    
    def fireWeapon(self):
        self.currentWeapon.FireAtTarget(self.currentWeaponPower, self.currentWeaponAngle)
        
    def increaseWeaponPower(self):
        self.currentWeaponPower += 1
        if(self.currentWeaponPower > self.maxWeaponPower):
            self.currentWeaponPower = 0
    
    def decreaseWeaponPower(self):
        self.currentWeaponPower -= 1
        if(self.currentWeaponPower > self.maxWeaponPower):
            self.currentWeaponPower = self.maxWeaponPower
    
    def increaseWeaponAngle(self):
        self.currentWeaponAngle += 1
        if(self.currentWeaponAngle > self.maxWeaponAngle):
            self.currentWeaponAngle = self.minWeaponAngle
    
    def decreaseWeaponAngle(self):
        self.currentWeaponAngle -= 1
        if(self.currentWeaponAngle < self.minWeaponAngle):
            self.currentWeaponAngle = self.maxWeaponAngle
         
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

        if hasattr(globals.current_view.mode, "planets"):
            for planet in globals.current_view.mode.planets:
                diff_vector = planet.body.position - self.body.position
                if diff_vector.Length() <  12:
                    self.body.angle = math.tan(float(diff_vector.x) / -diff_vector.y) + math.pi
