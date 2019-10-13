"""
Propeller Game Level Editor Engine created by Brad Wyatt

ISSUES TO SOLVE:
I may want to separate sprite groups by PLAY and STOP sprites
Several elifs (with references to many parameters)
Rotate spikes
"""
import random
import sys
import os
import copy
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import asksaveasfilename, askopenfilename
from ast import literal_eval
import pygame
from pygame.constants import RLEACCEL
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)

########################
# GLOBAL CONSTANTS and MUTABLES
# Starting positions of each of the objects
########################
STARTPOS = {'player': (10, 4), 'wall': (40, 12), 'reverse_wall': (102, 12),
            'spring': (255, 12), 'flyer': (130, 12), 'smily_robot': (162, 12),
            'door': (195, 2), 'diamonds': (225, 14), 'sticky_block': (70, 12),
            'fall_spikes': (290, 12), 'stand_spikes': (320, 12)}
SCREEN_WIDTH, SCREEN_HEIGHT = 936, 650
START_SPRITES = pygame.sprite.Group()
IMAGES = {}
SOUNDS = {}
    

def adjust_to_correct_appdir():
    """
    Used for adjusting python image loading to correct directory
    Taken from https://www.pygame.org/wiki/RunningInCorrectDirectory
    """
    try:
        appdir = sys.argv[0] # feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0, appdir)
    except:
        #placeholder for feedback, adjust to your app.
        #remember to use only python and python standard libraries
        #not any resource or module into the appdir
        #a window in Tkinter can be adequate for apps without console
        #a simple print with a timeout can be enough for console apps
        print('Please run from an OS console.')
        import time
        time.sleep(10)
        sys.exit(1)
adjust_to_correct_appdir()

def load_sound(file, name):
    sound = pygame.mixer.Sound(file)
    SOUNDS[name] = sound

def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0, 0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    IMAGES[name] = new_image

def snap_to_grid(pos, screen_width, screen_height):
    best_num_x, best_num_y = 0, 48 # Y is 48 so it doesn't go above the menu
    for x_coord in range(0, screen_width, 24):
        if pos[0]-x_coord <= 24 and pos[0]-x_coord >= 0:
            best_num_x = x_coord
    for y_coord in range(48, screen_height, 24):
        if pos[1]-y_coord <= 24 and pos[1]-y_coord >= 0:
            best_num_y = y_coord
    return (best_num_x, best_num_y)

def remove_placed_object(PLACED_SPRITES, mousepos):
    for placed_item_list in (PlacedPlayer.player_list, PlacedWall.wall_list, PlacedFlyer.flyer_list,
                             PlacedSpring.spring_list, PlacedDiamonds.diamonds_list, PlacedReverseWall.reverse_wall_list,
                             PlacedSmilyRobot.smily_robot_list, PlacedDoor.door_list, PlacedStickyBlock.sticky_block_list,
                             PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(mousepos):
                PLACED_SPRITES.remove(placed_item)
                placed_item_list.remove(placed_item)
    return PLACED_SPRITES

def restart_start_objects(START):
    START.player.rect.topleft = STARTPOS['player']
    START.wall.rect.topleft = STARTPOS['wall']
    START.reverse_wall.rect.topleft = STARTPOS['reverse_wall']
    START.spring.rect.topleft = STARTPOS['spring']
    START.flyer.rect.topleft = STARTPOS['flyer']
    START.smily_robot.rect.topleft = STARTPOS['smily_robot']
    START.door.rect.topleft = STARTPOS['door']
    START.diamonds.rect.topleft = STARTPOS['diamonds']
    START.sticky_block.rect.topleft = STARTPOS['sticky_block']
    START.fall_spikes.rect.topleft = STARTPOS['fall_spikes']
    START.fall_spikes.rect.topleft = STARTPOS['stand_spikes']
    return START

def get_color():
    color = askcolor()
    return [color[0][0], color[0][1], color[0][2]]

def load_file(PLACED_SPRITES, colorkey):
    request_file_name = askopenfilename(defaultextension=".lvl")
    open_file = open(request_file_name, "r")
    loaded_file = open_file.read()
    loaded_dict = literal_eval(loaded_file)
            
    for player in PlayPlayer.player_list:
        player.destroy()
    for door in PlayDoor.door_list:
        door.destroy()
    for wall in PlayWall.wall_list:
        wall.destroy()
    for reverse_wall in PlayReverseWall.reverse_wall_list:
        reverse_wall.destroy()
    for flyer in PlayFlyer.flyer_list:
        flyer.destroy()
    for smily_robot in PlaySmilyRobot.smily_robot_list:
        smily_robot.destroy()
    for spring in PlaySpring.spring_list:
        spring.destroy()
    for diamond in PlayDiamonds.diamonds_list:
        diamond.destroy()
    for sticky_block in PlayStickyBlock.sticky_block_list:
        sticky_block.destroy()
    for fall_spikes in PlayFallSpikes.fall_spikes_list:
        fall_spikes.destroy()
    for stand_spikes in PlayStandSpikes.stand_spikes_list:
        stand_spikes.destroy()
    open_file.close()
    
    # Removes all placed lists
    remove_all_placed()
    
    print("Removed all sprites. Now creating lists for loaded level.")
    
    for player_pos in loaded_dict['player']:
        PlacedPlayer(player_pos, PLACED_SPRITES)
    for door_pos in loaded_dict['door']:
        PlacedDoor(door_pos, PLACED_SPRITES)
    for wall_pos in loaded_dict['wall']:
        PlacedWall(wall_pos, PLACED_SPRITES)
    for reverse_wall_pos in loaded_dict['reverse_wall']:
        PlacedReverseWall(reverse_wall_pos, PLACED_SPRITES)
    for flyer_pos in loaded_dict['flyer']:
        PlacedFlyer(flyer_pos, PLACED_SPRITES)
    for smily_robot_pos in loaded_dict['smily_robot']:
        PlacedSmilyRobot(smily_robot_pos, PLACED_SPRITES)
    for spring_pos in loaded_dict['spring']:
        PlacedSpring(spring_pos, PLACED_SPRITES)
    for diamond_pos in loaded_dict['diamonds']:
        PlacedDiamonds(diamond_pos, PLACED_SPRITES)
    for sticky_block_pos in loaded_dict['sticky_block']:
        PlacedStickyBlock(sticky_block_pos, PLACED_SPRITES)
    for fall_spikes_pos in loaded_dict['fall_spikes']:
        PlacedFallSpikes(fall_spikes_pos, PLACED_SPRITES)
    for stand_spikes_pos in loaded_dict['stand_spikes']:
        PlacedStandSpikes(stand_spikes_pos, PLACED_SPRITES)
    colorkey = loaded_dict['RGB']
    
    print("File Loaded")
    return PLACED_SPRITES, colorkey

def save_file(colorkey):
    try:
        if PlacedPlayer.player_list and PlacedDoor.door_list:
            # default extension is optional, here will add .txt if missing
            save_file_prompt = asksaveasfilename(defaultextension=".lvl")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                obj_locations = copy.deepcopy(get_dict_rect_positions())
                obj_locations['RGB'] = colorkey
                save_file_name.write(str(obj_locations))
                save_file_name.close()
                print("File Saved Successfully.")
        else:
            print("Error! Need player and door to save!")
    except IOError:
        print("Save File Error, please restart game and try again.")

class InfoScreen():
    def __init__(self, INFO_SCREEN, screen):
        self.screen = screen
        self.title = INFO_SCREEN
        self.clock = pygame.time.Clock()
        self.menuon = 2
        self.main_loop()

    def main_loop(self):
        while self.menuon == 2:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            info_events = pygame.event.get()
            pygame.display.flip()
            for info_event in info_events:
                if info_event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if info_event.type == KEYDOWN:
                    if info_event.key == K_ESCAPE:
                        self.menuon = 1
                        break

class ClearButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_CLEAR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class InfoButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_INFO_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class RestartButton(pygame.sprite.Sprite):
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_RESTART_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLAY_SPRITES.add(self)

class GridButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GRID_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
        self.grid_on_var = 1

class ColorButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_COLOR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SAVE_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_LOAD_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class RotateButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_ROTATE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class StartBlankBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass
    def flip_start_sprite(self, DRAGGING, pos):
        self.rect.topleft = pos
        if DRAGGING.player:
            self.image = IMAGES["SPR_PLAYER"]
        elif DRAGGING.wall:
            self.image = IMAGES["SPR_WALL"]
        elif DRAGGING.diamonds:
            self.image = IMAGES["SPR_DIAMONDS"]
        elif DRAGGING.door:
            self.image = pygame.transform.smoothscale(IMAGES["SPR_DOOR_CLOSED"], (24, 40))
        elif DRAGGING.flyer:
            self.image = IMAGES["SPR_FLYER"]
        elif DRAGGING.reverse_wall:
            self.image = IMAGES["SPR_REVERSE_WALL"]
        elif DRAGGING.smily_robot:
            self.image = IMAGES["SPR_SMILYROBOT"]
        elif DRAGGING.spring:
            self.image = IMAGES["SPR_SPRING"]
        elif DRAGGING.sticky_block:
            self.image = IMAGES["SPR_STICKYBLOCK"]
        elif DRAGGING.fall_spikes:
            self.image = IMAGES["SPR_FALLSPIKES"]
        elif DRAGGING.stand_spikes:
            self.image = IMAGES["SPR_STANDSPIKES"]
        else:
            self.image = IMAGES["SPR_BLANKBOX"]

class StartWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_WALL"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartReverseWall(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_REVERSE_WALL"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartDiamonds(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DIAMONDS"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartDoor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.smoothscale(IMAGES["SPR_DOOR_CLOSED"], (24, 40))
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartFlyer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLYER"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartSmilyRobot(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SMILYROBOT"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartSpring(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SPRING"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartPlayer(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAYER"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartStickyBlock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STICKYBLOCK"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartFallSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FALLSPIKES"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass

class StartStandSpikes(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STANDSPIKES"]
        self.rect = self.image.get_rect()
        
        self.rotate = 0
    def update(self):
        pass

class PlacedWall(pygame.sprite.Sprite):
    wall_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_WALL"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedWall.wall_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedWall.wall_list.remove(self)
        self.kill()
        

class PlacedReverseWall(pygame.sprite.Sprite):
    reverse_wall_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_REVERSE_WALL"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedReverseWall.reverse_wall_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedReverseWall.reverse_wall_list.remove(self)
        self.kill()

class PlacedDiamonds(pygame.sprite.Sprite):
    diamonds_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DIAMONDS"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedDiamonds.diamonds_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedDiamonds.diamonds_list.remove(self)
        self.kill()

class PlacedDoor(pygame.sprite.Sprite):
    door_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DOOR_CLOSED"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedDoor.door_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedDoor.door_list.remove(self)
        self.kill()

class PlacedFlyer(pygame.sprite.Sprite):
    flyer_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLYER"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedFlyer.flyer_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedFlyer.flyer_list.remove(self)
        self.kill()

class PlacedSmilyRobot(pygame.sprite.Sprite):
    smily_robot_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SMILYROBOT"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedSmilyRobot.smily_robot_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedSmilyRobot.smily_robot_list.remove(self)
        self.kill()

class PlacedSpring(pygame.sprite.Sprite):
    spring_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SPRING"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedSpring.spring_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedSpring.spring_list.remove(self)
        self.kill()

class PlacedStickyBlock(pygame.sprite.Sprite):
    sticky_block_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STICKYBLOCK"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedStickyBlock.sticky_block_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedStickyBlock.sticky_block_list.remove(self)
        self.kill()

class PlacedFallSpikes(pygame.sprite.Sprite):
    fall_spikes_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FALLSPIKES"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedFallSpikes.fall_spikes_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedFallSpikes.fall_spikes_list.remove(self)
        self.kill()

class PlacedStandSpikes(pygame.sprite.Sprite):
    stand_spikes_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STANDSPIKES"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedStandSpikes.stand_spikes_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlacedStandSpikes.stand_spikes_list.remove(self)
        self.kill()
    
class PlacedPlayer(pygame.sprite.Sprite):
    player_list = []
    def __init__(self, pos, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAYER"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLACED_SPRITES.add(self)
        PlacedPlayer.player_list.append(self)
    def update(self):
        pass
    def move_to_coord(self, coord):
        self.rect.topleft = coord
    def destroy(self):
        PlacedPlayer.player_list.remove(self)
        self.kill()

class PlayWall(pygame.sprite.Sprite):
    wall_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_WALL"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayWall.wall_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlayWall.wall_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos
            
class PlayReverseWall(pygame.sprite.Sprite):
    reverse_wall_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayReverseWall.reverse_wall_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlayReverseWall.reverse_wall_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos

class PlayFlyer(pygame.sprite.Sprite):
    flyer_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLYER"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        self.right_or_left = random.choice([-2, 2])
        PlayFlyer.flyer_list.append(self)
    def update(self):
        self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
        for wall in PlayWall.wall_list:
            if self.rect.colliderect(wall.rect):
                self.right_or_left = self.right_or_left*-1
        for reverse_wall in PlayReverseWall.reverse_wall_list:
            if self.rect.colliderect(reverse_wall.rect):
                self.right_or_left = self.right_or_left*-1
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.right_or_left = self.right_or_left*-1
        self.sprite_direction()
    def sprite_direction(self):
        if self.right_or_left == 2:
            self.image = IMAGES["SPR_FLYER"]
        elif self.right_or_left == -2:
            self.image = pygame.transform.flip(IMAGES["SPR_FLYER"], 1, 0)
    def destroy(self):
        PlayFlyer.flyer_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos
        self.right_or_left = random.choice([-2, 2])

class PlayDiamonds(pygame.sprite.Sprite):
    diamonds_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DIAMONDS"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayDiamonds.diamonds_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlayDiamonds.diamonds_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos
        self.image = IMAGES["SPR_DIAMONDS"]

class PlayDoor(pygame.sprite.Sprite):
    door_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_DOOR_CLOSED"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayDoor.door_list.append(self)
    def update(self):
        pass
    def open_or_close(self, score, diamonds_list):
        if score == len(diamonds_list):
            return IMAGES["SPR_DOOR_OPEN"]
        return IMAGES["SPR_DOOR_CLOSED"]
    def destroy(self):
        PlayDoor.door_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos

class PlaySmilyRobot(pygame.sprite.Sprite):
    smily_robot_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SMILYROBOT"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlaySmilyRobot.smily_robot_list.append(self)
        self.right_or_left = random.choice([-2, 2])
        self.animatetimer = 0
        self.speed_y = 0
        self.jumps_left = 1
        self.wall_hit_list = []
        self.stickyblock_hit_list = []
    def update(self):
        if self.rect.topleft != (0, -100): # This is its out of play location
            self.animate()
            self.calc_grav()
            if PlayWall.wall_list is None:
                self.wall_hit_list = []
            else:
                self.wall_hit_list = pygame.sprite.spritecollide(self, PlayWall.wall_list, False)
            for wall in self.wall_hit_list:
                if(self.rect.right-wall.rect.left < 5 and
                   self.right_or_left == 2): # Robot moves right and collides into wall
                    self.rect.right = wall.rect.left
                    self.right_or_left = -2
                elif(wall.rect.right-self.rect.left < 5 and
                     self.right_or_left == -2): # Robot moves left and collides into wall
                    self.rect.left = wall.rect.right
                    self.right_or_left = 2
            if PlayStickyBlock.sticky_block_list is None:
                self.stickyblock_hit_list = []
            else:
                self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PlayStickyBlock.sticky_block_list, False)
            for stickyblock in self.stickyblock_hit_list:
                if(self.rect.right-stickyblock.rect.left < 5 and
                   self.right_or_left == 2): # Robot moves right and collides into wall
                    self.rect.right = stickyblock.rect.left
                    self.right_or_left = -2
                elif(stickyblock.rect.right-self.rect.left < 5 and
                     self.right_or_left == -2): # Robot moves left and collides into wall
                    self.rect.left = stickyblock.rect.right
                    self.right_or_left = 2
            self.rect.y += self.speed_y
            if PlayWall.wall_list is None:
                self.wall_hit_list = []
            else:
                self.wall_hit_list = pygame.sprite.spritecollide(self, PlayWall.wall_list, False)
            for wall in self.wall_hit_list:
                # Reset our position based on the top/bottom of the object.
                if self.speed_y > 0:
                    self.rect.bottom = wall.rect.top # On top of the wall
                elif self.speed_y < 0:
                    self.rect.top = wall.rect.bottom # Below the wall
                # Stop our vertical movement
                self.speed_y = 0
            if PlayStickyBlock.sticky_block_list is None:
                self.stickyblock_hit_list = []
            else:
                self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PlayStickyBlock.sticky_block_list, False)
            for stickyblock in self.stickyblock_hit_list:
                # Reset our position based on the top/bottom of the object.
                if self.speed_y > 0:
                    self.rect.bottom = stickyblock.rect.top # On top of the wall
                elif self.speed_y < 0:
                    self.rect.top = stickyblock.rect.bottom # Below the wall
                # Stop our vertical movement
                self.speed_y = 0
            self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
            if PlayReverseWall.reverse_wall_list:
                for reverse_wall in PlayReverseWall.reverse_wall_list:
                    if self.rect.colliderect(reverse_wall.rect):
                        self.right_or_left *= -1
            if PlayWall.wall_list is None:
                self.wall_hit_list = []
            else:
                self.wall_hit_list = pygame.sprite.spritecollide(self, PlayWall.wall_list, False)
            for wall in self.wall_hit_list:
                if self.speed_y > 0:
                    self.rect.bottom = wall.rect.top # On top of the wall
                    self.jumps_left = 2
            if PlayStickyBlock.sticky_block_list is None:
                self.stickyblock_hit_list = []
            else:
                self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PlayStickyBlock.sticky_block_list, False)
            for stickyblock in self.stickyblock_hit_list:
                if self.speed_y > 0:
                    self.rect.bottom = stickyblock.rect.top # On top of the wall
                    self.jumps_left = 2
    def destroy(self):
        #PlaySmilyRobot.smily_robot_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos
        self.speed_y = 0
        self.right_or_left = random.choice([-2, 2])
    def animate(self):
        # Two different pictures to animate that makes it look like it's moving
        self.animatetimer += 1
        if self.animatetimer > 5:
            self.image = IMAGES["SPR_SMILYROBOT2"]
        if self.animatetimer > 10:
            self.image = IMAGES["SPR_SMILYROBOT"]
            self.animatetimer = 0
    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        else:
            self.speed_y += .25

        
class PlayStickyBlock(pygame.sprite.Sprite):
    sticky_block_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STICKYBLOCK"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayStickyBlock.sticky_block_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlayStickyBlock.sticky_block_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos

class PlayFallSpikes(pygame.sprite.Sprite):
    fall_spikes_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FALLSPIKES"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayFallSpikes.fall_spikes_list.append(self)
        self.fall_var = 0
    def update(self):
        pass
    def destroy(self):
        PlayFallSpikes.fall_spikes_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos
        self.fall_var = 0

class PlayStandSpikes(pygame.sprite.Sprite):
    stand_spikes_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_STANDSPIKES"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayStandSpikes.stand_spikes_list.append(self)
        self.fall_var = 0
    def update(self):
        pass
    def destroy(self):
        PlayStandSpikes.stand_spikes_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos

class PlaySpring(pygame.sprite.Sprite):
    spring_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SPRING"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlaySpring.spring_list.append(self)
    def update(self):
        pass
    def destroy(self):
        PlaySpring.spring_list.remove(self)
        self.kill()
    def restart(self):
        self.rect.topleft = self.pos

class PlayPlayer(pygame.sprite.Sprite):
    player_list = []
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAYER"]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        PLAY_SPRITES.add(self)
        PlayPlayer.player_list.append(self)
        self.speed_x, self.speed_y = 0, 0
        self.jumps_left = 1
        self.propeller, self.playerproptimer = 0, 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count = 0
        self.wall_hit_list = []
        self.stickyblock_hit_list = []
    def update(self):
        self.calc_grav()
        self.rect.x += self.speed_x
        
        #####################
        # WALLS
        #####################
        self.wall_hit_list = pygame.sprite.spritecollide(self, PlayWall.wall_list, False)
        for wall in self.wall_hit_list:
            if self.speed_x > 0: #player moves right and collides into wall
                self.rect.right = wall.rect.left
            elif self.speed_x < 0: #player moves left and collides into wall
                self.rect.left = wall.rect.right
        self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PlayStickyBlock.sticky_block_list, False)
        for stickyblock in self.stickyblock_hit_list:
            if self.speed_x > 0: #player moves right and collides into wall
                self.rect.right = stickyblock.rect.left
            elif self.speed_x < 0: #player moves left and collides into wall
                self.rect.left = stickyblock.rect.right
        self.rect.y += self.speed_y
        # Check and see if we hit anything
        self.wall_hit_list = pygame.sprite.spritecollide(self, PlayWall.wall_list, False)
        for wall in self.wall_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.speed_y > 0:
                self.rect.bottom = wall.rect.top #On top of the wall
                self.jumps_left = 2
            elif self.speed_y < 0:
                self.rect.top = wall.rect.bottom #Below the wall
            # Stop our vertical movement
            self.speed_y = 0
            self.propeller = 0
        self.stickyblock_hit_list = pygame.sprite.spritecollide(self, PlayStickyBlock.sticky_block_list, False)
        for stickyblock in self.stickyblock_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.speed_y > 0:
                self.rect.bottom = stickyblock.rect.top #On top
                self.jumps_left = 2
            elif self.speed_y < 0:
                self.rect.top = stickyblock.rect.bottom #Below
            # Stop our vertical movement
            self.speed_y = 0
            self.propeller = 0
        self.animate_images()
        
        
    def destroy(self):
        PlayPlayer.player_list.remove(self)
        self.kill()
    def go_left(self):
        self.speed_x = -4
    def go_right(self):
        self.speed_x = 4
    def stop(self):
        self.speed_x = 0
    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        elif self.propeller == 1:
            self.speed_y += .01
            if self.speed_y >= -2:
                SOUNDS["SND_PROPELLER"].play()
            if self.speed_y > -1.5:
                self.propeller = 0
                self.speed_y += .25
        else:
            SOUNDS["SND_PROPELLER"].stop()
            self.speed_y += .25
    def jump(self):
        # For moving platforms that go up and down...
        self.speed_y += 2
        self.speed_y -= 2
        # If there is a platform below you, you are able to jump
        if self.wall_hit_list and self.jumps_left == 2: #Big First Jump
            self.speed_y = -7
            self.jumps_left = 1
        elif self.stickyblock_hit_list and self.jumps_left >= 1: # Sticky --> No Jump
            self.jumps_left = 0
        elif not self.wall_hit_list and self.jumps_left >= 1: # Double Jump when not on platform
            self.speed_y = -2
            self.propeller = 1
            self.jumps_left = 0
        elif not self.wall_hit_list: # If Player is not on top of wall, he only has propeller left
            if self.jumps_left == 2:
                self.jumps_left = 1
    def animate_images(self):
        if self.propeller == 1:
            self.playerproptimer += 1
            if self.last_pressed_r == 1:
                if self.playerproptimer > 1:
                    self.image = IMAGES["SPR_PLAYER_PROP"]
                if self.playerproptimer > 3:
                    self.image = IMAGES["SPR_PLAYER"]
                    self.playerproptimer = 0
            if self.last_pressed_r == 0:
                if self.playerproptimer > 1:
                    self.image = pygame.transform.flip(IMAGES["SPR_PLAYER_PROP"], 1, 0)
                if self.playerproptimer > 3:
                    self.image = pygame.transform.flip(IMAGES["SPR_PLAYER"], 1, 0)
                    self.playerproptimer = 0
        else:
            if self.last_pressed_r == 1:
                self.image = IMAGES["SPR_PLAYER"]
            else:
                self.image = pygame.transform.flip(IMAGES["SPR_PLAYER"], 1, 0)
    def restart(self):
        # Game Reset
        self.jumps_left = 1
        self.speed_y = 0
        self.propeller = 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count += 1
        self.rect.topleft = self.pos

class PlayEditSwitchButton(pygame.sprite.Sprite):
    def __init__(self, pos, GAME_MODE_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAY_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GAME_MODE_SPRITES.add(self)
    def game_mode_button(self, game_mode):
        if game_mode == 0:
            self.image = IMAGES["SPR_PLAY_BUTTON"]
        elif game_mode == 1:
            self.image = IMAGES["SPR_STOP_BUTTON"]
        return self.image

class MusicPlayer():
    def __init__(self, game_mode):
        if game_mode == 1:
            pygame.mixer.music.load("SOUNDS/playmusic.mp3")
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load("SOUNDS/editingmode.wav")
            pygame.mixer.music.play(-1)

class Grid(pygame.sprite.Sprite):
    grid_list = []
    def __init__(self, GRID_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GRID"]
        self.rect = self.image.get_rect()
        GRID_SPRITES.add(self)
        if self.rect.bottom > SCREEN_HEIGHT:
            GRID_SPRITES.remove(self)
        if self.rect.right > SCREEN_WIDTH:
            GRID_SPRITES.remove(self)
        Grid.grid_list.append(self)


class Dragging():
    def __init__(self):
        self.player = False
        self.wall = False
        self.flyer = False
        self.reverse_wall = False
        self.spring = False
        self.smily_robot = False
        self.door = False
        self.diamonds = False
        self.sticky_block = False
        self.fall_spikes = False
        self.stand_spikes = False
    def dragging_all_false(self):
        self.player = False
        self.wall = False
        self.flyer = False
        self.reverse_wall = False
        self.spring = False
        self.smily_robot = False
        self.door = False
        self.diamonds = False
        self.sticky_block = False
        self.fall_spikes = False
        self.stand_spikes = False
        

class Start():
    def __init__(self):
        self.blank_box = StartBlankBox()
        START_SPRITES.add(self.blank_box)
        self.player = StartPlayer()
        START_SPRITES.add(self.player)
        self.wall = StartWall()
        START_SPRITES.add(self.wall)
        self.flyer = StartFlyer()
        START_SPRITES.add(self.flyer)
        self.reverse_wall = StartReverseWall()
        START_SPRITES.add(self.reverse_wall)
        self.spring = StartSpring()
        START_SPRITES.add(self.spring)
        self.smily_robot = StartSmilyRobot()
        START_SPRITES.add(self.smily_robot)
        self.door = StartDoor()
        START_SPRITES.add(self.door)
        self.diamonds = StartDiamonds()
        START_SPRITES.add(self.diamonds)
        self.sticky_block = StartStickyBlock()
        START_SPRITES.add(self.sticky_block)
        self.fall_spikes = StartFallSpikes()
        START_SPRITES.add(self.fall_spikes)
        self.stand_spikes = StartStandSpikes()
        START_SPRITES.add(self.stand_spikes)

        
# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions():
    total_placed_list = {'player': PlacedPlayer.player_list, 'door': PlacedDoor.door_list, 
                          'wall': PlacedWall.wall_list, 'flyer': PlacedFlyer.flyer_list, 
                          'reverse_wall': PlacedReverseWall.reverse_wall_list,
                          'spring': PlacedSpring.spring_list, 'smily_robot': PlacedSmilyRobot.smily_robot_list,
                          'diamonds': PlacedDiamonds.diamonds_list, 'sticky_block': PlacedStickyBlock.sticky_block_list,
                          'fall_spikes': PlacedFallSpikes.fall_spikes_list, 'stand_spikes': PlacedStandSpikes.stand_spikes_list}
    get_rect_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_rect in item_list:
            item_list_in_name.append(item_rect.rect.topleft)
        get_rect_for_all_obj[item_key] = item_list_in_name
    return get_rect_for_all_obj

def remove_all_placed():
    for spr_list in [PlacedPlayer.player_list, PlacedWall.wall_list, PlacedFlyer.flyer_list,
                     PlacedReverseWall.reverse_wall_list, PlacedSpring.spring_list, PlacedSmilyRobot.smily_robot_list,
                     PlacedDoor.door_list, PlacedDiamonds.diamonds_list, PlacedStickyBlock.sticky_block_list,
                     PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    PlacedPlayer.player_list = []
    PlacedWall.wall_list = []
    PlacedFlyer.flyer_list = []
    PlacedReverseWall.reverse_wall_list = []
    PlacedSpring.spring_list = []
    PlacedSmilyRobot.smily_robot_list = []
    PlacedDoor.door_list = []
    PlacedDiamonds.diamonds_list = []
    PlacedStickyBlock.sticky_block_list = []
    PlacedFallSpikes.fall_spikes_list = []
    PlacedStandSpikes.stand_spikes_list = []

def remove_all_play():
    for spr_list in [PlayPlayer.player_list, PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    PlayPlayer.player_list = []
    PlayWall.wall_list = []
    PlayFlyer.flyer_list = []
    PlayReverseWall.reverse_wall_list = []
    PlaySpring.spring_list = []
    PlaySmilyRobot.smily_robot_list = []
    PlayDoor.door_list = []
    PlayDiamonds.diamonds_list = []
    PlayStickyBlock.sticky_block_list = []
    PlayFallSpikes.fall_spikes_list = []
    PlayStandSpikes.stand_spikes_list = []

def restart_level():
    for spr_list in [PlayPlayer.player_list, PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.restart()

def main():
    #global PLACED_SPRITES
    # Tk box for color
    ROOT = tk.Tk()
    ROOT.withdraw()
    
    MENUON = 1
    SCREEN = None

    COLORKEY = [160, 160, 160]
    
    RUNNING, DEBUG = 0, 1
    state = RUNNING
    debug_message = 0
    
    GRID_SPRITES = pygame.sprite.Group()
    #START_SPRITES = pygame.sprite.Group()
    PLAY_SPRITES = pygame.sprite.Group()
    GAME_MODE_SPRITES = pygame.sprite.Group()
    PLACED_SPRITES = pygame.sprite.Group()
    CLOCK = pygame.time.Clock()
    
    pygame.init()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # pygame.FULLSCREEN for fullSCREEN
    #Fonts
    FONT_ARIAL = pygame.font.SysFont('Arial', 24)
    #Sprites
    load_image("sprites/blankbox.png", "SPR_BLANKBOX", True, False)
    load_image("sprites/doorclosed.png", "SPR_DOOR_CLOSED", True, True)
    load_image("sprites/dooropen.png", "SPR_DOOR_OPEN", True, True)
    load_image("sprites/diamond.png", "SPR_DIAMONDS", True, True)
    load_image("sprites/Wall.png", "SPR_WALL", True, True)
    load_image("sprites/reversewall.png", "SPR_REVERSE_WALL", True, True)
    load_image("sprites/flyer.png", "SPR_FLYER", True, True)
    load_image("sprites/spring.png", "SPR_SPRING", True, True)
    load_image("sprites/smilyrobot1.png", "SPR_SMILYROBOT", True, True)
    load_image("sprites/smilyrobot2.png", "SPR_SMILYROBOT2", True, True)
    load_image("sprites/stickyblock.png", "SPR_STICKYBLOCK", True, True)
    load_image("sprites/fallspikes.png", "SPR_FALLSPIKES", True, True)
    load_image("sprites/standspikes.png", "SPR_STANDSPIKES", True, True)
    load_image("sprites/player.png", "SPR_PLAYER", True, True)
    load_image("sprites/playerprop.png", "SPR_PLAYER_PROP", True, True)
    load_image("sprites/play_button.png", "SPR_PLAY_BUTTON", True, True)
    load_image("sprites/stopbutton.png", "SPR_STOP_BUTTON", True, True)
    load_image("sprites/clear.png", "SPR_CLEAR_BUTTON", True, True)
    load_image("sprites/infobutton.png", "SPR_INFO_BUTTON", True, True)
    load_image("sprites/gridbutton.png", "SPR_GRID_BUTTON", True, True)
    load_image("sprites/restart.png", "SPR_RESTART_BUTTON", True, True)
    load_image("sprites/colorbutton.png", "SPR_COLOR_BUTTON", True, True)
    load_image("sprites/savefile.png", "SPR_SAVE_FILE_BUTTON", True, True)
    load_image("sprites/loadfile.png", "SPR_LOAD_FILE_BUTTON", True, True)
    load_image("sprites/rotate.png", "SPR_ROTATE_BUTTON", True, True)
    load_image("sprites/grid.png", "SPR_GRID", True, True)
    
    #Backgrounds
    START_MENU = pygame.image.load("sprites/startmenu.png").convert()
    START_MENU = pygame.transform.scale(START_MENU, (SCREEN_WIDTH, SCREEN_HEIGHT))
    INFO_SCREEN = pygame.image.load("sprites/infoSCREEN.bmp").convert()
    INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    #Start (Menu) Objects
    START = Start()
    #Dragging Variables
    DRAGGING = Dragging()
    
    PLAY_EDIT_SWITCH_BUTTON = PlayEditSwitchButton((SCREEN_WIDTH-50, 8), GAME_MODE_SPRITES)
    CLEAR_BUTTON = ClearButton((SCREEN_WIDTH-115, 10))
    START_SPRITES.add(CLEAR_BUTTON)
    INFO_BUTTON = InfoButton((SCREEN_WIDTH-320, 10))
    START_SPRITES.add(INFO_BUTTON)
    GRID_BUTTON = GridButton((SCREEN_WIDTH-150, 10))
    START_SPRITES.add(GRID_BUTTON)
    RESTART_BUTTON = RestartButton((SCREEN_WIDTH-175, 10), PLAY_SPRITES)
    COLOR_BUTTON = ColorButton((SCREEN_WIDTH-195, 10))
    START_SPRITES.add(COLOR_BUTTON)
    SAVE_FILE_BUTTON = SaveFileButton((SCREEN_WIDTH-230, 10))
    START_SPRITES.add(SAVE_FILE_BUTTON)
    LOAD_FILE_BUTTON = LoadFileButton((SCREEN_WIDTH-265, 10))
    START_SPRITES.add(LOAD_FILE_BUTTON)
    ROTATE_BUTTON = RotateButton((SCREEN_WIDTH-590, 7))
    START_SPRITES.add(ROTATE_BUTTON)
    
    #window
    GAME_ICON = pygame.image.load("sprites/playerico.png")
    pygame.display.set_icon(GAME_ICON)
    pygame.display.set_caption('Level Editor')
    #SOUNDS
    load_sound("SOUNDS/propeller.wav", "SND_PROPELLER")
    SOUNDS["SND_PROPELLER"].set_volume(.15)
    load_sound("SOUNDS/spring.wav", "SND_SPRING")
    SOUNDS["SND_SPRING"].set_volume(.15)
    #MUSIC_PLAYER = [MusicPlayer()]
    
    EDIT_MODE, PLAY_MODE = 0, 1
    game_mode = EDIT_MODE
    
    # Creating grid on main area
    for i in range(0, SCREEN_WIDTH, 24):
        for j in range(48, SCREEN_HEIGHT, 24):
            grid = Grid(GRID_SPRITES)
            grid.rect.topleft = i, j
    
    while True:
        CLOCK.tick(60)
        MOUSEPOS = pygame.mouse.get_pos()
        
        if state == RUNNING and MENUON == 1: # Initiate room
            START.player.rect.topleft = STARTPOS['player']
            START.wall.rect.topleft = STARTPOS['wall']
            START.flyer.rect.topleft = STARTPOS['flyer']
            START.reverse_wall.rect.topleft = STARTPOS['reverse_wall']
            START.spring.rect.topleft = STARTPOS['spring']
            START.smily_robot.rect.topleft = STARTPOS['smily_robot']
            START.door.rect.topleft = STARTPOS['door']
            START.diamonds.rect.topleft = STARTPOS['diamonds']
            START.sticky_block.rect.topleft = STARTPOS['sticky_block']
            START.fall_spikes.rect.topleft = STARTPOS['fall_spikes']
            START.stand_spikes.rect.topleft = STARTPOS['stand_spikes']


                    
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        debug_message = 1
                        state = DEBUG
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                        
                #################
                # LEFT CLICK (PRESSED DOWN) at Top of Screen
                #################
                if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[1] < 48): 
                    # DRAG (only for menu and inanimate buttons at top)
                    if game_mode == EDIT_MODE:
                        # BUTTONS
                        if GRID_BUTTON.rect.collidepoint(MOUSEPOS):
                            if GRID_BUTTON.grid_on_var == 1:
                                GRID_BUTTON.grid_on_var = 0
                            else:
                                GRID_BUTTON.grid_on_var = 1
                        if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                            COLORKEY = get_color()
                        if SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            save_file(COLORKEY)
                        if LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            PLACED_SPRITES, COLORKEY = load_file(PLACED_SPRITES, COLORKEY)
                        # DRAG
                        # Restarts all drag objects
                        
                        if START.player.rect.collidepoint(MOUSEPOS):
                            # Checks for if there is already a player placed on level
                            if not PlacedPlayer.player_list:
                                DRAGGING.dragging_all_false()
                                START = restart_start_objects(START)
                                DRAGGING.player = True
                                START.blank_box.flip_start_sprite(DRAGGING, START.player.rect.topleft)
                            else:
                                print("Error: Too many players")
                        elif START.door.rect.collidepoint(MOUSEPOS):
                            if not PlacedDoor.door_list:
                                DRAGGING.dragging_all_false()
                                START = restart_start_objects(START)
                                DRAGGING.door = True
                                START.blank_box.flip_start_sprite(DRAGGING, START.door.rect.topleft)
                            else:
                                print("Error: Only one exit allowed")
                        elif START.wall.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.wall = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.wall.rect.topleft)
                        elif START.flyer.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.flyer = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.flyer.rect.topleft)
                        elif START.reverse_wall.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.reverse_wall = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.reverse_wall.rect.topleft)
                        elif START.spring.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.spring = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.spring.rect.topleft)
                        elif START.smily_robot.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.smily_robot = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.smily_robot.rect.topleft)
                        elif START.diamonds.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.diamonds = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.diamonds.rect.topleft)
                        elif START.sticky_block.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.sticky_block = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.sticky_block.rect.topleft)
                        elif START.fall_spikes.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.fall_spikes = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.fall_spikes.rect.topleft)
                        elif START.stand_spikes.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.stand_spikes = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.stand_spikes.rect.topleft)
                            
                #################
                # LEFT CLICK (PRESSED DOWN)
                #################
                elif event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                    # Place object on location of mouse release
                    if DRAGGING.player:
                        PlacedPlayer(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.door:
                        PlacedDoor(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.wall:
                        PlacedWall(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.flyer:
                        PlacedFlyer(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.reverse_wall:
                        PlacedReverseWall(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.smily_robot:
                        PlacedSmilyRobot(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.spring:
                        PlacedSpring(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.diamonds:
                        PlacedDiamonds(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.sticky_block:
                        PlacedStickyBlock(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.fall_spikes:
                        PlacedFallSpikes(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                    elif DRAGGING.stand_spikes:
                        PlacedStandSpikes(snap_to_grid(MOUSEPOS, SCREEN_WIDTH, SCREEN_HEIGHT), PLACED_SPRITES)
                        
                #################
                # CLICK (RELEASE)
                #################           
                if game_mode == EDIT_MODE:
                # Right click on obj, destroy
                    if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):   
                        DRAGGING.dragging_all_false()
                        START = restart_start_objects(START)
                        PLACED_SPRITES = remove_placed_object(PLACED_SPRITES, MOUSEPOS)
                if event.type == MOUSEBUTTONUP:            
                    #################
                    # PLAY BUTTON
                    #################
                    if(PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_mode == EDIT_MODE):
                        # Makes sure there is at least one player to play game
                        if PlacedPlayer.player_list:
                            # Makes clicking play again unclickable
                            game_mode = PLAY_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            print("Play Mode Activated")
                            #MUSIC_PLAYER = [MusicPlayer()]
                            for placed_player in PlacedPlayer.player_list:
                                PlayPlayer(placed_player.rect.topleft, PLAY_SPRITES)
                            for placed_door in PlacedDoor.door_list:
                                PlayDoor(placed_door.rect.topleft, PLAY_SPRITES)
                            for placed_wall in PlacedWall.wall_list:
                                PlayWall(placed_wall.rect.topleft, PLAY_SPRITES)
                            for placed_flyer in PlacedFlyer.flyer_list:
                                PlayFlyer(placed_flyer.rect.topleft, PLAY_SPRITES)
                            for placed_reverse_wall in PlacedReverseWall.reverse_wall_list:
                                PlayReverseWall(placed_reverse_wall.rect.topleft, PLAY_SPRITES)
                            for placed_smily_robot in PlacedSmilyRobot.smily_robot_list:
                                PlaySmilyRobot(placed_smily_robot.rect.topleft, PLAY_SPRITES)
                            for placed_spring_list in PlacedSpring.spring_list:
                                PlaySpring(placed_spring_list.rect.topleft, PLAY_SPRITES)
                            for placed_diamonds_list in PlacedDiamonds.diamonds_list:
                                PlayDiamonds(placed_diamonds_list.rect.topleft, PLAY_SPRITES)
                            for placed_sticky_block_list in PlacedStickyBlock.sticky_block_list:
                                PlayStickyBlock(placed_sticky_block_list.rect.topleft, PLAY_SPRITES)
                            for placed_fall_spikes_list in PlacedFallSpikes.fall_spikes_list:
                                PlayFallSpikes(placed_fall_spikes_list.rect.topleft, PLAY_SPRITES)
                            for placed_stand_spikes_list in PlacedStandSpikes.stand_spikes_list:
                                PlayStandSpikes(placed_stand_spikes_list.rect.topleft, PLAY_SPRITES)
                        else:
                            print("You need a character!")
                    #################
                    # LEFT CLICK (RELEASE) STOP BUTTON
                    #################
                    elif(PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_mode == PLAY_MODE):
                        # Makes sure you are not in editing mode to enter editing mode
                        if game_mode == PLAY_MODE:
                            print("Editing Mode Activated")
                            PlayPlayer.player_list[0].death_count = 0
                            game_mode = EDIT_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            remove_all_play()
                            #MUSIC_PLAYER = []
                            #MUSIC_PLAYER = [MusicPlayer()]
                    if RESTART_BUTTON.rect.collidepoint(MOUSEPOS):
                        if game_mode == PLAY_MODE:
                            restart_level()
                    if INFO_BUTTON.rect.collidepoint(MOUSEPOS):
                        MENUON = 2
                    if CLEAR_BUTTON.rect.collidepoint(MOUSEPOS):
                        if game_mode == EDIT_MODE: #Editing mode
                            START = restart_start_objects(START)
                            # REMOVE ALL SPRITES
                            remove_all_placed()
                    if ROTATE_BUTTON.rect.collidepoint(MOUSEPOS):
                        START.stand_spikes.rotate -= 90
                        
                #################
                # KEYBOARD EVENTS (PLAYER)
                #################
                if game_mode == PLAY_MODE:
                    if event.type == pygame.KEYUP:
                        if event.key == K_LEFT and PlayPlayer.player_list[0].speed_x < 0:
                            PlayPlayer.player_list[0].stop()
                        if event.key == pygame.K_RIGHT and PlayPlayer.player_list[0].speed_x > 0:
                            PlayPlayer.player_list[0].stop()
                    if event.type == KEYDOWN:
                        if event.key == pygame.K_UP:
                            if PlayPlayer.player_list[0].jumps_left > 0:
                                PlayPlayer.player_list[0].jump()
                                
            ##################
            # ALL EDIT ACTIONS
            ##################
            # Replace start sprite with blank box in top menu
            if game_mode == EDIT_MODE:
                if DRAGGING.player and not PlacedPlayer.player_list:
                    START.blank_box.rect.topleft = STARTPOS['player'] # Replaces in Menu
                    START.player.rect.topleft = (MOUSEPOS[0]-(START.player.image.get_width()/2),
                                                 MOUSEPOS[1]-(START.player.image.get_height()/3))
                else:
                    DRAGGING.player = False
                    START.player.rect.topleft = STARTPOS['player']
                if DRAGGING.wall:
                    START.blank_box.rect.topleft = STARTPOS['wall'] # Replaces in Menu
                    START.wall.rect.topleft = (MOUSEPOS[0]-(START.wall.image.get_width()/2),
                                               MOUSEPOS[1]-(START.wall.image.get_height()/2))
                else:
                    START.wall.rect.topleft = STARTPOS['wall']
                if DRAGGING.reverse_wall:
                    START.blank_box.rect.topleft = STARTPOS['reverse_wall'] # Replaces in Menu
                    START.reverse_wall.rect.topleft = (MOUSEPOS[0]-(START.reverse_wall.image.get_width()/2),
                                                       MOUSEPOS[1]-(START.reverse_wall.image.get_height()/2))
                else:
                    START.reverse_wall.rect.topleft = STARTPOS['reverse_wall']
                if DRAGGING.diamonds:
                    START.blank_box.rect.topleft = STARTPOS['diamonds'] # Replaces in Menu
                    START.diamonds.rect.topleft = (MOUSEPOS[0]-(START.diamonds.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.diamonds.image.get_height()/2))
                else:
                    START.diamonds.rect.topleft = STARTPOS['diamonds']
                if DRAGGING.door and not PlacedDoor.door_list:
                    START.blank_box.rect.topleft = STARTPOS['door'] # Replaces in Menu
                    START.door.rect.topleft = (MOUSEPOS[0]-(START.door.image.get_width()/2),
                                               MOUSEPOS[1]-(START.door.image.get_height()/4))
                    START.door.image = IMAGES["SPR_DOOR_CLOSED"]
                else:
                    START.door.rect.topleft = STARTPOS['door']
                    START.door.image = pygame.transform.smoothscale(IMAGES["SPR_DOOR_CLOSED"], (24, 40))
                if DRAGGING.flyer:
                    START.blank_box.rect.topleft = STARTPOS['flyer'] # Replaces in Menu
                    START.flyer.rect.topleft = (MOUSEPOS[0]-(START.flyer.image.get_width()/2),
                                                MOUSEPOS[1]-(START.flyer.image.get_height()/2))
                else:
                    START.flyer.rect.topleft = STARTPOS['flyer']
                if DRAGGING.smily_robot:
                    START.blank_box.rect.topleft = STARTPOS['smily_robot'] # Replaces in Menu
                    START.smily_robot.rect.topleft = (MOUSEPOS[0]-(START.smily_robot.image.get_width()/2),
                                                      MOUSEPOS[1]-(START.smily_robot.image.get_height()/2))
                else:
                    START.smily_robot.rect.topleft = STARTPOS['smily_robot']
                if DRAGGING.spring:
                    START.blank_box.rect.topleft = STARTPOS['spring'] # Replaces in Menu
                    START.spring.rect.topleft = (MOUSEPOS[0]-(START.spring.image.get_width()/2),
                                                 MOUSEPOS[1]-(START.spring.image.get_height()/2))
                else:
                    START.spring.rect.topleft = STARTPOS['spring']
                if DRAGGING.sticky_block:
                    START.blank_box.rect.topleft = STARTPOS['sticky_block'] # Replaces in Menu
                    START.sticky_block.rect.topleft = (MOUSEPOS[0]-(START.sticky_block.image.get_width()/2),
                                                       MOUSEPOS[1]-(START.sticky_block.image.get_height()/2))
                else:
                    START.sticky_block.rect.topleft = STARTPOS['sticky_block']
                if DRAGGING.fall_spikes:
                    START.blank_box.rect.topleft = STARTPOS['fall_spikes'] # Replaces in Menu
                    START.fall_spikes.rect.topleft = (MOUSEPOS[0]-(START.fall_spikes.image.get_width()/2),
                                                      MOUSEPOS[1]-(START.fall_spikes.image.get_height()/2))
                else:
                    START.fall_spikes.rect.topleft = STARTPOS['fall_spikes']
                if START.stand_spikes.rotate == 0:
                    START.stand_spikes.image = IMAGES["SPR_STANDSPIKES"]
                else:
                    START.stand_spikes.image = pygame.transform.rotate(IMAGES["SPR_STANDSPIKES"], START.stand_spikes.rotate)
                if DRAGGING.stand_spikes:
                    START.blank_box.rect.topleft = STARTPOS['stand_spikes'] # Replaces in Menu
                    START.stand_spikes.rect.topleft = (MOUSEPOS[0]-(START.stand_spikes.image.get_width()/2),
                                                       MOUSEPOS[1]-(START.stand_spikes.image.get_height()/2))
                else:
                    START.stand_spikes.rect.topleft = STARTPOS['stand_spikes']
                    
            ##################
            # IN-GAME ACTIONS
            ##################
            if game_mode == PLAY_MODE:
                
                # Avoid player going off screen
                KEYS_PRESSED = pygame.key.get_pressed()
                if KEYS_PRESSED[K_LEFT]:
                    PlayPlayer.player_list[0].last_pressed_r = 0
                    if PlayPlayer.player_list[0].rect.left > 0:
                        PlayPlayer.player_list[0].go_left()
                    else:
                        PlayPlayer.player_list[0].stop()
                if KEYS_PRESSED[K_RIGHT]:
                    PlayPlayer.player_list[0].last_pressed_r = 1
                    if PlayPlayer.player_list[0].rect.right < SCREEN_WIDTH:
                        PlayPlayer.player_list[0].go_right()
                    else:
                        PlayPlayer.player_list[0].stop()
                # Dead
                if PlayPlayer.player_list[0].rect.top > SCREEN_HEIGHT and PlayPlayer.player_list[0].speed_y >= 0:
                    restart_level()
                # Spikes fall when player goes underneath
                if PlayFallSpikes.fall_spikes_list:
                    for fall_spike in PlayFallSpikes.fall_spikes_list:
                        if(PlayPlayer.player_list[0].rect.right > fall_spike.rect.left and
                           PlayPlayer.player_list[0].rect.left < fall_spike.rect.right and
                           PlayPlayer.player_list[0].rect.top > fall_spike.rect.bottom):
                            fall_spike.fall_var = 1
                        if fall_spike.fall_var == 1:
                            fall_spike.rect.top = fall_spike.rect.top + 5
                # Player wins when he captures all jewels and enters door
                if PlayDoor.door_list:
                    PlayDoor.door_list[0].image = PlayDoor.door_list[0].open_or_close(PlayPlayer.player_list[0].score, PlayDiamonds.diamonds_list)
                    if pygame.sprite.collide_mask(PlayPlayer.player_list[0], PlayDoor.door_list[0]):
                        if PlayPlayer.player_list[0].score == len(PlayDiamonds.diamonds_list):
                            print("You Win!")
                            PlayPlayer.player_list[0].death_count = 0
                            game_mode = EDIT_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            #music_player = [MusicPlayer()]
                            PlayPlayer.player_list[0].rect.topleft = PlacedPlayer.player_list[0].rect.topleft
                            for i in range(0, len(PlacedSmilyRobot.smily_robot_list)):
                                PlaySmilyRobot.smily_robot_list[i].rect.topleft = PlacedSmilyRobot.smily_robot_list[i].rect.topleft
                                PlaySmilyRobot.smily_robot_list[i].speed_y = 0
                            for i in range(0, len(PlacedFlyer.flyer_list)):
                                PlayFlyer.flyer_list[i].rect.topleft = PlacedFlyer.flyer_list[i].rect.topleft
                            for play_diamonds in PlayDiamonds.diamonds_list:
                                play_diamonds.image = IMAGES["SPR_DIAMONDS"]
                            for i in range(0, len(PlacedFallSpikes.fall_spikes_list)):
                                PlayFallSpikes.fall_spikes_list[i].rect.topleft = PlacedFallSpikes.fall_spikes_list[i].rect.topleft
                                PlayFallSpikes.fall_spikes_list[i].fall_var = 0
                            

                        
                #####################
                # COLLISIONS
                #####################
                for play_smily_robot in PlaySmilyRobot.smily_robot_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_smily_robot.rect):
                        if(PlayPlayer.player_list[0].rect.bottom <= play_smily_robot.rect.top + 10 and PlayPlayer.player_list[0].speed_y >= 0):
                            play_smily_robot.rect.topleft = (0, -100)
                            PlayPlayer.player_list[0].propeller = 0
                            PlayPlayer.player_list[0].speed_y = -4
                            PlayPlayer.player_list[0].jumps_left = 1 #Allows propeller in air
                        elif(PlayPlayer.player_list[0].rect.right-play_smily_robot.rect.left <= 10 and
                             PlayPlayer.player_list[0].rect.bottom > play_smily_robot.rect.top + 10):
                            restart_level()
                        elif(PlayPlayer.player_list[0].rect.left-play_smily_robot.rect.right <= 10 and
                             PlayPlayer.player_list[0].rect.bottom > play_smily_robot.rect.top + 10):
                            restart_level()
                for play_flyer in PlayFlyer.flyer_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_flyer.rect):
                        restart_level()
                for play_fall_spikes in PlayFallSpikes.fall_spikes_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_fall_spikes.rect):
                        restart_level()
                for play_stand_spikes in PlayStandSpikes.stand_spikes_list:
                    if PlayPlayer.player_list[0].rect.colliderect(play_stand_spikes.rect):
                        restart_level()
                for play_diamonds in PlayDiamonds.diamonds_list:
                    if pygame.sprite.collide_mask(PlayPlayer.player_list[0], play_diamonds):
                        PlayPlayer.player_list[0].score += 1
                        play_diamonds.image = IMAGES["SPR_BLANKBOX"]
                for spring in PlaySpring.spring_list:
                    if pygame.sprite.collide_mask(PlayPlayer.player_list[0], spring):
                        if PlayPlayer.player_list[0].rect.bottom <= spring.rect.top+20 and PlayPlayer.player_list[0].speed_y >= 10: #big jumps
                            SOUNDS["SND_SPRING"].play()
                            PlayPlayer.player_list[0].propeller = 0 
                            PlayPlayer.player_list[0].rect.bottom = spring.rect.top
                            PlayPlayer.player_list[0].speed_y = -10
                            PlayPlayer.player_list[0].jumps_left = 1 #Allows propeller in air
                        elif PlayPlayer.player_list[0].rect.bottom <= spring.rect.top+10 and PlayPlayer.player_list[0].speed_y >= 0:
                            SOUNDS["SND_SPRING"].play()
                            PlayPlayer.player_list[0].propeller = 0 #Fixes propeller bug
                            PlayPlayer.player_list[0].rect.bottom = spring.rect.top
                            PlayPlayer.player_list[0].speed_y = -10
                            PlayPlayer.player_list[0].jumps_left = 1 #Allows propeller in air
                        elif PlayPlayer.player_list[0].speed_x > 0:
                            PlayPlayer.player_list[0].rect.right = spring.rect.left
                        elif PlayPlayer.player_list[0].speed_x < 0:
                            PlayPlayer.player_list[0].rect.left = spring.rect.right
                        elif PlayPlayer.player_list[0].speed_y < 0:
                            PlayPlayer.player_list[0].speed_y = 0
                            PlayPlayer.player_list[0].propeller = 0
                            PlayPlayer.player_list[0].rect.top = spring.rect.bottom #Below the wall
            #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
            
            SCREEN.fill(COLORKEY)

            #Update all sprites
            START_SPRITES.update()
            PLACED_SPRITES.update()
            PLAY_SPRITES.update()
            GAME_MODE_SPRITES.draw(SCREEN)
            if game_mode == EDIT_MODE: #Only draw placed sprites in editing mode
                if GRID_BUTTON.grid_on_var == 1:
                    GRID_SPRITES.draw(SCREEN)
                START_SPRITES.draw(SCREEN)
                PLACED_SPRITES.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("", 1, (0, 0, 0))
            elif game_mode == PLAY_MODE: #Only draw play sprites in play mode
                PLAY_SPRITES.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("Deaths: " + str(PlayPlayer.player_list[0].death_count), 1, (0, 0, 0))
            SCREEN.blit(DEATH_COUNT_TEXT, ((SCREEN_WIDTH/2-50), 5))
            
            pygame.display.update()
        elif MENUON == 2: # Info SCREEN in a WHILE loop
            InfoScreen(INFO_SCREEN, SCREEN)
            MENUON = 1
        elif state == DEBUG:
            if debug_message == 1:
                print("Entering debug mode")
                debug_message = 0
                # USE BREAKPOINT HERE
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        state = RUNNING
        
if __name__ == "__main__":
    main()