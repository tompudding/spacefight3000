import gobject
import globals
import projectile

class Weapon(gobject.Gobject):
    
    def __init__(self, maxDamage, projectileImage, physics, bl, tr):
        self.maxDamage = maxDamage
        self.projectileImage = projectileImage
        
        self.tc = globals.atlas.TextureSpriteCoords(self.projectileImage)
        super(Weapon,self).__init__(physics,bl,tr,self.tc)
        
    def FireAtTarget(self, angle, force):
        #need to use the angle and force to determine where the projectile is headed. 
        return projectile.Projectile(self.projectileImage, self.projectileMass)
    
    
    
    