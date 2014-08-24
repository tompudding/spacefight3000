import weapon
from globals.types import Point

class Bazooka(weapon.Weapon):
    
    def __init__(self):
        self.right_texture = "red_bazooka_right.png"
        self.left_texture = "red_bazooka_left.png"
        self.projectile_texture_name = "tempRound.png" 
        super(Bazooka, self).__init__(500, self.projectile_texture_name, 2000, False, 1)
        #picked utterly random numbers, we can sort that later. 
