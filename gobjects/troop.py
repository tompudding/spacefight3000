import gobject
from weapon import weapon

class troop(gobject.gobject):
    
    def __init__(self, initialWeapon):
        self.currentWeapon = initialWeapon
    
    def changeWeapon(self, newWeapon):
        self.currentWeapon = newWeapon 
         
