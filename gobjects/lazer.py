import weapon
from globals.types import Point

class Lazer(weapon.Weapon):
    #lazers should probably be a limited shot weapon, since gravity wont affect them in the same way as other weapons. Maybe do a touch more damage
    #than the default bazooka as well. 
    
    def __init__(self):
        self.projectile_texture_name = "tempRound.png" 
        super(Lazer, self).__init__(75, self.projectile_texture_name, True, 5)
        #picked utterly random numbers, we can sort that later. 