import weapon
from globals.types import Point

class Bazooka(weapon.Weapon):
    
    def __init__(self):
        self.projectile_texture_name = "tempRound.png" 
        super(Bazooka, self).__init__(50, self.projectile_texture_name, 2000, False, 1)
        #picked utterly random numbers, we can sort that later. 