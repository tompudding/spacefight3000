import globals
from globals.types import Point
import Box2D as box2d
import cmath
import math

class AI(object):

    def __init__(self):
        self.idle_since = 0
        self.waiting = None

    def NextMove(self, troop, enemies):
        nearest_enemy, distance_squared = self.GetNearestEnemy(troop, enemies)
        if not troop.locked_planet:
            return True

        if nearest_enemy is None:
            return False

        # if we're on the same planet, either walk towards them or fire
        if nearest_enemy.locked_planet == troop.locked_planet:
            if distance_squared < 40 and not troop.fired:
                self.FireAt(troop, nearest_enemy)
                return True
            elif not troop.fired:
                self.WalkAt(troop, nearest_enemy)
                return True
            else:
                return False

        if not nearest_enemy.locked_planet == None and not troop.locked_planet == None:
            angle = self.GetAngle(troop.locked_planet.body, troop.body, nearest_enemy.locked_planet.body)
            if abs(angle) < math.pi / 6:
                if not troop.jumped:
                    print 'jump!'
                    troop.jump()
                else:
                    return False
            else:
                self.WalkAt(troop, troop.locked_planet)

            return True

        if troop.locked_planet == None:
            return True
        return False

    def FireAt(self, troop, target):
        vect_diff = target.body.position - troop.body.position
        troop.ActuallySetWeaponVector(vect_diff.x, vect_diff.y)
        troop.SetWeaponPower(1)
        globals.current_view.game_world.projectiles.append(troop.fireWeapon())
        troop.fired = True

    def WalkAt(self, troop, target):
        if self.GetAngle(troop.locked_planet.body, troop.body, target.body) > 0:
            troop.move_direction = Point(8.0,0.0)
        else:
            troop.move_direction = Point(-8.0,0.0)

    def WalkAway(self, troop, target):
        if self.GetAngle(troop.locked_planet.body, troop.body, target.body) > 0:
            troop.move_direction = Point(-8.0,0.0)
        else:
            troop.move_direction = Point(8.0,0.0)

    def GetAngle(self, origin_body, body1, body2):
        my_difference = origin_body.position - body1.position
        his_difference = origin_body.position - body2.position

        distance,angle1 = cmath.polar(complex(my_difference.x, my_difference.y))
        distance,angle2 = cmath.polar(complex(his_difference.x, his_difference.y))

        return angle1 - angle2


    def GetNearestEnemy(self, troop, enemies):
        distance = 10000000000000000
        if troop.locked_planet == None:
            return None, distance

        nearest_enemy = None

        location = troop.body.position
        for enemy in enemies:
            enemy_vect = box2d.b2Vec2(enemy.body.position)
            enemy_vect.sub_vector(location)
            new_distance = enemy_vect.LengthSquared()
            if distance > new_distance:
                distance = new_distance
                nearest_enemy = enemy

        return nearest_enemy, distance


    def GetNearestOnPlanetEnemy(self, troop, enemies):
        distance = 10000000000000000
        if troop.locked_planet == None:
            return None, distance

        nearest_enemy = None

        location = troop.body.position
        for enemy in enemies:
            if enemy.locked_planet == troop.locked_planet:
                enemy_vect = box2d.b2Vec2(enemy.body.position)
                enemy_vect.sub_vector(location)
                new_distance = enemy_vect.LengthSquared()
                if distance > new_distance:
                    distance = new_distance
                    nearest_enemy = enemy

        return nearest_enemy, distance

