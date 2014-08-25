import gobject
import globals
from globals.types import Point
import Box2D as box2d
import drawing

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
        print "setup explosion"
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
        

    def Disable(self):
        self.quad.Disable()
        print 'disable!'

    def Enable(self):
        self.quad.Enable()
        print 'enable!'

    def destroyAfterTimeLimit(self):
        time_limit = 5000

        if not self.applyGravity:
            time_limit = 100
            self.applyGravity = True
        if(not self.destroyMe):
            self.destroyMe = True
            self.destroy_at = globals.time + time_limit
    
    def explode(self):
        if(self.explosive):
            if(self.exploding):
                required_explosion_tc = (globals.time - self.startOfExplosion) / self.explosion_frame_duration
                print "required_explosion_tc = ",required_explosion_tc
                if(self.last_explosion_tc != required_explosion_tc):
                    if(required_explosion_tc >= len(self.tc_explode)):
                        return False
                    else:
                        self.explosion_quad.SetTextureCoordinates(self.tc_explode[required_explosion_tc])
                        bl, tr = self.getExplosionPosition()
                        self.explosion_quad.SetVertices(bl, tr, drawing.constants.DrawLevels.ui)
                        self.last_explosion_tc = required_explosion_tc
                        return True
                    
            else:
                print "start exploding"
                self.startOfExplosion = globals.time
                self.exploding = True
                self.quad.Disable()
                bl, tr = self.getExplosionPosition()
                self.explosion_quad.SetVertices(bl, tr, drawing.constants.DrawLevels.ui)
                self.explosion_quad.Enable()
                return True
        else:
            return False
        
        return True
    
    def getExplosionPosition(self):
        projectileCenter = Point(self.body.GetWorldCenter()[0] / globals.physics.scale_factor, self.body.GetWorldCenter()[1] / globals.physics.scale_factor)
        bl = projectileCenter - Point(50,50)
        tr = bl + Point(100,100)
        return bl, tr

    def Update(self):
        if self.TeleportUpdate():
            return
        
        
        if self.destroyMe:
            if globals.time >= self.destroy_at:
                if(not self.explode()):
                    self.explosion_quad.Disable()
                    self.Destroy()
        

                
