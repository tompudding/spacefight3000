import globals
import projectile
import Box2D as box2d
import cmath
import math

class Weapon(object):
    
    def __init__(self, maxDamage, projectileImage, power_modifier, limitedAmmo, currentAmmo):
        self.maxDamage = maxDamage
        self.projectileImage = projectileImage
        self.limitedAmmo = limitedAmmo
        self.currentAmmo = currentAmmo
        self.power_modifier = power_modifier
        self.imageSize = None

        #self.tc = globals.atlas.TextureSpriteCoords(self.projectileImage)
        #super(Weapon,self).__init__(physics,bl,tr,self.tc)
        
    def FireAtTarget(self, angle, weapon_force, bl, parentTroop):
        #need to use the angle and force to determine where the projectile is headed. 
        if(self.limitedAmmo):
            self.currentAmmo -= 1
                    
        #work out force to apply to the projectile  
        update_distance_rect = cmath.rect(weapon_force * self.power_modifier, angle)
        x = update_distance_rect.real
        y = update_distance_rect.imag
        
        projectileAngle = angle
            
        force = box2d.b2Vec2(x,y)
        return projectile.Projectile(self.projectileImage, bl, self.imageSize, projectileAngle, force, self.maxDamage, parentTroop)
    
    def isOutOfAmmo(self):
        if(self.limitedAmmo and self.currentAmmo <= 0):
            return True
        
        return False
    
    
    
    
    
    
