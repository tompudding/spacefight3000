import gobject
import globals

class Planet(gobject.CircleGobject):
    texture_name = 'basicPlanet.png'
    static = True
    def __init__(self,physics,bl,tr):
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_name)
        super(Planet,self).__init__(physics,bl,tr,self.tc)
        self.body.SetMassFromShapes()
        physics.AddObject(self)
