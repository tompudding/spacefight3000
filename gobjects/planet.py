import gobject
import globals
from globals.types import Point
import cmath
import drawing
import math

class PortalEnd(gobject.CircleGobject):
    texture_name = 'gate'
    def __init__(self,centre,radius,angle):
        self.tc = [globals.atlas.TextureSpriteCoords(self.texture_name + '%d.png' % i) for i in xrange(6)]
        super(PortalEnd,self).__init__(centre,radius,self.tc)
        self.body.angle = angle
        self.PhysUpdate([])

    def InitPolygons(self,tcs):
        self.quad = drawing.Quad(globals.quad_buffer, tc = tcs[0])
        #self.body.angle = 2

    def CreateShape(self,midpoint,pos = None):
        return super(PortalEnd,self).CreateShape(midpoint,pos)


class Portal(object):
    size = 30
    def __init__(self,source_planet,source_angle,target_planet,target_angle):
        self.ends = []
        for planet,angle in (source_planet,source_angle),(target_planet,target_angle):
            centre = planet.GetSurfacePoint(self.size,angle)
            self.ends.append(PortalEnd(centre,self.size,angle+3*math.pi/2))


class Planet(gobject.CircleGobject):
    texture_name = '600blue.png'
    #static = True
    is_gravity_source = True
    def __init__(self,centre,radius):
        self.tc = globals.atlas.TextureSpriteCoords(self.texture_name)
        super(Planet,self).__init__(centre,radius,self.tc)
        globals.physics.AddObject(self)

    def GetSurfacePoint(self,distance,angle):
        centre = self.body.GetWorldCenter() / globals.physics.scale_factor
        vector = cmath.rect((self.shape.radius / globals.physics.scale_factor) + distance, angle)
        return Point(*centre) + Point(vector.real,vector.imag)

class BluePlanet(Planet):
    texture_name = '600blue.png'

class YellowPlanet(Planet):
    texture_name = '600yellow.png'
