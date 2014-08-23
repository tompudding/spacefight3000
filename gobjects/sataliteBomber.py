import weapon
from globals.types import Point

class SataliteBomber(weapon.Weapon):
    #if the player hits a planet correctly, orbits dropping a number of bombs, very limited in number, high damage. 
    
    def __init__(self, physics, bl, tr):
        self.projectile_texture_name = "tempRound.png" 
        super(SataliteBomber, self).__init__(100, self.projectile_texture_name, True, 1, physics, bl, Point( (bl[0] + 5), (bl[1] + 5) ))
        #picked utterly random numbers, we can sort that later. 