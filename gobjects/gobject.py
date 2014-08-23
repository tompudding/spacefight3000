import Box2D as box2d
from globals.types import Point
import globals
import drawing
import math

class Gobject(object):
    isBullet = False
    mass     = 1
    filter_group = None
    static   = False
    health   = 500
    z_level  = 10
    def __init__(self,physics,bl,tr,tc = None,angle=0):
        self.dead = False
        self.tc = tc
        self.bl = bl
        self.tr = tr
        if tc != None:
            self.InitPolygons(tc)
            self.visible = True
        else:
            self.visible = False
        self.physics = physics
        self.bodydef = box2d.b2BodyDef()
        #This is inefficient, but it doesn't want to grab properly otherwise. Shitty hack but whatever
        self.bodydef.allowSleep = False
        self.midpoint = (tr - bl)*0.5*physics.scale_factor
        self.bodydef.position = tuple((bl*physics.scale_factor) + self.midpoint)
        self.bodydef.angle = angle
        self.shape = self.CreateShape(self.midpoint)
        if not self.static:
            self.shape.userData = self
        if self.filter_group != None:
            self.shape.filter.groupIndex = self.filter_group
        self.bodydef.isBullet = self.isBullet
        self.body = physics.world.CreateBody(self.bodydef)
        self.shape.density = self.mass
        self.shape.friction = 0.7
        self.shapeI = self.body.CreateShape(self.shape)
        self.child_joint = None
        self.parent_joint = None
        self.ExtraShapes()
        self.PhysUpdate()

    def ExtraShapes(self):
        pass

    def Destroy(self):
        if self.static:
            #Don't ever destroy static things
            return
        if self.dead:
            return
        if self.parent_joint:
            #We're attached, so get rid of that before killing us
            self.parent_joint.Ungrab()
            self.parent_joint = None
        self.shape.ClearUserData()
        self.physics.world.DestroyBody(self.body)
        self.dead = True
        self.quad.Delete()

    def Damage(self,amount):
        #can't damage static stuff
        return

    def CreateShape(self,midpoint,pos = None):
        if self.dead:
            return
        shape = self.shape_type()
        if pos == None:
            shape.SetAsBox(*midpoint)
        else:
            shape.SetAsBox(midpoint[0],midpoint[1],pos.to_vec(),0)
        return shape

    def InitPolygons(self,tc):
        if self.dead:
            return
        self.quad = drawing.Quad(globals.quad_buffer,tc = tc)


    def GetPos(self):
        if self.dead:
            return
        return Point(*self.body.position)/self.physics.scale_factor

    def GetAngle(self):
        if self.dead:
            return
        return self.body.angle

    def PhysUpdate(self):
        if self.dead or self.static:
            return
        #Just set the vertices

        for i,vertex in enumerate(self.shape.vertices):
            screen_coords = Point(*self.body.GetWorldPoint(vertex))/self.physics.scale_factor
            self.quad.vertex[self.vertex_permutation[i]] = (screen_coords.x,screen_coords.y,self.z_level)

class BoxGobject(Gobject):
    shape_type = box2d.b2PolygonDef

class CircleGobject(Gobject):
    shape_type = box2d.b2CircleDef
    vertex_permutation = (0,3,2,1)
    def CreateShape(self,midpoint,pos = None):
        if self.dead:
            return
        shape = self.shape_type()
        shape.radius = midpoint.length()/math.sqrt(2)
        if pos != None:
            shape.SetLocalPosition(pos.to_vec())
        return shape

    def PhysUpdate(self):
        if self.dead:
            return
        #Just set the vertices

        p = Point(*self.body.GetWorldPoint(self.shape.localPosition))
        r = self.shape.radius
        
        for i,(x,y) in enumerate( ((r,r),(r,-r),(-r,-r),(-r,r)) ):
            screen_coords = Point(*self.body.GetWorldPoint(self.shape.localPosition+Point(x,y).to_vec()))/self.physics.scale_factor
            self.quad.vertex[self.vertex_permutation[i]] = (screen_coords.x,screen_coords.y,self.z_level)

