import weapon
from globals.types import Point

class Lazer(weapon.Weapon):
    #lazers should probably be a limited shot weapon, since gravity wont affect them in the same way as other weapons. Maybe do a touch more damage
    #than the default bazooka as well. 
    
    def __init__(self):
        self.projectile_texture_name = "laser.png" 
        super(Lazer, self).__init__(75, self.projectile_texture_name, 2000, True, 5)
        self.imageSize = Point(24,4)
        #picked utterly random numbers, we can sort that later. 
    
    def FireAtTarget(self, angle, weapon_force, bl, parentTroop):
        projectile = super(Lazer, self).FireAtTarget(angle,weapon_force,bl,parentTroop)
        projectile.dontApplyGravity()
        return projectile