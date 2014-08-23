import gobject

class Projectile(gobject.Gobject):
    
    def __init__(self, image):
        self.image = image
        self.isBullet = True
