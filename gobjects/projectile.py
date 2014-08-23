import gobject

class projectile(gobject.gobject):
    
    def __init__(self, image, mass):
        self.image = image
        self.mass = mass
        self.isBullet = True
