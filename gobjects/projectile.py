import gobject
import globals
from globals.types import Point

class Projectile(gobject.BoxGobject):
    
    def __init__(self, image, bl):
        self.image = image
        self.isBullet = True
        
        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + Point(50,50)
        
        super(Projectile,self).__init__(bl, tr, self.tc)
