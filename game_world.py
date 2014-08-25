import gobjects
import globals
from globals.types import Point
import math

import itertools
class GameWorld(object):
    last_level = 1
    def __init__(self, level):
        self.planets = []
        self.goodies = []
        self.baddies = []
        self.portals = []
        self.projectiles = []
        self.level = level


        if level == 0:
            self.planets.append(gobjects.BluePlanet(Point(800,900), 200));
            self.planets.append(gobjects.YellowPlanet(Point(1500,900), 200));
            self.portals.append(gobjects.Portal(self.planets[0],3*math.pi/2,self.planets[1],1.5))
            
            wellEquiptTroop = gobjects.Troop(gobjects.Bazooka, Point(600,600),1)
            wellEquiptTroop.add_weapon(gobjects.Lazer)
            self.goodies.append(wellEquiptTroop);
            self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(600,900),1));
            self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1500,600),0));
            self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1500,900),0));
        elif level == 1:
            self.planets.append(gobjects.BluePlanet(Point(1100,600), 200));
            self.goodies.append(gobjects.Troop(gobjects.Bazooka, Point(1000,700),1));
            self.baddies.append(gobjects.Troop(gobjects.Bazooka, Point(1500,600),0));



        self.ResetAfterTurn()
        self.UpdateHUD()
        globals.current_view.viewpos.Set(Point(500,500))
    def update(self):
        for item in itertools.chain(self.goodies,self.baddies,self.portals, self.projectiles):
            item.Update()

        self.goodies = [t for t in self.goodies if not t.dead]
        self.baddies = [t for t in self.baddies if not t.dead]
        self.projectiles = [p for p in self.projectiles if not p.dead]

        self.UpdateHUD()

    def Destroy(self):
        for item in itertools.chain(self.goodies,self.baddies,self.portals,self.planets,self.projectiles):
            item.Destroy()

    def UpdateHUD(self):
        if hasattr(globals.current_view.mode, "selectedGoodie"):
            move_to_display = globals.max_movement - round(globals.current_view.mode.selectedGoodie.amount_moved)
            if move_to_display < 0:
                move_to_display = 0
            globals.current_view.hud.SetLevelBar("Us: {0}    Them: {1}    Level {2}    Movement Left {3}".format(len(self.goodies), len(self.baddies), self.level+1, move_to_display))

    def ResetAfterTurn(self):
        self.goodies_to_play = list(self.goodies)
        self.badies_to_play = list(self.baddies)
        for item in itertools.chain(self.goodies,self.baddies):
            item.amount_moved = 0

    def NextGoodieToPlay(self):
        if len(self.goodies_to_play) > 0:
            return self.goodies_to_play.pop()
        elif len(self.badies_to_play) > 0:
            return None
        else:
            self.ResetAfterTurn()
            return self.goodies_to_play.pop()

    def NextBadieToPlay(self):
        if len(self.badies_to_play) > 0:
            return self.badies_to_play.pop()
        else:
            return None
