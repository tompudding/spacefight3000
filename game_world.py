import gobjects
from globals.types import Point

import itertools
class GameWorld(object):
    def __init__(self):
        self.planets = []

        self.planets.append(gobjects.BluePlanet(Point(300,400), 200));
        self.planets.append(gobjects.YellowPlanet(Point(1000,400), 200));
        self.portal = gobjects.Portal(self.planets[0],0.3,self.planets[1],1.5)

        self.goodies = []
        self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,100)));
        self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,400)));

        self.baddies = []
        self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,100)));
        self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,400)));

    def update(self):
        self.goodies = [t for t in self.goodies if not t.dead]
        self.baddies = [t for t in self.baddies if not t.dead]
