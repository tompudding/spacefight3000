import gobject
import globals
from globals.types import Point
import Box2D as box2d

class Projectile(gobject.BoxGobject):
    
    def __init__(self, image, bl, force, maxDamage, parentTroop):
        self.image = image
        self.isBullet = True
        self.destroyMe = False
        self.ParentTroop = parentTroop
        self.maxDamage = maxDamage
        
        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + Point(5,5)
        
        super(Projectile,self).__init__(bl, tr, self.tc)
        
        self.body.SetMassFromShapes()
        globals.physics.AddObject(self)
        self.body.ApplyForce(force, self.body.GetWorldCenter())

    
    def destroyNextUpdate(self):
        self.destroyMe = True
        
    def Update(self):
        if(self.destroyMe):
            self.Destroy()
    