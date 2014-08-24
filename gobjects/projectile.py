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
        self.destroy_at = 0

        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + Point(10,10)

        super(Projectile,self).__init__(bl, tr, self.tc)

        self.body.SetMassFromShapes()
        globals.physics.AddObject(self)
        self.body.ApplyForce(force, self.body.GetWorldCenter())

    
    def destroyNextUpdate(self):
        self.destroyMe = True
        self.destroy_at = globals.time
    
    def destroyAfterTimeLimit(self):
        if(not self.destroyMe):
            self.destroyMe = True
            self.destroy_at = globals.time + 5000
        
    def Update(self):
        if(self.destroyMe):
            if(globals.time >= self.destroy_at):
                self.Destroy()
    