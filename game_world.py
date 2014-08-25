import gobjects
import globals
from globals.types import Point
import math
import itertools

class GameWorld(object):
    last_level = 2
    troop_planet_distance = 20
    def __init__(self, level):
        self.planets = []
        self.goodies = []
        self.baddies = []
        self.portals = []
        self.projectiles = []
        self.level = level

        if level == 0:
            self.createLevel1()
        elif level == 1:
            self.createLevel2()
        elif level == 2:
            self.createLevel3()


        self.ResetAfterTurn()
        self.UpdateHUD()

    def createLevel1(self):
        #add planets
        self.planets.append(gobjects.planet.BluePlanet(Point(800,900), 200));
        self.planets.append(gobjects.planet.YellowPlanet(Point(1500,900), 200));

        #add portals
        self.portals.append(gobjects.Portal(self.planets[0],3*math.pi/2,self.planets[1],1.5))

        #add troops - goodies
        pos = self.planets[0].GetSurfacePoint(self.troop_planet_distance,5*math.pi/4)
        self.goodies.append(self.getTroop(1, pos, 1));
        pos = self.planets[0].GetSurfacePoint(self.troop_planet_distance,math.pi/2)
        self.goodies.append(self.getTroop(1, pos, 1));

        #baddies
        pos = self.planets[1].GetSurfacePoint(self.troop_planet_distance,0)
        self.baddies.append(gobjects.Troop(gobjects.Lazer, pos,0));
        pos = self.planets[1].GetSurfacePoint(self.troop_planet_distance,3*math.pi/2)
        self.baddies.append(gobjects.Troop(gobjects.Lazer, pos,0));

        #set view position
        globals.current_view.viewpos.Set(Point(500,500))

    def createLevel2(self):
        #add planets
        self.planets.append(gobjects.planet.BluePlanet(Point(1100,600), 200));
        self.planets.append(gobjects.planet.SpaceHattanDayPlanet(Point(2000,900), 250));

        #Lets have 6 portals on the planet, 2 pairs go to each other, the other two go to the other planet
        self.portals.append(gobjects.Portal(self.planets[0],0,self.planets[0],math.pi))
        self.portals.append(gobjects.Portal(self.planets[0],math.pi/3,self.planets[0],4*math.pi/3))
        self.portals.append(gobjects.Portal(self.planets[0],2*math.pi/3,self.planets[1],math.pi/3))
        self.portals.append(gobjects.Portal(self.planets[0],5*math.pi/3,self.planets[1],4*math.pi/3))

        #troops - goodies
        pos = self.planets[0].GetSurfacePoint(self.troop_planet_distance,math.pi/2)
        self.goodies.append(self.getTroop(2, pos, 1));

        #baddies
        pos = self.planets[1].GetSurfacePoint(self.troop_planet_distance,3*math.pi/2)
        self.baddies.append(gobjects.Troop(gobjects.Lazer, pos,0));

        #set view position
        globals.current_view.viewpos.Set(Point(810,340))

    def createLevel3(self):
        #cant jump high enough to move between worlds, need to use the gates

        #add planets
        self.planets.append(gobjects.planet.BluePlanet(Point(500,500), 300));
        self.planets.append(gobjects.planet.YellowPlanet(Point(3500,500), 300));
        self.planets.append(gobjects.planet.SpaceHattanDayPlanet(Point(500,3500), 300));
        self.planets.append(gobjects.planet.BunnyPlanet(Point(3500,3500), 300));

        #portals
        self.portals.append(gobjects.Portal(self.planets[0],0,self.planets[1],math.pi))
        self.portals.append(gobjects.Portal(self.planets[0],math.pi,self.planets[2],math.pi))
        self.portals.append(gobjects.Portal(self.planets[0],math.pi/2,self.planets[3],math.pi))

        self.portals.append(gobjects.Portal(self.planets[1],0,self.planets[2],math.pi/2))
        self.portals.append(gobjects.Portal(self.planets[1],math.pi/2,self.planets[3],math.pi/2))

        self.portals.append(gobjects.Portal(self.planets[2],0,self.planets[3],0))

        #troops - goodies
        pos = self.planets[0].GetSurfacePoint(self.troop_planet_distance,3*math.pi/2)
        self.goodies.append(self.getTroop(3, pos, 1));

        pos = self.planets[3].GetSurfacePoint(self.troop_planet_distance,3*math.pi/2)
        self.goodies.append(self.getTroop(3, pos, 1));

        #baddies
        pos = self.planets[1].GetSurfacePoint(self.troop_planet_distance,3*math.pi/2)
        self.baddies.append(gobjects.Troop(gobjects.Lazer, pos,0));

        pos = self.planets[2].GetSurfacePoint(self.troop_planet_distance,3*math.pi/2)
        self.baddies.append(gobjects.Troop(gobjects.Lazer, pos,0));

        #set view position
        globals.current_view.viewpos.Set(Point(810,340))

    def getTroop(self, num_weapons, pos, goodness):
        troop = gobjects.Troop(gobjects.Lazer, pos, goodness)

        if(num_weapons >= 2):
            troop.add_weapon(gobjects.Bazooka)

        if(num_weapons >= 3):
            troop.add_weapon(gobjects.Grenade)

        return troop


    def update(self):
        for item in itertools.chain(self.goodies,self.baddies,self.portals, self.projectiles):
            item.Update()

        self.ReapFallenHeroes()

        self.UpdateHUD()

    def ReapFallenHeroes(self):
        self.goodies = [t for t in self.goodies if not t.dead]
        self.baddies = [t for t in self.baddies if not t.dead]
        self.projectiles = [p for p in self.projectiles if not p.dead]

    def Destroy(self):
        for item in itertools.chain(self.goodies,self.baddies,self.portals,self.planets,self.projectiles):
            item.Destroy()
        self.planets = []

    def UpdateHUD(self):
        if hasattr(globals.current_view.mode, "selected_troop") and globals.current_view.mode.selected_troop:
            move_to_display = globals.max_movement - round(globals.current_view.mode.selected_troop.amount_moved)
            if move_to_display < 0:
                move_to_display = 0
            globals.current_view.hud.SetLevelBar("Us: {0}    Them: {1}    Level {2}    Movement Left {3}".format(len(self.goodies), len(self.baddies), self.level+1, move_to_display))

    def ResetAfterTurn(self):
        self.goodies_to_play = list(self.goodies)
        self.badies_to_play = list(self.baddies)
        for item in itertools.chain(self.goodies,self.baddies):
            item.amount_moved = 0
            item.fired = False

    def NextGoodieToPlay(self):
        self.ReapFallenHeroes()
        if len(self.goodies_to_play) > 0:
            return self.goodies_to_play.pop()
        elif len(self.badies_to_play) > 0:
            return None
        elif len(self.goodies) > 0:
            self.ResetAfterTurn()
            return self.goodies_to_play.pop()
        else:
            return None

    def NextBadieToPlay(self):
        self.ReapFallenHeroes()
        if len(self.badies_to_play) > 0:
            return self.badies_to_play.pop()
        else:
            return None
