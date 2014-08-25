import globals
import Box2D as box2d
import cmath

class AI(object):

    def NextMove(self, troop, enemies):
        nearest_enemy = self.GetNearestEnemy(troop, enemies)

        if not nearest_enemy is None:
            my_difference = troop.locked_planet.body.position - troop.body.position
            his_difference = troop.locked_planet.body.position - nearest_enemy.body.position

           
            distance,angle1 = cmath.polar(complex(my_difference.x, my_difference.y))
            distance,angle2 = cmath.polar(complex(his_difference.x, his_difference.y))

            print angle1, angle2

            if angle1 > angle2:
                return -8.0
            else:
                return 8.0

    def GetNearestEnemy(self, troop, enemies):
        if troop.locked_planet == None:
            return []
       
        nearest_enemy = None
        distance = 10000000000000000
        location = troop.body.position
        for enemy in enemies:
            if enemy.locked_planet == troop.locked_planet:
                enemy_vect = box2d.b2Vec2(enemy.body.position)
                enemy_vect.sub_vector(location)
                new_distance = enemy_vect.LengthSquared() 
                if distance > new_distance:
                    distance = new_distance
                    nearest_enemy = enemy

        return nearest_enemy
            


