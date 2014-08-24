import gobject
import globals
from globals.types import Point
import Box2D as box2d

class Projectile(gobject.BoxGobject):

    def __init__(self, image, bl, force):
        self.image = image
        self.isBullet = True

        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + Point(15,15)

        super(Projectile,self).__init__(bl, tr, self.tc)

        self.body.SetMassFromShapes()
        globals.physics.AddObject(self)

        self.body.ApplyForce(force, self.body.GetWorldCenter())
