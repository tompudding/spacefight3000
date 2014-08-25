from OpenGL.GL import *
import random,numpy,cmath,math,pygame

import ui,globals,drawing,os,copy
from globals.types import Point
import Box2D as box2d
import modes
import random
import gobjects
import hud

def b2Vec_indexer(self,index):
    if index == 0:
        return self.x
    elif index == 1:
        return self.y
def b2Vec_setter(self,index,val):
    if index == 0:
        self.x = val
    elif index == 1:
        self.y = val
box2d.b2Vec2.__getitem__ = b2Vec_indexer
box2d.b2Vec2.__setitem__ = b2Vec_setter

class Viewpos(object):
    follow_threshold = 0
    max_away = 250
    def __init__(self,point):
        self.pos = point
        self.NoTarget()
        self.follow = None
        self.follow_locked = False
        self.t = 0

    def NoTarget(self):
        self.target        = None
        self.target_change = None
        self.start_point   = None
        self.target_time   = None
        self.start_time    = None
        self.follow        = None
        self.follow_locked = False
        self.t = 0

    def Set(self,point):
        self.pos = point
        #self.NoTarget()

    def SetTarget(self,point,rate=2,callback = None):
        #Don't fuck with the view if the player is trying to control it
        rate /= 4.0
        self.follow        = None
        self.follow_start  = 0
        self.follow_locked = False
        self.target        = point
        self.target_change = self.target - self.pos
        self.start_point   = self.pos
        self.start_time    = t
        self.duration      = self.target_change.length()/rate
        self.callback      = callback
        if self.duration < 200:
            self.duration  = 200
        self.target_time   = self.start_time + self.duration

    def Follow(self,actor):
        """
        Follow the given actor around.
        """
        self.follow        = actor
        self.follow_start  = globals.time
        self.follow_locked = False

    def HasTarget(self):
        return self.target != None

    def Get(self):
        return self.pos

    def Skip(self):
        self.pos = self.target
        self.NoTarget()
        if self.callback:
            self.callback(self.t)
            self.callback = None

    def Update(self):
        try:
            return self.update()
        finally:
            self.pos = self.pos.to_int()

    def update(self):
        t = globals.time
        self.t = globals.time
        if self.follow:
            if self.follow_locked:
                self.pos = Point(*self.follow.centre_world) - globals.screen*0.5/globals.game_view.zoom
            else:
                #We haven't locked onto it yet, so move closer, and lock on if it's below the threshold
                fpos = Point(*self.follow.centre_world)
                if not fpos:
                    return
                target = fpos - globals.screen*0.5/globals.game_view.zoom
                diff = target - self.pos
                self.pos += diff*0.02

        elif self.target:
            if t >= self.target_time:
                self.pos = self.target
                self.NoTarget()
                if self.callback:
                    self.callback(t)
                    self.callback = None
            elif t < self.start_time: #I don't think we should get this
                return
            else:
                partial = float(t-self.start_time)/self.duration
                partial = partial*partial*(3 - 2*partial) #smoothstep
                self.pos = (self.start_point + (self.target_change*partial)).to_int()

class fwContactPoint:
    """
    Structure holding the necessary information for a contact point.
    All of the information is copied from the contact listener callbacks.
    """
    shape1 = None
    shape2 = None
    normal = None
    position = None
    velocity = None
    id  = None
    state = 0

class MyContactListener(box2d.b2ContactListener):
    physics = None
    def __init__(self):
        super(MyContactListener, self).__init__()
    def Add(self, point):
        """Handle add point"""
        if not globals.physics:
            return
        cp          = fwContactPoint()
        cp.shape1   = point.shape1
        cp.shape2   = point.shape2
        cp.position = point.position.copy()
        cp.normal   = point.normal.copy()
        cp.id       = point.id.key
        #globals.sounds.thud.play()
        globals.physics.contacts.append(cp)

        self.checkProjectileTroopCollision(cp.shape1, cp.shape2)
        self.checkProjectileTroopCollision(cp.shape2, cp.shape1)

        s1 = point.shape1.userData
        s2 = point.shape2.userData
        if hasattr(s1, "teleportable") and s1.teleportable and isinstance(s2,gobjects.planet.PortalEnd):
            s1,s2 = s2,s1

        if isinstance(s1,gobjects.planet.PortalEnd) and hasattr(s2, "teleportable") and s2.teleportable:
            troop = s2
            portal = s1
            troop.AddPortalContact(portal,cp)

        #returns false if the projectile hits the originating troop
    def checkProjectileTroopCollision(self, shape1, shape2):
        if isinstance(shape2.userData, gobjects.Projectile):
            projectile = shape2.userData
            if hasattr(projectile,'teleport_in_progress') and projectile.teleport_in_progress:
                print 'ignoring!'
                #ignore this, it's a phantom!
                return
            if isinstance(shape1.userData, gobjects.Troop):
                troop = shape1.userData

                if not (projectile.ParentTroop != None and troop == projectile.ParentTroop):
                    troop.TakeDamage(projectile.getDamageToDo())
                    projectile.destroyNextUpdate()
            else:
                if isinstance(shape1.userData, gobjects.Planet):
                    projectile.destroyAfterTimeLimit(100)
                elif isinstance(shape1.userData, gobjects.planet.PortalEnd):
                    pass
                else:
                    projectile.destroyNextUpdate()


    def Persist(self, point):
        """Handle persist point"""

        pass

    def Remove(self, point):
        """Handle remove point"""
        cp          = fwContactPoint()
        cp.shape1   = point.shape1
        cp.shape2   = point.shape2
        cp.position = point.position.copy()
        cp.normal   = point.normal.copy()
        cp.id       = point.id.key

        s1 = point.shape1.userData
        s2 = point.shape2.userData
        if isinstance(s1,gobjects.Troop) and isinstance(s2,gobjects.planet.PortalEnd):
            s1,s2 = s2,s1
        if isinstance(s1,gobjects.planet.PortalEnd) and isinstance(s2,gobjects.Troop):
            troop = s2
            portal = s1
            troop.RemovePortalContact(portal,cp)
    def Result(self, point):
        """Handle results"""
        pass

class MyContactFilter(box2d.b2ContactFilter):
    def __init__(self):
        self.thrown = None
        self.pushed = None
        self.collide = False
        super(MyContactFilter,self).__init__()
    def ShouldCollide(self, shape1, shape2):
        #print 'cf',shape1
        #print 'cf1',shape2
        # Implements the default behavior of b2ContactFilter in Python
        if self.collide:
            return True

        #print 'collision!',shape1 == shape1.userData.shape#,shape2
        filter1 = shape1.filter
        filter2 = shape2.filter
        #print filter1.groupIndex,filter2.groupIndex
        if filter1.groupIndex == filter2.groupIndex and filter1.groupIndex != 0:
            return filter1.groupIndex > 0

        collides = (filter1.maskBits & filter2.categoryBits) != 0 and (filter1.categoryBits & filter2.maskBits) != 0
        return collides


class Physics(object):
    scale_factor = 0.05
    def __init__(self,parent):
        self.contact_listener = MyContactListener()
        self.contact_listener.physics = self
        self.contact_filter = MyContactFilter()
        self.contact_filter.physics = self
        self.parent = parent
        self.worldAABB=box2d.b2AABB()
        self.worldAABB.lowerBound = (-100,-globals.screen.y-100)
        self.worldAABB.upperBound = (100 + self.parent.absolute.size.x*self.scale_factor,100 + self.parent.absolute.size.y*self.scale_factor + 100)
        self.gravity = (0, 0)
        self.doSleep = True
        self.world = box2d.b2World(self.worldAABB, self.gravity, self.doSleep)
        self.world.SetContactListener(self.contact_listener)
        self.world.SetContactFilter(self.contact_filter)
        self.timeStep = 1.0 / 60.0
        self.velocityIterations = 10
        self.positionIterations = 8
        self.max_zoom = 2.0
        self.objects = []
        self.gravity_sources = []

    def AddObject(self,obj):
        if not obj.static:
            self.objects.append(obj)
        if obj.is_gravity_source:
            self.gravity_sources.append(obj)

    def RemoveObject(self,to_remove):
        if not to_remove.static:
            self.objects = [obj for obj in self.objects if obj is not to_remove]
        if to_remove.is_gravity_source:
            self.gravity_sources = [obj for obj in self.gravity_sources if obj is not to_remove]

    def Step(self):
        self.contacts = []
        self.world.Step(self.timeStep, self.velocityIterations, self.positionIterations)
        for obj in self.objects:
            obj.PhysUpdate(self.gravity_sources)


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
    max_zoom = 4.0
    min_zoom = 0.5
    def __init__(self):
        self.atlas = globals.atlas
        self.backdrop_texture = drawing.texture.Texture(os.path.join(globals.dirs.images,'starfield.png'))
        self.backdrop_alpha_texture = drawing.texture.Texture(os.path.join(globals.dirs.images,'starfield_alpha.png'))
        super(GameView,self).__init__(Point(0,0),Point(4000,4000))
        tiles = (self.absolute.size.to_float())/self.backdrop_texture.size
        self.backdrop  = drawing.Quad(globals.backdrop_buffer,tc = numpy.array([(0,0),(0,tiles.y),(tiles.x,tiles.y),(tiles.x,0)]))
        self.backdrop_alpha  = drawing.Quad(globals.backdrop_alpha_buffer,tc = numpy.array([(tiles.x,tiles.y),(tiles.x,0),(0,0),(0,tiles.y),]))
        self.backdrop.SetVertices(Point(0,0),
                                  self.absolute.size,
                                  drawing.constants.DrawLevels.grid)
        self.backdrop_alpha.SetVertices(Point(0,0),
                                        self.absolute.size,
                                        drawing.constants.DrawLevels.grid+1)
        self.game_over = False
        self.dragging = None
        self.paused = False
        self.zoom = 1
        self.viewpos = Viewpos(Point(0,0))
        pygame.mixer.music.load(os.path.join('resource','music','theme.ogg'))
        #self.music_playing = False

        globals.physics = Physics(self)

        #skip titles for development of the main game
        self.mode = modes.Titles(self)
        self.parallax = Point(-1024,-1024)
        #self.mode = modes.LevelOne(self)
        self.StartMusic()

        self.hud = hud.Hud(globals.screen_root)

    def StartMusic(self):
        pygame.mixer.music.play(-1)
        self.music_playing = True

    def Draw(self):
        drawing.ResetState()
        drawing.DrawAll(globals.backdrop_buffer,self.backdrop_texture.texture)

        drawing.ResetState()
        drawing.Translate(self.parallax.x-self.viewpos.pos.x/2,self.parallax.y-self.viewpos.pos.y/2,0)
        drawing.DrawAll(globals.backdrop_alpha_buffer,self.backdrop_alpha_texture.texture)

        drawing.ResetState()
        drawing.Scale(self.zoom,self.zoom,1)
        drawing.Translate(-self.viewpos.pos.x,-self.viewpos.pos.y,0)
        drawing.DrawAll(globals.quad_buffer,self.atlas.texture.texture)
        drawing.DrawAll(globals.nonstatic_text_buffer,globals.text_manager.atlas.texture.texture)
        drawing.DrawNoTexture(globals.nonstatic_ui_buffer)

    def Update(self):
        self.viewpos.Update()

        if self.hud and self.hud.help_screen.enabled:
            return
        self.viewpos.Update()
        if self.mode:
            self.mode.Update()

        if self.game_over:
            return

        if not self.paused:
            globals.physics.Step()

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
        if key == pygame.K_LCTRL or key == pygame.K_RCTRL:
            self.dragging = None
        self.mode.KeyUp(key)

    def MouseButtonDown(self,pos,button):
        if self.hud and self.hud.help_screen.enabled:
            return False,False
        screen_pos = self.viewpos.Get() + (pos/self.zoom)
        if button == 2 or button == 3 or pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.dragging = screen_pos

        if button not in (4,5): #Don't give them scroll wheel events
            self.mode.MouseButtonDown(screen_pos,button)

        return super(GameView,self).MouseButtonDown(pos,button)

    def MouseButtonUp(self,pos,button):
        if self.hud and self.hud.help_screen.enabled:
            return False,False
        #print 'mouse button up',pos,button
        screen_pos = self.viewpos.Get() + (pos/self.zoom)
        if button == 2 or button == 3 or pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.dragging = None
        elif button == 4 and not self.dragging:
            self.AdjustZoom(-0.5,pos)
        elif button == 5 and not self.dragging:
            self.AdjustZoom(+0.5,pos)

        if button not in (4,5):
            self.mode.MouseButtonUp(screen_pos,button)
        return super(GameView,self).MouseButtonUp(pos,button)

    def MouseMotion(self,pos,rel,handled):
        if self.hud and self.hud.help_screen.enabled:
            return False
        #print 'mouse',pos
        #if self.selected_player != None:
        #    self.selected_player.MouseMotion()
        screen_pos = self.viewpos.Get() + (pos/self.zoom)
        screen_rel = rel/self.zoom
        self.mouse_pos = pos
        if self.dragging:
            self.viewpos.Set(self.dragging - (pos/self.zoom))
            self.ClampViewpos()
            self.dragging = self.viewpos.Get() + (pos/self.zoom)
        else:
            self.mode.MouseMotion(screen_pos,screen_rel)
        #print self.viewpos.Get()
        return super(GameView,self).MouseMotion(pos,screen_rel,handled)

    def AdjustZoom(self,amount,pos):
        pos_coords = self.viewpos.Get() + (pos/self.zoom)
        oldzoom = self.zoom
        self.zoom -= (amount/10.0)
        if self.zoom < self.min_zoom:
            self.zoom = self.min_zoom
        if self.zoom > self.max_zoom:
            self.zoom = self.max_zoom

        #if we've zoomed so far out that we can see an edge of the screen, fix that
        top_left= Point(0,globals.screen.y/self.zoom)
        top_right = globals.screen/self.zoom
        bottom_right = Point(globals.screen.x/self.zoom,0)

        new_viewpos = self.viewpos.Get()
        if new_viewpos.y < 0:
            new_viewpos.y = 0

        if new_viewpos.x < 0:
            new_viewpos.x = 0

        #now the top left
        new_top_right = new_viewpos+top_right
        if new_top_right.y  > self.absolute.size.y:
            new_viewpos.y -= (new_top_right.y - self.absolute.size.y)

        if new_top_right.x > self.absolute.size.x:
            new_viewpos.x -= (new_top_right.x - self.absolute.size.x)

        try:
            if new_viewpos.y < 0:
                raise ValueError

            if new_viewpos.x < 0:
                raise ValueError

            #now the top left
            new_top_right = new_viewpos+top_right
            if new_top_right.y  > self.absolute.size.y:
                raise ValueError

            if new_top_right.x > self.absolute.size.x:
                raise ValueError

        except ValueError:
            #abort! This is a bit shit but whatever
            self.zoom = oldzoom
            return

        new_pos_coords = self.viewpos.Get() + pos/self.zoom
        self.parallax += (pos_coords-new_pos_coords)/2
        self.viewpos.Set(self.viewpos.Get() + (pos_coords - new_pos_coords))
        diff = self.ClampViewpos()
        self.parallax += diff/2

    def ClampViewpos(self):
        old = Point(*self.viewpos.pos)
        if self.viewpos.pos.x < 0:
            self.viewpos.pos.x = 0
        if self.viewpos.pos.y < 0:
            self.viewpos.pos.y = 0
        if self.viewpos.pos.x > (self.absolute.size.x - (globals.screen.x/self.zoom)):
            self.viewpos.pos.x = (self.absolute.size.x - (globals.screen.x/self.zoom))
        if self.viewpos.pos.y > (self.absolute.size.y - (globals.screen.y/self.zoom)):
            self.viewpos.pos.y = (self.absolute.size.y - (globals.screen.y/self.zoom))
        return self.viewpos.pos-old
