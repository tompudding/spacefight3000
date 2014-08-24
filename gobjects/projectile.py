import gobject
import globals
from globals.types import Point
import Box2D as box2d

class Projectile(gobject.TeleportableBox):
    always_instaport = True
    def __init__(self, image, bl, force, maxDamage, parentTroop):
        self.image = image
        self.isBullet = True
        self.destroyMe = False
        self.ParentTroop = parentTroop
        self.maxDamage = maxDamage
        self.destroy_at = 0
        self.applyGravity = True

        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + Point(10,10)

        super(Projectile,self).__init__(bl, tr, self.tc)

        self.body.SetMassFromShapes()
        globals.physics.AddObject(self)
        self.body.ApplyForce(force, self.body.GetWorldCenter())
    
    def dontApplyGravity(self):
        self.applyGravity = False

    def destroyNextUpdate(self):
        self.destroyMe = True
        self.destroy_at = globals.time

    def Disable(self):
        self.quad.Disable()

    def Enable(self):
        self.quad.Enable()

    def destroyAfterTimeLimit(self):
        time_limit = 5000
        
        if(not self.applyGravity):
            time_limit = 100
            self.applyGravity = True
        if(not self.destroyMe):
            self.destroyMe = True
            self.destroy_at = globals.time + time_limit


    def Update(self):
        if self.TeleportUpdate():
            return

        if(self.destroyMe):
            if(globals.time >= self.destroy_at):
                self.Destroy()
