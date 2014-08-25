import weapon
from globals.types import Point

class Grenade(weapon.Weapon):
    #Timed explosive, same damage as bazooka, limited ammo? 
    
    def __init__(self):
        self.projectile_texture_name = "grenade.png" 
        super(Grenade, self).__init__(50, self.projectile_texture_name, 4000, True, 3)
        self.imageSize = Point(25, 32)