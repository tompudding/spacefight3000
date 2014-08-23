import gobject
import globals

class Troop(gobject.BoxGobject):
    texture_name = 'bazookaTroop.png'
    def __init__(self,physics,bl,tr):
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_name)
        super(Troop,self).__init__(physics,bl,tr,self.tc)
        self.body.SetMassFromShapes()
        if not self.static:
            physics.AddObject(self)
