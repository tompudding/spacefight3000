from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
import gobjects
from globals.types import Point
import sys
import gobjects.bazooka
import itertools
import game_world
from ai import AI

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
        self.Complete()
        self.elapsed = globals.time - self.start
        self.stage = self.handlers[self.stage]()

    def Complete(self):
        self.backdrop.Delete()
        self.blurb_text.Delete()
        self.parent.game_world = game_world.GameWorld(0)
        self.parent.mode = PlayerPlaying(self.parent)

    def Startup(self):
        return TitleStages.STARTED


class GameMode(Mode):
    def __init__(self,parent):
        self.parent = parent


class GameOver(Mode):
    def __init__(self,parent, won):
        self.parent          = parent
        if won:
            globals.sounds.level_win.play()
            self.blurb           = "You are winner!! !"
        else:
            globals.sounds.level_lose.play()
            self.blurb           = "You am lost! !!"

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
                                     bl     = Point(0,0)        ,
                                     tr     = Point(1.0,0.6)       ,
                                     text   = self.blurb ,
                                     textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                     alignment = drawing.texture.TextAlignments.CENTRE,
                                     scale  = 24)

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

class PlayerPlaying(Mode):
    speed = 8
    class KeyFlags:
        LEFT  = 1
        RIGHT = 2
        UP    = 4
        DOWN  = 8
        SHIFT = 16

    direction_amounts = {KeyFlags.LEFT  : Point(-speed, 0.00),
                         KeyFlags.RIGHT : Point( speed, 0.00),
                         KeyFlags.UP    : Point( 0.00, speed),
                         KeyFlags.DOWN  : Point( 0.00, speed),
                         KeyFlags.SHIFT : Point (0.00, 0.00) }

    keyflags = {pygame.K_LEFT  : KeyFlags.LEFT,
                pygame.K_RIGHT : KeyFlags.RIGHT,
                pygame.K_a  : KeyFlags.LEFT,
                pygame.K_d : KeyFlags.RIGHT,
                pygame.K_LSHIFT : KeyFlags.SHIFT,
                pygame.K_RSHIFT : KeyFlags.SHIFT
                }

    def __init__(self,parent):
        self.parent          = parent




        self.start           = pygame.time.get_ticks()
        self.stage           = PlayingStages.PLAYERS_GO
        self.handlers        = {PlayingStages.PLAYERS_GO : self.PlayerPlay}
        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(globals.screen)
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      buffer = globals.ui_buffer,
                                      colour = (0,0,0,0))
        self.backdrop.Enable()

        self.selected_troop = None
        self.keydownmap = 0
        self.fired = False
        self.moved = False

        self.selected_troop = parent.game_world.NextGoodieToPlay()
        if self.IsItOver():
            return
        if self.selected_troop == None:
            self.parent.mode = ComputerPlaying(self.parent)
        else:
            self.selected_troop.select()
            globals.game_view.viewpos.Follow(self.selected_troop)


        self.last_drag = globals.time

    def MouseMotion(self,pos,rel):
        if self.selected_troop != None:
            self.selected_troop.setWeaponAngle(pos)

    def KeyDown(self,key):
        if key in self.keyflags:
            self.keydownmap |= self.keyflags[key]
            if self.selected_troop:
                if not self.moved:
                    self.selected_troop.move_direction += self.direction_amounts[self.keyflags[key]]
                else:
                    globals.sounds.not_allowed.play()
        elif key in (pygame.K_UP,pygame.K_w) and self.selected_troop and not self.moved:
            self.selected_troop.jump()
        elif key == pygame.K_k and self.selected_troop:
            self.selected_troop.Destroy()
            self.selected_troop.unselect()
            self.selected_troop = None
        elif key == pygame.K_x:
            for baddie in self.parent.game_world.baddies:
                baddie.Destroy();
        elif key == pygame.K_c:
            if self.selected_troop:
                globals.game_view.viewpos.Follow(self.selected_troop)
        elif key == pygame.K_n:
            if self.selected_troop:
                self.selected_troop.unselect()
            self.parent.mode = ComputerPlaying(self.parent)
        elif key == pygame.K_SPACE:
            if self.selected_troop:
                if not self.selected_troop.locked_planet:
                    globals.sounds.not_allowed.play()
                    return
                self.selected_troop.unselect()
            self.parent.mode = ComputerPlaying(self.parent)

    def KeyUp(self,key):
        if key in self.keyflags and (self.keydownmap & self.keyflags[key]):
            self.keydownmap &= (~self.keyflags[key])
            if self.selected_troop and not self.moved:
                self.selected_troop.move_direction -= self.direction_amounts[self.keyflags[key]]

    def MouseButtonDown(self,pos,button):
        if not self.fired:
            if button == 1 or ( button == 1 and self.keydownmap & PlayerPlaying.KeyFlags.SHIFT ):
                if self.selected_troop != None:
                    self.selected_troop.chargeWeapon()
        else:
            globals.sounds.not_allowed.play()

    def MouseButtonUp(self,pos,button):
        if not self.fired:
            if button == 1 or ( button == 1 and self.keydownmap & PlayerPlaying.KeyFlags.SHIFT) :
                if self.selected_troop != None:
                    self.selected_troop.setWeaponAngle(pos)
                    self.parent.game_world.projectiles.append(self.selected_troop.fireWeapon())
                    self.fired = True

    def Update(self):
        if self.IsItOver():
            return
        self.elapsed = globals.time - self.start
        if self.selected_troop and self.selected_troop.amount_moved > globals.max_movement:
            self.selected_troop.move_direction = Point(0,0)
            self.selected_troop.max_movement = 0
            self.moved = True

        self.stage = self.handlers[self.stage](globals.time)
        self.parent.game_world.update()

        if self.selected_troop == None or self.selected_troop.dead:
            self.EndGo()

        if globals.game_view.dragging is not None and globals.game_view.viewpos.follow:
            globals.game_view.viewpos.NoTarget()


    def PlayerPlay(self, ticks):
        return PlayingStages.PLAYERS_GO

    def EndGo(self):
        if self.selected_troop:
            self.selected_troop.unselect()
        self.parent.mode = ComputerPlaying(self.parent)

    def IsItOver(self):
        if len(self.parent.game_world.baddies) == 0:
            globals.sounds.level_win.play()
            if game_world.GameWorld.last_level == self.parent.game_world.level:
                self.parent.mode = GameOver(self.parent, True)
            else:
                self.parent.game_world.Destroy()
                self.parent.game_world = game_world.GameWorld(self.parent.game_world.level + 1)
                self.parent.mode = PlayerPlaying(self.parent)
            return True
        elif len(self.parent.game_world.goodies) == 0:
            self.parent.mode = GameOver(self.parent, False)
            return True
        else:
            return False

class ComputerPlaying(Mode):
    def __init__(self,parent):
        self.parent          = parent
        self.start           = pygame.time.get_ticks()
        bl = self.parent.GetRelative(Point(0,0))
        tr = bl + self.parent.GetRelative(globals.screen)
        self.backdrop        = ui.Box(parent = globals.screen_root,
                                      pos    = Point(0,0),
                                      tr     = Point(1,1),
                                      buffer = globals.ui_buffer,
                                      colour = (0,0,0,0))
        self.backdrop.Enable()
        self.selected_troop = parent.game_world.NextBadieToPlay()
        if self.selected_troop == None:
            self.parent.mode = PlayerPlaying(self.parent)
        else:
            self.selected_troop.select()
        self.ai = AI()


        self.last_drag = globals.time


    def Update(self):
        if self.selected_troop == None:
            self.EndGo()
            return

        keep_going = self.ai.NextMove(self.selected_troop, self.parent.game_world.goodies)
        self.parent.game_world.update()

        if self.selected_troop is None:
            self.EndGo()
            return
        if self.selected_troop.amount_moved > globals.max_movement:
            self.EndGo()
            return

        if self.selected_troop.dead or not keep_going:
            self.EndGo()
            return

        if(globals.game_view.dragging == None):
            if(globals.time > self.last_drag + 500):
                globals.game_view.viewpos.Follow(self.selected_troop)
        else:
            self.last_drag = globals.time
            globals.game_view.viewpos.NoTarget()



    def EndGo(self):
        if self.selected_troop:
            self.selected_troop.unselect()
        self.parent.mode = PlayerPlaying(self.parent)

