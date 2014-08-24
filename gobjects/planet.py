import gobject
import globals
from globals.types import Point
import cmath
import drawing

class PortalEnd(gobject.CircleGobject):
    texture_name = 'gate'
    def __init__(self,bl,tr):
        self.tc = [globals.atlas.TextureSpriteCoords(self.texture_name + '%d.png' % i) for i in xrange(6)]
        super(PortalEnd,self).__init__(bl,tr,self.tc)

    def InitPolygons(self,tcs):
        self.quad = drawing.Quad(globals.quad_buffer, tc = tcs[0])

class Portal(object):
    def __init__(self,source_planet,source_angle,target_planet,target_angle):
        self.ends = []
        for planet,angle in (source_planet,source_angle),(target_planet,target_angle):
            bl = source_planet.GetSurfacePoint(source_angle)
            tr = bl + Point(50,50)
            self.ends.append(PortalEnd(bl,tr))


class Planet(gobject.CircleGobject):
    texture_name = '600blue.png'
    #static = True
    is_gravity_source = True
    def __init__(self,bl,tr):
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_name)
        super(Planet,self).__init__(bl,tr,self.tc)
        globals.physics.AddObject(self)

    def GetSurfacePoint(self,angle):
        centre = self.body.GetWorldCenter() / globals.physics.scale_factor
        vector = cmath.rect(self.shape.radius / globals.physics.scale_factor, angle)
        return Point(*centre) + Point(vector.real,vector.imag)

class BluePlanet(Planet):
    texture_name = '600blue.png'

class YellowPlanet(Planet):
    texture_name = '600yellow.png'
