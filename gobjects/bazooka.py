import weapon

class bazooka(weapon.Weapon):
    
    def __init__(self):
        self.projectile_texture_name = "" 
        super(weapon.Weapon, self).__init__(50, 5, self.projectile_texture_name)
        #picked utterly random numbers, we can sort that later. 