import weapon

class Bazooka(weapon.Weapon):
    
    def __init__(self, physics, bl, tr):
        self.projectile_texture_name = "bazookaTroop.png" 
        super(Bazooka, self).__init__(50, self.projectile_texture_name, physics, bl, tr)
        #picked utterly random numbers, we can sort that later. 