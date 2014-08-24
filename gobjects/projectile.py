import gobject
import globals
from globals.types import Point
import Box2D as box2d

class Projectile(gobject.BoxGobject):
    
    def __init__(self, image, bl):
        self.image = image
        self.isBullet = True
        
        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + Point(5,5)
        
        super(Projectile,self).__init__(bl, tr, self.tc)
        
        self.body.SetMassFromShapes()
        globals.physics.AddObject(self)
    
        
        self.body.ApplyForce( box2d.b2Vec2(0,1000), self.body.GetWorldCenter())
        