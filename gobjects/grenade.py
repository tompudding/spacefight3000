import weapon
from globals.types import Point

class Grenade(weapon.Weapon):
    #Timed explosive, same damage as bazooka, limited ammo? 
    
    def __init__(self):
        self.projectile_texture_name = "tempRound.png" 
        super(Grenade, self).__init__(50, self.projectile_texture_name, True, 3)
        #picked utterly random numbers, we can sort that later. 