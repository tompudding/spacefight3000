import gobjects
import globals
from globals.types import Point

import itertools
class GameWorld(object):
    last_level = 1
    def __init__(self, level):
        self.planets = []
        self.goodies = []
        self.baddies = []
        self.portals = []
        self.level = level
        print level
        globals.current_view.hud.SetLevelBar("Level " + str(level+1))

        if level == 0:
            self.planets.append(gobjects.BluePlanet(Point(300,400), 200));
            self.planets.append(gobjects.YellowPlanet(Point(1000,400), 200));
            self.portals.append(gobjects.Portal(self.planets[0],2,self.planets[1],1.5))
            self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,100)));
            self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,400)));
            self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,100)));
            self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,400)));
        elif level == 1:
            self.planets.append(gobjects.BluePlanet(Point(600,600), 200));
            self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,400)));
            self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,100)));
        
        self.projectiles = []

    def update(self):
        self.goodies = [t for t in self.goodies if not t.dead]
        self.baddies = [t for t in self.baddies if not t.dead]
        self.projectiles = [p for p in self.projectiles if not p.dead]

        for item in itertools.chain(self.goodies,self.baddies,self.portals, self.projectiles):
            item.Update()

    def Destroy(self):
        for item in itertools.chain(self.goodies,self.baddies,self.portals,self.planets):
            item.Destroy()

        


