import gobject
import globals
import projectile

class Weapon(gobject.BoxGobject):
    
    def __init__(self, maxDamage, projectileImage, limitedAmmo, currentAmmo, physics, bl, tr):
        self.maxDamage = maxDamage
        self.projectileImage = projectileImage
        self.limitedAmmo = limitedAmmo
        self.currentAmmo = currentAmmo
        
        self.tc = globals.atlas.TextureSpriteCoords(self.projectileImage)
        super(Weapon,self).__init__(physics,bl,tr,self.tc)
        
    def FireAtTarget(self, angle, force):
        #need to use the angle and force to determine where the projectile is headed. 
        print "open fire... alll weapons, angle, force = ", angle, force
        
        if(self.limitedAmmo):
            self.currentAmmo -= 1
        
        return projectile.Projectile(self.projectileImage)
    
    def isOutOfAmmo(self):
        if(self.limitedAmmo and self.currentAmmo <= 0):
            return True
        
        return False
    
    
    
    
    
    
