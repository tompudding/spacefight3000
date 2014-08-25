import weapon
from globals.types import Point
import globals

class Grenade(weapon.Weapon):
    #Timed explosive, same damage as bazooka, limited ammo?

    def __init__(self):
        self.projectile_texture_name = "grenade.png"
        self.fire_sound = globals.sounds.grenade_fire
        super(Grenade, self).__init__(50, self.projectile_texture_name, 4000, True, 3)
        self.imageSize = Point(25, 32)
        self.projectileExplodes = True

    def FireAtTarget(self, angle, weapon_force, bl, parentTroop):
        projectile = super(Grenade, self).FireAtTarget(angle,weapon_force,bl,parentTroop)
        projectile.destroyAfterTimeLimit(3000)
        return projectile
