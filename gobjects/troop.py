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
import ui
from collections import namedtuple

class Troop(gobject.TeleportableBox):
    texture_name = 'redtrooper'
    frame_duration = 100
    jump_power = 40
    jump_duration = 300
    def __init__(self, initialWeapon, bl, goodness):
        self.good = goodness
        self.health = self.initial_health
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

        health_bar_size = globals.game_view.GetRelative(Point(20,10))
        self.health_bar = ui.PowerBar(parent=globals.game_view,
                                     pos=Point(0,0),
                                     tr=health_bar_size,
                                     level=1.0,
                                     bar_colours=(drawing.constants.colours.red,
                                                  drawing.constants.colours.yellow,
                                                  drawing.constants.colours.green),
                                     buffer=globals.nonstatic_ui_buffer,
                                     border_colour = drawing.constants.colours.white)
        self.health_bar.Disable()

        self.max_weapon_power = 1
        self.power_increase_amount_per_milisecond = (0.6 / 1000.0)
        self.last_power_update_time = globals.time
        self.projectile_position = None

        self.locked_planet = None
        self.move_direction = Point(0,0)
        self.jumping = None
        self.charging = False
        self.amount_moved = 0

        super(Troop,self).__init__(bl,tr,self.tc_right)
        self.teleportable = goodness

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
        self.SetWeaponQuad()

    def changeWeapon(self, btnClass, pos, button, weaponToChangeTo):
        globals.sounds.select_weapon.play()
        self.currentWeapon = weaponToChangeTo
        self.SetWeaponQuad()

    def SetWeaponQuad(self):
        if self.direction == 'right':
            tc = self.currentWeapon.item_tc_right
        else:
            tc = self.currentWeapon.item_tc_left
        if tc:
            self.weapon_quad.SetTextureCoordinates(tc)

    def setDirection(self,newdirection):
        self.direction = newdirection


    def Disable(self):
        self.quad.Disable()
        self.selectionBoxQuad.Disable()

    def Enable(self):
        self.quad.Enable()
        if self.selected:
            self.selectionBoxQuad.Enable()

    def Destroy(self):
        print 'bob'
        super(Troop,self).Destroy()
        if not self.static:
            globals.physics.RemoveObject(self)
        self.health_bar.Delete()
        self.selectionBoxQuad.Delete()

    def add_weapon(self, wpn):
        self.weapon_options.append(wpn())


    def select(self):
        self.selected = True
        self.selectionBoxQuad.Enable()
        self.createWeaponSelectionBoxes()


    def createWeaponSelectionBoxes(self):
        weapon_selection_options = []
        for weapon in self.weapon_options:
            wpn_detail = namedtuple("wpn_detail", 'image, image_size, callback, callback_args, limited_ammo, current_ammo')
            detail = wpn_detail(weapon.projectileImage, weapon.imageSize, self.changeWeapon, weapon, weapon.limitedAmmo, weapon.currentAmmo)

            weapon_selection_options.append( detail )

        globals.game_view.hud.createWeaponSelectionBoxs(weapon_selection_options)

    def unselect(self):
        self.selected = False
        self.charging = False
        self.selectionBoxQuad.Disable()
        self.move_direction = Point(0,0)
        globals.game_view.hud.setWeaponPowerBarValue(0.0)

    def fireWeapon(self):
        newProjectile = self.currentWeapon.FireAtTarget(self.currentWeaponAngle, self.currentWeaponPower, self.projectile_position, self)

        #switch weapon if we run out of ammo.
        if self.currentWeapon.isOutOfAmmo():
            self.weapon_options.remove(self.currentWeapon)
            self.currentWeapon = self.defaultWeapon

        self.createWeaponSelectionBoxes()



        #reset
        self.charging = False
        self.currentWeaponPower = 0.0
        globals.game_view.hud.setWeaponPowerBarValue(0.0)

        return newProjectile

    def SetProjectileBLPosition(self, dx, dy):

        projectile_start_pos = box2d.b2Vec2(dx,dy)
        projectile_start_pos.Normalize()
        projectile_start_pos.mul_float(self.midpoint.x + 30)
        projectile_start_pos.add_vector(box2d.b2Vec2(self.body.GetWorldCenter()[0] / globals.physics.scale_factor, self.body.GetWorldCenter()[1] / globals.physics.scale_factor))

        self.projectile_position = Point(projectile_start_pos[0], projectile_start_pos[1])

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
        self.SetWeaponPower(self.currentWeaponPower + 0.01)

    def decreaseWeaponPower(self):
        self.SetWeaponPower(self.currentWeaponPower - 0.01)

    def SetWeaponPower(self, power):
        if power > self.max_weapon_power:
            self.currentWeaponPower = self.maxWeaponPower
        elif power < 0:
            self.currentWeaponPower = 0
        else:
            self.currentWeaponPower = power

    def setWeaponAngle(self, mouse_xy):
        dx = float(mouse_xy[0] * globals.physics.scale_factor - (self.body.position[0])) #/ globals.physics.scale_factor))
        dy = float(mouse_xy[1] * globals.physics.scale_factor - (self.body.position[1])) #/ globals.physics.scale_factor))

        self.ActuallySetWeaponVector( dx, dy )

    def ActuallySetWeaponVector(self, dx, dy):
        self.currentWeaponAngle = cmath.phase( complex(dx, dy) )
        self.SetProjectileBLPosition(dx, dy)

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
        self.weapon_quad = drawing.Quad(globals.quad_buffer)

    def Update(self):
        current_time = globals.time

        if self.TeleportUpdate():
            return


        if self.charging:
            amountToIncreasePower = ( (current_time - self.last_power_update_time) ) * self.power_increase_amount_per_milisecond
            self.currentWeaponPower += amountToIncreasePower

            if self.currentWeaponPower > self.max_weapon_power:
                self.currentWeaponPower = self.max_weapon_power

            globals.game_view.hud.setWeaponPowerBarValue(self.currentWeaponPower)

        self.last_power_update_time = current_time

        if self.health <= 0:
            self.Destroy()

    def TakeDamage(self, amount):
        self.health -= amount
        amount_full = float(self.health)/self.initial_health
        self.health_bar.SetBarLevel(amount_full)
        if self.health != self.initial_health:
            self.health_bar.Enable()
        else:
            self.health_bar.Disable()
        print self.health

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
        self.weapon_quad.SetAllVertices(vertices, self.z_level+0.1)
        if self.health != self.initial_health:
            self.health_bar.SetPosAbsolute( vertices[2] + Point(10,10) )

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
            self.amount_moved += abs(vector.real) / 1000
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
