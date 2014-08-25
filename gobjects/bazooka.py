import weapon
from globals.types import Point
import globals

class Bazooka(weapon.Weapon):
    item_name_left_good = item_name_left_bad = 'red_bazooka_left.png'
    item_name_right_good = item_name_right_bad = 'red_bazooka_right.png'
    def __init__(self):
        self.fire_sound = globals.sounds.bazooka_fire
        self.projectile_texture_name = "zookshell.png"
        super(Bazooka, self).__init__(300, self.projectile_texture_name, 2000, True, 5)
        self.imageSize = Point(24, 8)
        self.projectileExplodes = True
        #picked utterly random numbers, we can sort that later.
