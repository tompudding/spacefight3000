import gobjects
from globals.types import Point

class GameWorld(object):
    def __init__(self):
        self.planets = []
        self.planets.append(gobjects.BluePlanet(Point(100,200), Point(500,600)));
        self.planets.append(gobjects.YellowPlanet(Point(800,200), Point(1200,600)));

        self.goodies = []
        self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,100)));
        self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(100,400)));
        
        self.baddies = []
        self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,100)));
        self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,400)));
