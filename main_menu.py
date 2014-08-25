import globals
import drawing
from globals.types import Point
from pygame.locals import *
import ui
import random
import os
import game_view
import pygame

class MainMenu(ui.RootElement):
    def __init__(self):
        super(MainMenu,self).__init__(Point(0,0),globals.screen)
        self.backdrop_texture = drawing.texture.Texture(os.path.join(globals.dirs.images,'starfield.png'))
        self.backdrop = drawing.Quad(globals.backdrop_buffer,tc = drawing.constants.full_tc)
        self.backdrop.SetVertices(Point(0,0),
                                  self.absolute.size,
                                  drawing.constants.DrawLevels.grid)

        self.play_button = ui.TextBoxButton(self ,
                                            'Play'               ,
                                            Point(0.22,0.15),
                                            size=16,
                                            callback = self.Play,
                                            line_width=4)
        self.exit_button = ui.TextBoxButton(globals.screen_root,
                                            'Exit'              ,
                                            Point(0.65,
                                                  (0.15)),
                                            size=16,
                                            callback = self.Quit,
                                            line_width=4)
        self.times = [80,850,1600]
        self.words = 'SPACE','FIGHT','3000!!!'
        self.positions = Point(0.15,0.7),Point(0.25,0.5),Point(0.35,0.3)
        self.colours = (drawing.constants.colours.red,
                        drawing.constants.colours.blue,
                        drawing.constants.colours.yellow)
        self.words_ui = []
        for word,position,colour in zip(self.words,self.positions,self.colours):
            self.words_ui.append( ui.TextBox(parent=self,
                                             bl=position,
                                             tr=position+Point(0.6,0.2),
                                             text=word,
                                             scale=48,
                                             textType = drawing.texture.TextTypes.SCREEN_RELATIVE,
                                             colour=colour) )
        for word in self.words_ui:
            word.Disable()
        self.words_to_appear = self.words_ui[::]
        pygame.mixer.music.load(os.path.join('resource','music','title_music.ogg'))
        self.StartMusic()

        self.start = globals.time

    def Draw(self):
        drawing.ResetState()
        drawing.DrawAll(globals.backdrop_buffer,self.backdrop_texture.texture)

    def StartMusic(self):
        pygame.mixer.music.play(-1)
        self.music_playing = True

    def StopMusic(self):
        pygame.mixer.music.stop()
        self.music_playing = False


    def KeyDown(self,key):
        return

    def Update(self):
        if not self.times:
            return
        if globals.time-self.start > self.times[0]+800:
            self.words_to_appear[0].Enable()
            self.words_to_appear.pop(0)
            self.times.pop(0)


    def Play(self,pos):
        self.backdrop.Delete()
        self.play_button.Delete()
        self.exit_button.Delete()
        for word in self.words_ui:
            word.Delete()
        self.StopMusic()
        globals.current_view = globals.game_view = game_view.GameView()

    def Quit(self,pos):
        raise SystemExit('Goodbye')
