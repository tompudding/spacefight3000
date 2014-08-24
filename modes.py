from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
import gobjects
from globals.types import Point
import sys
import gobjects.bazooka
from game_world import GameWorld

class Mode(object):
    """ Abstract base class to represent game modes """
    def __init__(self,parent):
        self.parent = parent
    
    def KeyDown(self,key):
        pass
    
    def KeyUp(self,key):
        pass
    def MouseMotion(self,pos,rel):
        pass

    def MouseButtonDown(self,pos,button):
        return

    def MouseButtonUp(self,pos,button):
        return

    def Update(self,t):
        pass

class TitleStages(object):
    STARTED  = 0
    COMPLETE = 1
    TEXT     = 2
    SCROLL   = 3
    WAIT     = 4
    PLAYING = 5


class Titles(Mode):
    blurb = "SPACE FIGHT 3000"
    def __init__(self,parent):
        self.parent          = parent
        self.start           = pygame.time.get_ticks()
        self.stage           = TitleStages.STARTED
        self.handlers        = {TitleStages.STARTED  : self.Startup,
                                TitleStages.COMPLETE : self.Complete}
        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(globals.screen)
        self.blurb_text = ui.TextBox(parent = self.parent,
                                     bl     = bl         ,
                                     tr     = tr         ,
                                     text   = self.blurb ,
                                     textType = drawing.texture.TextTypes.GRID_RELATIVE,
                                     colour = (1,1,1,1),
                                     scale  = 8)
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      buffer = globals.ui_buffer,
                                      colour = (0,0,0,0))
        self.backdrop.Enable()

    def KeyDown(self,key):
        self.Complete()
        self.stage = TitleStages.PLAYING

    def Update(self):        
        self.elapsed = globals.time - self.start
        self.stage = self.handlers[self.stage]()

    def Complete(self):
        self.backdrop.Delete()
        self.blurb_text.Delete()
        self.parent.mode = Playing(self.parent)

    def Startup(self):
        return TitleStages.STARTED

class GameMode(Mode):
    def __init__(self,parent):
        self.parent = parent
        

class GameOver(Mode):
    blurb = "GAME OVER"
    def __init__(self,parent):
        self.parent          = parent
        self.blurb           = self.blurb
        self.blurb_text      = None
        self.handlers        = {TitleStages.TEXT    : self.TextDraw,
                                TitleStages.SCROLL  : self.Wait,
                                TitleStages.WAIT    : self.Wait}
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      buffer = globals.backdrop_buffer,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      colour = (0,0,0,0.6))
        
        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(globals.screen)
        self.blurb_text = ui.TextBox(parent = globals.screen_root,
                                     bl     = bl         ,
                                     tr     = tr         ,
                                     text   = self.blurb ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     scale  = 3)

        self.start = None
        self.blurb_text.EnableChars(0)
        self.stage = TitleStages.TEXT
        self.played_sound = False
        self.skipped_text = False
        self.letter_duration = 20
        self.continued = False
        #pygame.mixer.music.load('end_fail.mp3')
        #pygame.mixer.music.play(-1)

    def Update(self):
        if self.start == None:
            self.start = globals.time
        self.elapsed = globals.time - self.start
        self.stage = self.handlers[self.stage](globals.time)
        if self.stage == TitleStages.COMPLETE:
            raise sys.exit('Come again soon!')

    def Wait(self,t):
        return self.stage

    def SkipText(self):
        if self.blurb_text:
            self.skipped_text = True
            self.blurb_text.EnableChars()

    def TextDraw(self,t):
        if not self.skipped_text:
            if self.elapsed < (len(self.blurb_text.text)*self.letter_duration) + 2000:
                num_enabled = int(self.elapsed/self.letter_duration)
                self.blurb_text.EnableChars(num_enabled)
            else:
                self.skipped_text = True
        elif self.continued:
            return TitleStages.COMPLETE
        return TitleStages.TEXT


    def KeyDown(self,key):
        if not self.skipped_text:
            self.SkipText()
        else:
            self.continued = True

    def MouseButtonDown(self,pos,button):
        self.KeyDown(0)
        return False,False

class PlayingStages:
    PLAYERS_GO = 0
    COMPUTERS_GO = 1

class Playing(Mode):
    speed = 8
    class KeyFlags:
        LEFT  = 1
        RIGHT = 2
        UP    = 4
        DOWN  = 8

    direction_amounts = {KeyFlags.LEFT  : Point(-0.01*speed, 0.00),
                         KeyFlags.RIGHT : Point( 0.01*speed, 0.00),
                         KeyFlags.UP    : Point( 0.00, 0.01*speed),
                         KeyFlags.DOWN  : Point( 0.00,-0.01*speed)}

    keyflags = {pygame.K_LEFT  : KeyFlags.LEFT,
                pygame.K_RIGHT : KeyFlags.RIGHT,
                pygame.K_UP    : KeyFlags.UP,
                pygame.K_DOWN  : KeyFlags.DOWN}

    def __init__(self,parent):
        self.parent          = parent
        self.start           = pygame.time.get_ticks()
        self.stage           = PlayingStages.PLAYERS_GO
        self.handlers        = {PlayingStages.PLAYERS_GO : self.PlayerPlay,
                                PlayingStages.COMPUTERS_GO : self.ComputerPlay}
        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(globals.screen)
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      buffer = globals.ui_buffer,
                                      colour = (0,0,0,0))
        self.backdrop.Enable()



        self.selectedGoodie = None
        self.keydownmap = 0

        self.parent.game_world = GameWorld(self.parent.physics)

    def KeyDown(self,key):
        if key in self.keyflags:
            self.keydownmap |= self.keyflags[key]
            if self.selectedGoodie:
                self.selectedGoodie.move_direction += self.direction_amounts[self.keyflags[key]]
        elif key == pygame.K_SPACE and not self.selectedGoodie == None:
            self.selectedGoodie.fireWeapon()
        if key == pygame.K_n:
            self.StartComputersGo()

    def KeyUp(self,key):
        if key in self.direction_amounts and (self.keydownmap & self.keyflags[key]):
            self.keydownmap &= (~self.keyflags[key])
            if self.selectedGoodie:
                self.selectedGoodie.move_direction += self.direction_amounts[self.keyflags[key]]
    
    def MouseButtonDown(self,pos,button):
        objectUnderPoint = self.parent.physics.GetObjectAtPoint(pos)
        if not objectUnderPoint:
            if self.selectedGoodie:
                self.selectedGoodie.unselect()
                self.selectedGoodie = None
        
        if objectUnderPoint is not self.selectedGoodie and objectUnderPoint in self.parent.game_world.goodies:
            objectUnderPoint.select()
            self.selectedGoodie = objectUnderPoint

    def Update(self):        
        self.elapsed = globals.time - self.start
        self.stage = self.handlers[self.stage](globals.time)

    def StartComputersGo(self):
        self.selectedGoodie = None
        self.stage = PlayingStages.COMPUTERS_GO
        self.computers_go_time = 0;

    def PlayerPlay(self, ticks):
        return PlayingStages.PLAYERS_GO

    def ComputerPlay(self, ticks):
        if len(self.parent.game_world.baddies) == 0:
            raise sys.exit("player won")
        elif self.computers_go_time == 0:
            self.computers_go_time = ticks
            self.current_baddie_index = 0
            self.parent.game_world.baddies[0].select()
        elif ticks - self.computers_go_time > 500:
            self.parent.game_world.baddies[self.current_baddie_index].fireWeapon()
            self.computers_go_time = ticks
            self.parent.game_world.baddies[self.current_baddie_index].unselect()
            self.current_baddie_index += 1
            if self.current_baddie_index == len(self.parent.game_world.baddies):
                return PlayingStages.PLAYERS_GO
            else:
                self.parent.game_world.baddies[self.current_baddie_index].select()
        return PlayingStages.COMPUTERS_GO
