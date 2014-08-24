import gobject
import globals
import weapon
import math
from globals.types import Point
import math
import cmath
import drawing
import Box2D as box2d

class Troop(gobject.BoxGobject):

    def __init__(self, initialWeapon, bl):
        tr = bl + Point(50,50)
        self.texture_filename = 'bazookaTroop.png'
        self.selectedBoxFilename = 'selectionBox.png'
        self.selected = False
        self.selectionBoxQuad = None
        self.selectedBoxtc = globals.atlas.TextureSpriteCoords(self.selectedBoxFilename)
        self.currentWeaponAngle = 0
        self.currentWeaponPower = 0

        self.maxWeaponPower = 100
        self.maxWeaponAngle = (2 * math.pi)
        self.minWeaponAngle = 0
        self.angleModificationAmount = 0.17 #about 10 degrees, needs to be fairly granular.
        self.locked_planet = None
        self.move_direction = Point(0,0)


        self.tc = globals.atlas.TextureSpriteCoords(self.texture_filename)
        super(Troop,self).__init__(bl,tr,self.tc)

        #always create the unit with a default weapon that has infinite ammo. Could change this later, but if
        #you want to give another weapon that isnt unlimited, use change weapon.
        self.currentWeapon = initialWeapon()
        self.defaultWeapon = initialWeapon()

        self.body.SetMassFromShapes()
        if not self.static:
            globals.physics.AddObject(self)

        self.selectionBoxQuad.Disable()

    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon

    def select(self):
        self.selected = True
        self.selectionBoxQuad.Enable()

    def unselect(self):
        self.selected = False
        self.selectionBoxQuad.Disable()

    def fireWeapon(self):
        newProjectile = self.currentWeapon.FireAtTarget(self.currentWeaponPower, self.currentWeaponAngle, self.bl)

        #switch weapon if we run out of ammo.
        if(self.currentWeapon.isOutOfAmmo()):
            self.currentWeapon = self.defaultWeapon

        return newProjectile


    def increaseWeaponPower(self):
        self.currentWeaponPower += 1
        if(self.currentWeaponPower > self.maxWeaponPower):
            self.currentWeaponPower = 0

    def decreaseWeaponPower(self):
        self.currentWeaponPower -= 1
        if(self.currentWeaponPower < 0):
            self.currentWeaponPower = self.maxWeaponPower

    def increaseWeaponAngle(self):
        self.currentWeaponAngle += self.angleModificationAmount
        if(self.currentWeaponAngle > self.maxWeaponAngle):
            self.currentWeaponAngle = self.minWeaponAngle

    def decreaseWeaponAngle(self):
        self.currentWeaponAngle -= self.angleModificationAmount
        if(self.currentWeaponAngle < self.minWeaponAngle):
            self.currentWeaponAngle = self.maxWeaponAngle

    def InitPolygons(self,tc):
        super(Troop,self).InitPolygons(self.tc)

        if self.dead:        #drawing.Translate(-self.viewpos.pos.x/2,-self.viewpos.pos.y/2,0)
            return
        self.selectionBoxQuad = drawing.Quad(globals.quad_buffer, tc = self.selectedBoxtc)

    def Update(self):
        pass

    def PhysUpdate(self,gravity_sources):
        #Don't pass the gravity sources as we want to take care of that
        super(Troop,self).PhysUpdate([])
        if self.dead or self.static:
            return
        #Just set the vertices
        vertices = []
        for i,vertex in enumerate(self.shape.vertices):
            screen_coords = Point(*self.body.GetWorldPoint(vertex))/globals.physics.scale_factor
            vertices.append( screen_coords )

        self.selectionBoxQuad.SetAllVertices(vertices, self.z_level+0.1)

        if self.locked_planet:
            self.doGravity([self.locked_planet])
            diff_vector = self.body.position - self.locked_planet.body.position
            distance,angle = cmath.polar(complex(diff_vector.x,diff_vector.y))
            self.body.linearVelocity = box2d.b2Vec2(0,0)
            vector = cmath.rect(self.move_direction.x*200,self.body.angle)
            self.body.ApplyForce(box2d.b2Vec2(vector.real,vector.imag),self.body.GetWorldCenter())
            self.body.angle = angle - math.pi/2
            self.locked_planet = None
        else:
            self.doGravity(gravity_sources)
            if hasattr(globals.current_view.mode, "planets"):
                for planet in globals.current_view.mode.planets:
                    diff_vector = self.body.position - planet.body.position
                    if diff_vector.Length() < planet.shape.radius*1.2:
                        #We're near a planet. We'll lock on if the velocity in direction towards the planets surface is low enough
                        v = self.body.linearVelocity.x*diff_vector.x + self.body.linearVelocity.y*diff_vector.y
                        if abs(v) < 5:
                            distance,angle = cmath.polar(complex(diff_vector.x,diff_vector.y))
                            self.body.angle = angle - math.pi/2
                            self.locked_planet = planet
                            self.body.linearVelocity = box2d.b2Vec2(0,0)
                            break
