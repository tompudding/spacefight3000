import gobject
from projectile import projectile

class weapon(gobject.gobject):
    
    def __init__(self, maxDamage, projectileMass, projectileImage):
        self.maxDamage = maxDamage
        self.projectileMass = projectileMass
        self.projectileImage = projectileImage
        
    def FireAtTarget(self, angle, force):
        #need to use the angle and force to determine where the projectile is headed. 
        return projectile(self.projectileImage, self.projectileMass)
    
    
    
    