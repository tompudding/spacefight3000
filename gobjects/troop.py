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
    jump_power = 50
    jump_duration = 300
    def __init__(self, initialWeapon, bl):
        tr = bl + Point(50,50)
        self.texture_filename = 'redtrooper.png'
        self.selectedBoxFilename = 'selectionBox.png'
        self.selected = False
        self.selectionBoxQuad = None
        self.selectedBoxtc = globals.atlas.TextureSpriteCoords(self.selectedBoxFilename)
        self.currentWeaponAngle = 0
        self.currentWeaponPower = 0

        self.max_weapon_power = 1
        self.power_increase_amount_per_milisecond = (0.2 / 1000.0)
        self.last_power_update_time = globals.time

        self.locked_planet = None
        self.move_direction = Point(0,0)
        self.jumping = None
        self.charging = False
        self.teleport_target = None

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

    def Teleport(self, target_portal_end):
        self.teleport_target = target_portal_end

    def select(self):
        self.selected = True
        self.selectionBoxQuad.Enable()

    def unselect(self):
        self.selected = False
        self.selectionBoxQuad.Disable()

    def fireWeapon(self):
        current_bl_pos = self.getProjectileBLPosition()

        newProjectile = self.currentWeapon.FireAtTarget(self.currentWeaponAngle, self.currentWeaponPower, current_bl_pos)

        #switch weapon if we run out of ammo.
        if(self.currentWeapon.isOutOfAmmo()):
            self.currentWeapon = self.defaultWeapon

        #reset
        self.charging = False
        self.currentWeaponPower = 0.0
        globals.game_view.hud.setWeaponPowerBarValue(0.0)

        return newProjectile

    def getProjectileBLPosition(self):
        current_angle = self.body.angle
        update_distance_rect = cmath.rect(self.midpoint.x + 0.3, current_angle)
        x = update_distance_rect.real
        y = update_distance_rect.imag

        blx = (self.body.GetWorldCenter()[0] + x) / globals.physics.scale_factor
        bly = (self.body.GetWorldCenter()[1] + y) / globals.physics.scale_factor

        return Point(blx, bly)

    def chargeWeapon(self):
        self.charging = True

    def jump(self):
        if not self.locked_planet:
            #can only jump on the surface
            print 'jemp'
            return
        print 'jimp!'
        self.locked_planet = None
        r = cmath.rect(self.jump_power,self.body.angle+math.pi/2)
        self.body.ApplyImpulse(box2d.b2Vec2(r.real,r.imag),self.body.GetWorldCenter())
        self.jumping = globals.time + self.jump_duration

    def increaseWeaponPower(self):
        self.currentWeaponPower += 0.01
        if(self.currentWeaponPower > self.maxWeaponPower):
            self.currentWeaponPower = 0

    def decreaseWeaponPower(self):
        self.currentWeaponPower -= 0.01
        if(self.currentWeaponPower < 0):
            self.currentWeaponPower = self.maxWeaponPower

    def setWeaponAngle(self, mouse_xy):
        projectile_pos = self.getProjectileBLPosition()
        dx = float(mouse_xy[0] - (projectile_pos[0])) #/ globals.physics.scale_factor))
        dy = float(mouse_xy[1] - (projectile_pos[1])) #/ globals.physics.scale_factor))

        self.currentWeaponAngle = cmath.phase( complex(dx, dy) )

    def InitPolygons(self,tc):
        super(Troop,self).InitPolygons(self.tc)

        if self.dead:        #drawing.Translate(-self.viewpos.pos.x/2,-self.viewpos.pos.y/2,0)
            return
        self.selectionBoxQuad = drawing.Quad(globals.quad_buffer, tc = self.selectedBoxtc)

    def update(self):
        current_time = globals.time

        if self.teleport_target:
            self.body.SetXForm(self.teleport_target.body.position,0)
            self.teleport = None

        if self.charging:
            amountToIncreasePower = ( (current_time - self.last_power_update_time) ) * self.power_increase_amount_per_milisecond
            self.currentWeaponPower += amountToIncreasePower

            if(self.currentWeaponPower > self.max_weapon_power):
                self.currentWeaponPower = self.max_weapon_power
            
            globals.game_view.hud.setWeaponPowerBarValue(self.currentWeaponPower)

        self.last_power_update_time = current_time


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

        if self.jumping:
            if globals.time > self.jumping:
                #jump done
                self.jumping = False
            self.doGravity(gravity_sources)
            return

        if self.locked_planet:
            self.doGravity([self.locked_planet])
            diff_vector = self.body.position - self.locked_planet.body.position
            distance,angle = cmath.polar(complex(diff_vector.x,diff_vector.y))
            self.body.linearVelocity = box2d.b2Vec2(self.body.linearVelocity.x/10,self.body.linearVelocity.y/10)
            vector = cmath.rect(self.move_direction.x*200,self.body.angle)
            self.body.ApplyForce(box2d.b2Vec2(vector.real,vector.imag),self.body.GetWorldCenter())
            self.body.angle = angle - math.pi/2
            vector = cmath.rect(-1000,angle )
            self.body.ApplyForce(box2d.b2Vec2(vector.real,vector.imag),self.body.GetWorldCenter())
            #self.locked_planet = None
        else:
            self.doGravity(gravity_sources)
            if hasattr(globals.current_view, "game_world"):
                for planet in globals.current_view.game_world.planets:
                    diff_vector = self.body.position - planet.body.position
                    if diff_vector.Length() < planet.shape.radius*1.2:
                        #We're near a planet. We'll lock on if the velocity in direction towards the planets surface is low enough
                        v = self.body.linearVelocity.x*diff_vector.x + self.body.linearVelocity.y*diff_vector.y
                        if abs(v) < 5:
                            distance,angle = cmath.polar(complex(diff_vector.x,diff_vector.y))
                            self.body.angle = angle - math.pi/2
                            self.locked_planet = planet
                            vector = cmath.rect(-1000,angle )
                            self.body.ApplyForce(box2d.b2Vec2(vector.real,vector.imag),self.body.GetWorldCenter())
                            break
