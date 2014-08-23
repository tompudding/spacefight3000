import gobject
import projectile

class Weapon(gobject.Gobject):
    
    def __init__(self, maxDamage, projectileMass, projectileImage):
        self.maxDamage = maxDamage
        self.projectileMass = projectileMass
        self.projectileImage = projectileImage
        
    def FireAtTarget(self, angle, force):
        #need to use the angle and force to determine where the projectile is headed. 
        return projectile.Projectile(self.projectileImage, self.projectileMass)
    
    
    
    