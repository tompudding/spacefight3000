import gobject
import globals
from globals.types import Point
import Box2D as box2d
import drawing
import math
import itertools

class Projectile(gobject.TeleportableBox):
    always_instaport = True
    def __init__(self, image, bl, imageSize, imageAngle, force, maxDamage, parentTroop, explosive):
        self.image = image
        self.isBullet = True
        self.destroyMe = False
        self.ParentTroop = parentTroop
        self.maxDamage = maxDamage
        self.destroy_at = 0
        self.applyGravity = True
        self.explosive = explosive

        self.tc = globals.atlas.TextureSpriteCoords(self.image)
        tr = bl + imageSize

        super(Projectile,self).__init__(bl, tr, self.tc)

        self.body.SetMassFromShapes()
        globals.physics.AddObject(self)
        self.body.angle = imageAngle
        self.body.ApplyForce(force, self.body.GetWorldCenter())

        #explosion stuff
        self.setupExplosionQuads()
        self.exploding = False

    def setupExplosionQuads(self):
        self.explosion_frame_duration = 100
        self.tc_explode = [globals.atlas.TextureSpriteCoords("splode" +'%d.png' % i) for i in xrange(7)]

        self.explosion_duration = len(self.tc_explode)*self.explosion_frame_duration
        self.explosion_quad = drawing.Quad(globals.quad_buffer, tc = self.tc_explode[0])

        self.explosion_quad.SetVertices(self.bl, self.tr, drawing.constants.DrawLevels.ui)
        self.explosion_quad.SetTextureCoordinates(self.tc_explode[1])

        self.explosion_quad.Disable()

        self.last_explosion_tc = 0


    def dontApplyGravity(self):
        self.applyGravity = False

    def destroyNextUpdate(self):
        self.destroyMe = True
        self.destroy_at = globals.time


    def Destroy(self):
        super(Projectile,self).Destroy()
        globals.physics.RemoveObject(self)

    def Disable(self):
        self.quad.Disable()

    def Enable(self):
        self.quad.Enable()

    def destroyAfterTimeLimit(self, limit):
        time_limit = limit

        if not self.applyGravity:
            self.applyGravity = True
        if not self.destroyMe:
            self.destroyMe = True
            self.destroy_at = globals.time + time_limit

    def explode(self):
        if self.explosive:
            if self.exploding:
                required_explosion_tc = (globals.time - self.startOfExplosion) / self.explosion_frame_duration
                if self.last_explosion_tc != required_explosion_tc:
                    if required_explosion_tc >= len(self.tc_explode):
                        return False
                    else:
                        self.progressExplosionAnimation(required_explosion_tc)
                        return True
            else:
                self.createExplosion()
                return True
        else:
            return False

        return True

    def progressExplosionAnimation(self, required_explosion_tc):
        self.explosion_quad.SetTextureCoordinates(self.tc_explode[required_explosion_tc])
        self.explosion_quad.SetVertices(self.explosion_bl, self.explosion_tr, drawing.constants.DrawLevels.ui)
        self.last_explosion_tc = required_explosion_tc

    def createExplosion(self):
        globals.sounds.explosion.play()
        self.startOfExplosion = globals.time
        self.exploding = True
        self.quad.Disable()

        self.getExplosionPosition()
        self.explosion_quad.SetVertices(self.explosion_bl, self.explosion_tr, drawing.constants.DrawLevels.ui)
        self.explosion_quad.Enable()

        #check for damage to some mans
        for troop in itertools.chain(globals.game_view.game_world.goodies, globals.game_view.game_world.baddies):
            explosionRange = 50
            explosionRange = math.pow(50, 2)
            explosionDamage = 200
        
            troopCenter = Point(troop.body.GetWorldCenter()[0] / globals.physics.scale_factor, troop.body.GetWorldCenter()[1] / globals.physics.scale_factor)
            explosionCenter = Point(self.body.GetWorldCenter()[0] / globals.physics.scale_factor, self.body.GetWorldCenter()[1] / globals.physics.scale_factor)
            distance = (troopCenter - explosionCenter).SquareLength()
            
            
            if(distance < explosionRange):
                troop.TakeDamage(explosionDamage * distance/explosionRange)
                
                impulseToApply = troopCenter - explosionCenter
                impulseToApply.Normalize()
                impulseToApply * Point(1, 1)
                impulse = box2d.b2Vec2(impulseToApply[0], impulseToApply[1])
                troop.locked_planet = None
                troop.body.ApplyImpulse(impulse, troop.body.GetWorldCenter())
            

    def getExplosionPosition(self):
        projectileCenter = Point(self.body.GetWorldCenter()[0] / globals.physics.scale_factor, self.body.GetWorldCenter()[1] / globals.physics.scale_factor)

        self.explosion_bl = projectileCenter - Point(50,50)
        self.explosion_tr = self.explosion_bl + Point(100,100)

    def Update(self):
        if self.TeleportUpdate():
            return

        if self.destroyMe:
            if globals.time >= self.destroy_at:
                if not self.explode():
                    self.explosion_quad.Delete()
                    self.Destroy()



