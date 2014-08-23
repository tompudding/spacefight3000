import gobject

class Projectile(gobject.Gobject):
    
    def __init__(self, image, mass):
        self.image = image
        self.mass = mass
        self.isBullet = True
