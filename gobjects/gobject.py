import Box2D as box2d
from globals.types import Point
import globals
import drawing
import math
import gobjects
import numpy
import cmath

class Gobject(object):
    isBullet = False
    mass     = 1
    filter_group = None
    static   = False
    initial_health   = 500
    z_level  = 10
    is_gravity_source = False
    max_gravity_distance = 1000
    def __init__(self,bl,tr,tc = None,angle=0):
        self.dead = False
        self.tc = tc
        self.bl = bl
        self.tr = tr
        self.weapon_quad = None
        if tc != None:
            self.InitPolygons(tc)
            self.visible = True
        else:
            self.visible = False
        self.bodydef = box2d.b2BodyDef()
        #This is inefficient, but it doesn't want to grab properly otherwise. Shitty hack but whatever
        #self.bodydef.allowSleep = False
        self.midpoint = (tr - bl)*0.5*globals.physics.scale_factor
        self.bodydef.position = tuple((bl*globals.physics.scale_factor) + self.midpoint)
        self.bodydef.angle = angle
        self.shape = self.CreateShape(self.midpoint)
        if not self.static:
            self.shape.userData = self
        if self.filter_group != None:
            self.shape.filter.groupIndex = self.filter_group
        self.bodydef.isBullet = self.isBullet
        self.body = globals.physics.world.CreateBody(self.bodydef)
        self.shape.density = self.mass
        self.shape.friction = 0.7
        self.shapeI = self.body.CreateShape(self.shape)
        self.child_joint = None
        self.parent_joint = None
        self.ExtraShapes()
        self.PhysUpdate([])
        self.health = self.initial_health

    @property
    def centre_world(self):
        return self.body.GetWorldCenter()/globals.physics.scale_factor

    def ExtraShapes(self):
        pass

    def Destroy(self):
        if self.dead:
            return
        if self.parent_joint:
            #We're attached, so get rid of that before killing us
            self.parent_joint.Ungrab()
            self.parent_joint = None
        self.shape.ClearUserData()
        print 'destroy',self
        globals.physics.world.DestroyBody(self.body)
        self.dead = True
        self.quad.Delete()
        globals.sounds.portal_aura.stop()

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
        return Point(*self.body.position)/globals.physics.scale_factor

    def GetAngle(self):
        if self.dead:
            return
        return self.body.angle

    def doGravity(self,gravity_sources):
        if self.is_gravity_source:
            return

        if isinstance(self, gobjects.Projectile):
            if not self.applyGravity:
                return

        for source in gravity_sources:
            force_dir = -(self.centre_world - source.centre_world)
            distance = Point(*force_dir).length()
            force_dir = force_dir/distance
            force_magnitude = source.mass*75/(distance*distance)
            self.body.ApplyForce(force_dir*force_magnitude,self.body.GetWorldCenter())
            #print self,distance

    def PhysUpdate(self,gravity_sources):
        if self.dead or self.static:
            return
        #Just set the vertices
        vertices = [0,0,0,0]
        for i,vertex in enumerate(self.shape.vertices):
            screen_coords = Point(*self.body.GetWorldPoint(vertex))/globals.physics.scale_factor
            vertices[self.vertex_permutation[i]] = screen_coords

        self.quad.SetAllVertices(vertices, self.z_level)

        self.doGravity(gravity_sources)

class BoxGobject(Gobject):
    shape_type = box2d.b2PolygonDef
    vertex_permutation = (0,3,2,1)

class TeleportableBox(BoxGobject):
    teleport_duration = 1100
    portal_touch_duration = 1000
    teleport_min_velocity = 2
    always_instaport = False
    teleportable = True
    def __init__(self,bl,tr,tc):
        self.touch_portal = None
        self.instaport = None
        self.teleport_in_progress = None
        self.last_teleport = 0
        self.portal_contacts = []
        self.locked_planet = None
        self._move_direction = Point(0,0)
        super(TeleportableBox,self).__init__(bl,tr,tc)

    def TouchPortal(self, portal):
        #we've touched a portal. We want the following to happen:
        #If we're moving fast enough, just teleport us straight away
        #otherwise, wait a few seconds and then do it
        if self.teleport_in_progress:
            return
        if self.always_instaport or (not self.locked_planet and self.body.linearVelocity.Length() > self.teleport_min_velocity):
            if globals.time - self.last_teleport < 1000:
                #if we just teleported, don't do an instaport
                return
            self.instaport = portal.other_end
            return
        self.touch_portal = (portal,globals.time + self.portal_touch_duration)
        globals.sounds.portal_aura.play(loops=-1)

    @property
    def move_direction(self):
        return self._move_direction

    @move_direction.setter
    def move_direction(self,v):
        self._move_direction = v
        self.teleportable = True

    def AddPortalContact(self, portal, contact):
        if self.teleport_in_progress:
            return
        if not self.touch_portal:
            self.TouchPortal(portal)
        self.portal_contacts.append( (portal, contact) )

    def RemovePortalContact(self, portal, contact):
        if self.teleport_in_progress:
            return
        start_len = len(self.portal_contacts)
        new_contacts = []
        for p,c in self.portal_contacts:
            if p is not portal:
                #we don't care about these
                new_contacts.append( (p,c) )
            else:
                #it is portal, so don't use it if the contact id is the same
                if c.id != contact.id:
                    new_contacts.append( (p,c) )

        if len(new_contacts) == len(self.portal_contacts):
            #we didn't remove any
            return
        self.portal_contacts = new_contacts
        if not self.portal_contacts and self.touch_portal and self.touch_portal[0] is portal:
            self.touch_portal = None
            globals.sounds.portal_aura.stop()

    def InitiateTeleport(self, portal):
        if self.teleport_in_progress:
            return

        globals.sounds.portal_aura.stop()
        globals.sounds.teleport.play()
        if self.weapon_quad:
            self.weapon_quad.Disable()

        #rotate the linearvelcity by the angle of the portal
        r = self.body.linearVelocity.x + self.body.linearVelocity.y*1j
        distance,angle = cmath.polar(r)
        portal_angle = portal.other_end.body.angle - portal.body.angle
        rotate_velocity = cmath.rect(distance,angle - portal_angle)
        self.saved_linear_velocity = box2d.b2Vec2(rotate_velocity.real,rotate_velocity.imag)
        self.saved_angular_velocity = self.body.angularVelocity
        self.saved_angle = angle + portal_angle

        #Make 16 quads in the same place as before
        w = (self.quad.vertex[1] - self.quad.vertex[0])/4
        h = (self.quad.vertex[3] - self.quad.vertex[0])/4
        tc_w = (self.quad.tc[1] - self.quad.tc[0])/4
        tc_h = (self.quad.tc[3] - self.quad.tc[0])/4
        for i in xrange(4):
            for j in xrange(4):
                self.teleport_quads[i*4+j].Enable()
                self.teleport_quads[i*4+j].start_vertex[0] = self.quad.vertex[0] + w*j + h*i
                self.teleport_quads[i*4+j].start_vertex[1] = self.quad.vertex[0] + w*(j+1) + h*i
                self.teleport_quads[i*4+j].start_vertex[2] = self.quad.vertex[0] + w*(j+1) + h*(i+1)
                self.teleport_quads[i*4+j].start_vertex[3] = self.quad.vertex[0] + w*j + h*(i+1)

                self.teleport_quads[i*4+j].tc[0] = self.quad.tc[0] + tc_w*j + tc_h*i
                self.teleport_quads[i*4+j].tc[1] = self.quad.tc[0] + tc_w*(j+1) + tc_h*i
                self.teleport_quads[i*4+j].tc[2] = self.quad.tc[0] + tc_w*(j+1) + tc_h*(i+1)
                self.teleport_quads[i*4+j].tc[3] = self.quad.tc[0] + tc_w*j + tc_h*(i+1)

        self.body.SetXForm(portal.body.position,0)
        for i,vertex in enumerate(self.shape.vertices):
            screen_coords = Point(*self.body.GetWorldPoint(vertex))/globals.physics.scale_factor
            self.quad.vertex[self.vertex_permutation[i]] = (screen_coords.x,screen_coords.y,self.z_level)

        w = (self.quad.vertex[1] - self.quad.vertex[0])/4
        h = (self.quad.vertex[3] - self.quad.vertex[0])/4
        tc_w = (self.quad.tc[1] - self.quad.tc[0])/4
        tc_h = (self.quad.tc[3] - self.quad.tc[0])/4
        for i in xrange(4):
            for j in xrange(4):
                self.teleport_quads[i*4+j].target_vertex[0] = self.quad.vertex[0] + w*j + h*i
                self.teleport_quads[i*4+j].target_vertex[1] = self.quad.vertex[0] + w*(j+1) + h*i
                self.teleport_quads[i*4+j].target_vertex[2] = self.quad.vertex[0] + w*(j+1) + h*(i+1)
                self.teleport_quads[i*4+j].target_vertex[3] = self.quad.vertex[0] + w*j + h*(i+1)

        self.Disable()


        #Make it a sensor so it's not subject to the collision stuff
        self.body.PutToSleep()
        self.touch_portal = None
        globals.sounds.portal_aura.stop()
        self.portal_contacts = []
        self.teleport_in_progress = (portal,globals.time + self.teleport_duration)

    def InitPolygons(self,tc):
        super(TeleportableBox,self).InitPolygons(tc)
        self.teleport_quads = [drawing.Quad(globals.quad_buffer, tc = tc) for i in xrange(16)]
        for quad in self.teleport_quads:
            quad.start_vertex = [0,0,0,0]
            quad.target_vertex = [0,0,0,0]

    def Teleport(self, portal):
        self.Enable()
        for quad in self.teleport_quads:
            quad.Disable()
        self.body.WakeUp()
        self.touch_portal = None
        self.locked_planet = False
        self.portal_contacts = []
        self.body.SetXForm(portal.body.position,0)
        self.body.linearVelocity = self.saved_linear_velocity
        self.body.angularVelocity = self.saved_angular_velocity
        self.body.angle = self.saved_angle
        if(self.weapon_quad):
            self.weapon_quad.Enable()
        #Dont allow another teleport until we've moved
        self.teleportable = False

        self.last_teleport = globals.time

    @property
    def centre_world(self):
        if not self.teleport_in_progress:
            return self.body.GetWorldCenter()/globals.physics.scale_factor
        #teleport is in progress, report an approximate position
        portal,t = self.teleport_in_progress
        progress = 1-(t - globals.time)/float(self.teleport_duration)
        start = self.teleport_quads[0].start_vertex[0]
        end = self.teleport_quads[0].target_vertex[0]
        p = start + (end-start)*progress
        return box2d.b2Vec2(float(p[0]),float(p[1]))

    def TeleportUpdate(self):
        if self.teleport_in_progress:
            portal,t = self.teleport_in_progress
            if globals.time > t:
                self.teleport_in_progress = None
                self.Teleport(portal)
                return True

            progress = 1-(t - globals.time)/float(self.teleport_duration)
            for i in xrange(4):
                for j in xrange(4):
                    for k in xrange(4):
                        start = self.teleport_quads[i*4+j].start_vertex[k]
                        end = self.teleport_quads[i*4+j].target_vertex[k]
                        x = math.sin(progress*0.3*(i+1)*(j+1))*10
                        y = math.sin(progress*3*0.3*(i+1)*(j+1))*10
                        if progress > 0.5:
                            x *= 1-(0.5-progress)**2
                            y *= 1-(0.5-progress)**2
                        self.teleport_quads[i*4+j].vertex[k] = numpy.array([x,y,0]) + start + ((end-start)*progress)

            return True
        else:

            if self.instaport:
                print 'jim'
                self.InitiateTeleport(self.instaport)
                self.instaport = None

            if self.touch_portal:
                #check if we're still touching it. Really inefficient but I can't see a nice way of doing this in
                #box2d
                portal,end_time = self.touch_portal
                if globals.time > end_time:
                    self.InitiateTeleport(portal.other_end)
                    self.touch_portal = None
                    globals.sounds.portal_aura.stop()


class CircleGobject(Gobject):
    shape_type = box2d.b2CircleDef
    vertex_permutation = (1,0,3,2)
    is_sensor = False
    def __init__(self,centre,radius,tc = None,angle=0):
        self.dead = False
        self.tc = tc
        if tc != None:
            self.InitPolygons(tc)
            self.visible = True
        else:
            self.visible = False
        self.bodydef = box2d.b2BodyDef()
        #This is inefficient, but it doesn't want to grab properly otherwise. Shitty hack but whatever
        self.bodydef.allowSleep = False
        self.midpoint = radius*math.sqrt(2)*globals.physics.scale_factor
        self.bodydef.position = box2d.b2Vec2(*(centre*globals.physics.scale_factor))
        self.bodydef.angle = angle
        self.shape = self.CreateShape(radius)
        self.shape.isSensor = self.is_sensor
        if not self.static:
            self.shape.userData = self
        if self.filter_group != None:
            self.shape.filter.groupIndex = self.filter_group
        self.bodydef.isBullet = self.isBullet
        self.body = globals.physics.world.CreateBody(self.bodydef)
        self.shape.density = self.mass
        self.shape.friction = 0.7
        self.shapeI = self.body.CreateShape(self.shape)
        self.child_joint = None
        self.parent_joint = None
        self.ExtraShapes()
        self.PhysUpdate([])
        self.health = Gobject.initial_health

    def CreateShape(self,radius,pos = None):
        if self.dead:
            return
        shape = self.shape_type()
        shape.radius = radius*globals.physics.scale_factor
        self.midpoint = Point(0,0)
        if pos != None:
            shape.SetLocalPosition(pos.to_vec())
        return shape

    def PhysUpdate(self,gravity_sources):
        if self.dead:
            return
        #Just set the vertices

        p = Point(*self.body.GetWorldPoint(self.shape.localPosition))
        r = self.shape.radius

        for i,(x,y) in enumerate( ((r,r),(r,-r),(-r,-r),(-r,r)) ):
            screen_coords = Point(*self.body.GetWorldPoint(self.shape.localPosition+Point(x,y).to_vec()))/globals.physics.scale_factor
            self.quad.vertex[self.vertex_permutation[i]] = (screen_coords.x,screen_coords.y,self.z_level)
