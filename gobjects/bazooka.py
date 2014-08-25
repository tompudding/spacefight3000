import weapon
from globals.types import Point
import globals

class Bazooka(weapon.Weapon):
    def __init__(self):
        self.fire_sound = globals.sounds.bazooka_fire
        self.right_texture = "red_bazooka_right.png"
        self.left_texture = "red_bazooka_left.png"
        self.projectile_texture_name = "zookshell.png"
        super(Bazooka, self).__init__(500, self.projectile_texture_name, 2000, True, 5)
        self.imageSize = Point(24, 8)
        self.projectileExplodes = True
        #picked utterly random numbers, we can sort that later.
