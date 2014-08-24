import gobject
import globals

class Planet(gobject.CircleGobject):
    texture_name = '600blue.png'
    #static = True
    is_gravity_source = True
    def __init__(self,bl,tr):
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_name)
        super(Planet,self).__init__(bl,tr,self.tc)
        globals.physics.AddObject(self)

class BluePlanet(Planet):
    texture_name = '600blue.png'

class YellowPlanet(Planet):
    texture_name = '600yellow.png'
