import globals
from globals.types import Point
import Box2D as box2d
import cmath

class AI(object):

    def NextMove(self, troop, enemies):
        nearest_enemy, distance_squared = self.GetNearestEnemy(troop, enemies)


        if distance_squared < 40 and not troop.fired:
            vect_diff = nearest_enemy.body.position - troop.body.position
            troop.ActuallySetWeaponVector(vect_diff.x, vect_diff.y)
            troop.SetWeaponPower(1)
            troop.fireWeapon()
            troop.fired = True
            return True

        nearest_enemy, distance_squared = self.GetNearestOnPlanetEnemy(troop, enemies)

        if not nearest_enemy is None:
            my_difference = troop.locked_planet.body.position - troop.body.position
            his_difference = troop.locked_planet.body.position - nearest_enemy.body.position
           
            distance,angle1 = cmath.polar(complex(my_difference.x, my_difference.y))
            distance,angle2 = cmath.polar(complex(his_difference.x, his_difference.y))

            if angle1 > angle2:
                troop.move_direction = Point(8.0,0.0)
            else:
                troop.move_direction = Point(-8.0,0.0)

            return True
        else:
            return False

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

