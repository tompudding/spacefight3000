import gobject
import globals
import weapon
import math
from globals.types import Point
import math
import cmath
import drawing
import Box2D as box2d
import numpy
from collections import namedtuple

class Troop(gobject.TeleportableBox):
    texture_name = 'redtrooper'
    frame_duration = 100
    jump_power = 50
    jump_duration = 300
    def __init__(self, initialWeapon, bl, goodness):
        self.good = goodness
        if self.good == 0:
            self.texture_name = 'alien'
        self.direction = 'right'
        self.tc_right = [globals.atlas.TextureSpriteCoords(self.texture_name +'_right_%d.png' % i) for i in xrange(4)]
        self.tc_left = [globals.atlas.TextureSpriteCoords(self.texture_name +'_left_%d.png' % i) for i in xrange(4)]
        self.last_frame = self.tc_right[0]
        self.animation_duration = len(self.tc_right)*self.frame_duration
        tr = bl + Point(25,50)
        self.selectedBoxFilename = 'selectionBox.png'
        self.selected = False
        self.selectionBoxQuad = None
        self.selectedBoxtc = globals.atlas.TextureSpriteCoords(self.selectedBoxFilename)
        self.currentWeaponAngle = 0
        self.currentWeaponPower = 0

        self.max_weapon_power = 1
        self.power_increase_amount_per_milisecond = (0.6 / 1000.0)
        self.last_power_update_time = globals.time
        self.projectile_position = None
        self.last_mouse_xy = None

        self.locked_planet = None
        self.move_direction = Point(0,0)
        self.jumping = None
        self.charging = False

        super(Troop,self).__init__(bl,tr,self.tc_right)

        #always create the unit with a default weapon that has infinite ammo. Could change this later, but if
        #you want to give another weapon that isnt unlimited, use change weapon.
        self.weapon_options = []
        self.currentWeapon = initialWeapon()
        self.weapon_options.append(self.currentWeapon)
        self.defaultWeapon = initialWeapon()

        self.body.SetMassFromShapes()
        if not self.static:
            globals.physics.AddObject(self)

        self.selectionBoxQuad.Disable()
        self.z_level = 200

    def changeWeapon(self, btnClass, pos, button, weaponToChangeTo):
        self.currentWeapon = weaponToChangeTo
    
    def setDirection(self,newdirection):
        self.direction = newdirection


    def Disable(self):
        self.quad.Disable()
        self.selectionBoxQuad.Disable()

    def Enable(self):
        self.quad.Enable()
        if self.selected:
            self.selectionBoxQuad.Enable()

    def add_weapon(self, wpn):
        self.weapon_options.append(wpn())
        

    def select(self):
        self.selected = True
        self.selectionBoxQuad.Enable()
        self.createWeaponSelectionBoxes()

    
    def createWeaponSelectionBoxes(self):
        weapon_selection_options = []
        for weapon in self.weapon_options:
            wpn_detail = namedtuple("wpn_detail", 'image, image_size, callback, callback_args')
            detail = wpn_detail(weapon.projectileImage, weapon.imageSize, self.changeWeapon, weapon)
            
            weapon_selection_options.append( detail )
            weapon_selection_options.append( detail )
        
        globals.game_view.hud.createWeaponSelectionBoxs(weapon_selection_options)
        
    def unselect(self):
        self.selected = False
        self.selectionBoxQuad.Disable()
        self.move_direction = Point(0,0)
        #globals.game_view.hud.clearWeaponSelectionBoxs()

    def fireWeapon(self):
        self.setWeaponAngle(self.last_mouse_xy)
        #self.getProjectileBLPosition(self.last_mouse_xy)
        newProjectile = self.currentWeapon.FireAtTarget(self.currentWeaponAngle, self.currentWeaponPower, self.projectile_position, self)

        #switch weapon if we run out of ammo.
        if(self.currentWeapon.isOutOfAmmo()):
            self.weapon_options.remove(self.currentWeapon)
            self.currentWeapon = self.defaultWeapon
            self.createWeaponSelectionBoxes()
            
            

        #reset
        self.charging = False
        self.currentWeaponPower = 0.0
        globals.game_view.hud.setWeaponPowerBarValue(0.0)

        return newProjectile

    def getProjectileBLPosition(self, mouse_xy):
        dx = mouse_xy[0] - self.body.GetWorldCenter()[0] / globals.physics.scale_factor
        dy = mouse_xy[1] - self.body.GetWorldCenter()[1] / globals.physics.scale_factor

        projectile_start_pos = box2d.b2Vec2(dx,dy)
        projectile_start_pos.Normalize()
        projectile_start_pos.mul_float(self.midpoint.x + 30)
        projectile_start_pos.add_vector(box2d.b2Vec2(self.body.GetWorldCenter()[0] / globals.physics.scale_factor, self.body.GetWorldCenter()[1] / globals.physics.scale_factor))

        self.projectile_position = Point(projectile_start_pos[0], projectile_start_pos[1])
        #current_angle = self.body.angle

        #if(self.direction == 'right'):
        #    update_distance_rect = cmath.rect(self.midpoint.x + 1, current_angle)
        #    x = update_distance_rect.real
        #    y = update_distance_rect.imag
        #    blx = (self.body.GetWorldCenter()[0] + x) / globals.physics.scale_factor
        #    bly = (self.body.GetWorldCenter()[1] + y) / globals.physics.scale_factor
        #else:
        #    update_distance_rect = cmath.rect(self.midpoint.x - 1, current_angle + math.pi)
        #    x = update_distance_rect.real
        #    y = update_distance_rect.imag
        #    blx = (self.body.GetWorldCenter()[0] - x) / globals.physics.scale_factor
        #    bly = (self.body.GetWorldCenter()[1] + y) / globals.physics.scale_factor

        #return Point(blx, bly)

    def chargeWeapon(self):
        self.charging = True

    def jump(self):
        if not self.locked_planet:
            #can only jump on the surface
            return
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
        self.last_mouse_xy = mouse_xy
        self.getProjectileBLPosition(mouse_xy)

        dx = float(mouse_xy[0] - (self.projectile_position[0])) #/ globals.physics.scale_factor))
        dy = float(mouse_xy[1] - (self.projectile_position[1])) #/ globals.physics.scale_factor))

        self.currentWeaponAngle = cmath.phase( complex(dx, dy) )

    def InitPolygons(self,tc):
        if self.direction == 'right':
            tc = self.tc_right[0]
            super(Troop,self).InitPolygons(self.tc_right[0])
        else:
            tc = self.tc_left[0]
            super(Troop,self).InitPolygons(self.tc_left[0])

        if self.dead:        #drawing.Translate(-self.viewpos.pos.x/2,-self.viewpos.pos.y/2,0)
            return

        self.selectionBoxQuad = drawing.Quad(globals.quad_buffer, tc = self.selectedBoxtc)

    def Update(self):
        current_time = globals.time

        if self.TeleportUpdate():
            return


        if self.charging:
            amountToIncreasePower = ( (current_time - self.last_power_update_time) ) * self.power_increase_amount_per_milisecond
            self.currentWeaponPower += amountToIncreasePower

            if(self.currentWeaponPower > self.max_weapon_power):
                self.currentWeaponPower = self.max_weapon_power

            globals.game_view.hud.setWeaponPowerBarValue(self.currentWeaponPower)

        self.last_power_update_time = current_time

        if(self.health <= 0):
            self.Destroy()

    def TakeDamage(self, amount):
        self.health -= amount

    def PhysUpdate(self,gravity_sources):
        #Don't pass the gravity sources as we want to take care of that
        if self.teleport_in_progress:
            return
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
            if self.move_direction.x > 0:
                self.direction = 'right'
            elif self.move_direction.x < 0:
                self.direction = 'left'
            else:
                self.direction = 'none'
            oldframe = self.last_frame
            frame = (globals.time%self.animation_duration)/self.frame_duration
            if self.direction == 'right':
                tc = self.tc_right[frame]
            elif self.direction == 'left':
                tc = self.tc_left[frame]
            else:
                tc = oldframe
            self.last_frame = tc
            self.quad.SetTextureCoordinates(tc)

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

    def Destroy(self):
        super(Troop,self).Destroy()
        self.selectionBoxQuad.Delete()
