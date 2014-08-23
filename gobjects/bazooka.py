import weapon
from globals.types import Point

class Bazooka(weapon.Weapon):
    
    def __init__(self, physics, bl, tr):
        self.projectile_texture_name = "tempRound.png" 
        super(Bazooka, self).__init__(50, self.projectile_texture_name, physics, bl, Point( (bl[0] + 5), (bl[1] + 5) ))
        #picked utterly random numbers, we can sort that later. 