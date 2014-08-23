from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import Box2D as box2d
import modes
import random

def b2Vec_indexer(self,index):
    if index == 0:
        return self.x
    elif index == 1:
        return self.y
def b2Vec_setter(self,index,val):
    if index == 0:
        self.x =val
    elif index == 1:
        self.y = val
box2d.b2Vec2.__getitem__ = b2Vec_indexer
box2d.b2Vec2.__setitem__ = b2Vec_setter


class MyContactListener(box2d.b2ContactListener):
    physics = None
    def __init__(self): 
        super(MyContactListener, self).__init__() 
    def Add(self, point):
        """Handle add point"""
        if not self.physics:
            return
        cp          = fwContactPoint()
        cp.shape1   = point.shape1
        cp.shape2   = point.shape2
        cp.position = point.position.copy()
        cp.normal   = point.normal.copy()
        cp.id       = point.id
        #globals.sounds.thud.play()
        self.physics.contacts.append(cp)
        
    def Persist(self, point):
        """Handle persist point"""

        pass
    def Remove(self, point):
        """Handle remove point"""
        pass
    def Result(self, point):
        """Handle results"""
        pass

class Physics(object):
    scale_factor = 0.05
    def __init__(self,parent):
        self.contact_listener = MyContactListener()
        self.contact_listener.physics = self
        #self.contact_filter = MyContactFilter()
        #self.contact_filter.physics = self
        self.parent = parent
        self.worldAABB=box2d.b2AABB()
        self.worldAABB.lowerBound = (-100,-globals.screen.y-100)
        self.worldAABB.upperBound = (100 + self.parent.absolute.size.x*self.scale_factor,100 + self.parent.absolute.size.y*self.scale_factor + 100)
        self.gravity = (0, 0)
        self.doSleep = True
        self.world = box2d.b2World(self.worldAABB, self.gravity, self.doSleep)
        self.world.SetContactListener(self.contact_listener)
        #self.world.SetContactFilter(self.contact_filter)
        self.timeStep = 1.0 / 60.0
        self.velocityIterations = 10
        self.positionIterations = 8
        self.max_zoom = 2.0
        self.objects = []
    
    def AddObject(self,obj):
        self.objects.append(obj)

    def Step(self):
        self.contacts = []
        self.world.Step(self.timeStep, self.velocityIterations, self.positionIterations)
        
        for obj in self.objects:
            obj.PhysUpdate()

    def GetObjectAtPoint(self,pos):
        aabb = box2d.b2AABB()
        phys_pos = pos*self.scale_factor

        aabb.lowerBound.Set(phys_pos.x-0.1,phys_pos.y-0.1)
        aabb.upperBound.Set(phys_pos.x+0.1,phys_pos.y+0.1)
        (count,shapes) = self.world.Query(aabb,10)
        for shape in shapes:
            trans = box2d.b2XForm()
            trans.SetIdentity()
            p = phys_pos - Point(*shape.GetBody().position)
            if shape.TestPoint(trans,tuple(p)):
                return shape.userData
        return None


class GameView(ui.RootElement):
    def __init__(self):
        self.atlas = globals.atlas = drawing.texture.TextureAtlas('tiles_atlas_0.png','tiles_atlas.txt')
        self.game_over = False
        #pygame.mixer.music.load('music.ogg')
        #self.music_playing = False
        super(GameView,self).__init__(Point(0,0),globals.screen)
        self.physics = Physics(self)
        #skip titles for development of the main game
        self.mode = modes.Titles(self)
        #self.mode = modes.LevelOne(self)
        self.StartMusic()

    def StartMusic(self):
        pass
        #pygame.mixer.music.play(-1)
        #self.music_playing = True

    def Draw(self):
        drawing.ResetState()
        drawing.DrawNoTexture(globals.line_buffer)
        drawing.DrawNoTexture(globals.colour_tiles)
        drawing.DrawAll(globals.nonstatic_text_buffer,globals.text_manager.atlas.texture.texture)
        
    def Update(self):
        if self.mode:
            self.mode.Update()

        if self.game_over:
            return
            
    def GameOver(self):
        self.game_over = True
        self.mode = modes.GameOver(self)
        
    def KeyDown(self,key):
        self.mode.KeyDown(key)

    def KeyUp(self,key):
        if key == pygame.K_DELETE:
            if self.music_playing:
                self.music_playing = False
                pygame.mixer.music.set_volume(0)
            else:
                self.music_playing = True
                pygame.mixer.music.set_volume(1)
        self.mode.KeyUp(key)

