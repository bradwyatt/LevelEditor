"""
Propeller Platformer: Level Editor created by Brad Wyatt
"""
import random
import time
import sys
import os
import copy
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
from ast import literal_eval
import pygame
from pygame.constants import RLEACCEL
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, IMAGES, SOUNDS, MOBILE_ACCESSIBILITY_MODE, load_image, load_sound
from ui import ClearButton, InfoButton, EraserButton, RestartButton, GridButton, SaveFileButton, LoadFileButton
from start_objects import StartWall, StartReverseWall, StartDiamonds, StartDoor, StartFlyer, StartSmilyRobot, StartSpring, StartPlayer, StartStickyBlock, StartFallSpikes, StartStandSpikes, RotateButton
from placed_objects import PlacedWall, PlacedReverseWall, PlacedDiamonds, PlacedDoor, PlacedFlyer, PlacedSmilyRobot, PlacedSpring, PlacedStickyBlock, PlacedFallSpikes, PlacedStandSpikes, PlacedPlayer
from play_objects import PlayWall, PlayReverseWall, PlayFlyer, PlayDiamonds, PlayDoor, PlaySmilyRobot, PlayStickyBlock, PlayStandSpikes, PlayFallSpikes, PlaySpring, PlayPlayer

# Initialize pygame
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # pygame.FULLSCREEN for fullSCREEN
GAME_ICON = pygame.image.load("sprites/player_ico.png")
pygame.display.set_icon(GAME_ICON)
pygame.display.set_caption('Level Editor')
clock = pygame.time.Clock()

def create_transparent_surface(width, height):
    """
    Creates a transparent surface of the specified size.
    :param width: Width of the surface.
    :param height: Height of the surface.
    :return: A transparent surface.
    """
    transparent_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    transparent_surface.fill((0, 0, 0, 0))  # Fill with complete transparency
    return transparent_surface

def load_all_assets():
    #Sprites
    IMAGES['spr_dynamic_object_placeholder'] = create_transparent_surface(24, 24)  # Assuming 24x24 is the size for dynamic object placeholder
    load_image("sprites/door_closed.png", "spr_door_closed", True)
    IMAGES['spr_door_closed_start'] = pygame.transform.scale(IMAGES['spr_door_closed'], (48, 72))
    load_image("sprites/door_open.png", "spr_door_open", True)
    load_image("sprites/diamond.png", "spr_diamonds", True)
    IMAGES['spr_diamonds_start'] = pygame.transform.scale(IMAGES['spr_diamonds'], (48, 48))
    load_image("sprites/wall.png", "spr_wall", True)
    IMAGES['spr_wall_start'] = pygame.transform.scale(IMAGES['spr_wall'], (48, 48))
    load_image("sprites/reverse_wall.png", "spr_reverse_wall", True)
    IMAGES['spr_reverse_wall_start'] = pygame.transform.scale(IMAGES['spr_reverse_wall'], (48, 48))
    load_image("sprites/flyer.png", "spr_flyer", True)
    IMAGES['spr_flyer_start'] = pygame.transform.scale(IMAGES['spr_flyer'], (48, 48))
    load_image("sprites/spring.png", "spr_spring", True)
    IMAGES['spr_spring_start'] = pygame.transform.scale(IMAGES['spr_spring'], (48, 48))
    load_image("sprites/smily_robot_1.png", "spr_smily_robot", True)
    IMAGES['spr_smily_robot_start'] = pygame.transform.scale(IMAGES['spr_smily_robot'], (48, 48))
    load_image("sprites/smily_robot_2.png", "spr_smily_robot_2", True)
    load_image("sprites/sticky_block.png", "spr_sticky_block", True)
    IMAGES['spr_sticky_block_start'] = pygame.transform.scale(IMAGES['spr_sticky_block'], (48, 48))
    load_image("sprites/fall_spikes.png", "spr_fall_spikes", True)
    IMAGES['spr_fall_spikes_start'] = pygame.transform.scale(IMAGES['spr_fall_spikes'], (48, 48))
    load_image("sprites/stand_spikes.png", "spr_stand_spikes_0_degrees", True)
    IMAGES['spr_stand_spikes_90_degrees'] = pygame.transform.rotate(IMAGES["spr_stand_spikes_0_degrees"], -90)
    IMAGES['spr_stand_spikes_180_degrees'] = pygame.transform.rotate(IMAGES["spr_stand_spikes_0_degrees"], -180)
    IMAGES['spr_stand_spikes_270_degrees'] = pygame.transform.rotate(IMAGES["spr_stand_spikes_0_degrees"], -270)
    IMAGES['spr_stand_spikes_0_degrees_start'] = pygame.transform.scale(IMAGES['spr_stand_spikes_0_degrees'], (48, 48))
    IMAGES['spr_stand_spikes_90_degrees_start'] = pygame.transform.scale(IMAGES['spr_stand_spikes_90_degrees'], (48,48))
    IMAGES['spr_stand_spikes_180_degrees_start'] = pygame.transform.scale(IMAGES['spr_stand_spikes_180_degrees'], (48,48))
    IMAGES['spr_stand_spikes_270_degrees_start'] = pygame.transform.scale(IMAGES['spr_stand_spikes_270_degrees'], (48,48))
    load_image("sprites/player.png", "spr_player", True)
    IMAGES['spr_player_start'] = pygame.transform.scale(IMAGES['spr_player'], (40, 72))
    load_image("sprites/player_propeller.png", "spr_player_propeller", True)
    load_image("sprites/play_button.png", "spr_play_button", True)
    load_image("sprites/stop_button.png", "spr_stop_button", True)
    load_image("sprites/clear.png", "spr_clear_button", True)
    load_image("sprites/info_button.png", "spr_info_button", True)
    load_image("sprites/grid_button.png", "spr_grid_button", True)
    load_image("sprites/restart.png", "spr_restart_button", True)
    load_image("sprites/save_file.png", "spr_save_file_button", True)
    load_image("sprites/load_file.png", "spr_load_file_button", True)
    load_image("sprites/rotate.png", "spr_rotate_button", True)
    load_image("sprites/grid.png", "spr_grid", True)
    load_image("sprites/eraser_not_selected_button.png", "spr_eraser_not_selected_button", True)
    load_image("sprites/eraser_selected_button.png", "spr_eraser_selected_button", True)
    load_image("sprites/eraser_cursor.png", "spr_eraser_cursor", True)
    
    load_image("sprites/blue_left_arrow.png", "spr_blue_left_arrow", True)
    load_image("sprites/blue_left_arrow_active.png", "spr_blue_left_arrow_active", True)

    load_image("sprites/blue_right_arrow.png", "spr_blue_right_arrow", True)
    load_image("sprites/blue_right_arrow_active.png", "spr_blue_right_arrow_active", True)

    load_image("sprites/jump_button.png", "spr_jump_button", True)
    load_image("sprites/jump_button_active.png", "spr_jump_button_active", True)



    
    #SOUNDS
    load_sound("sounds/propeller.wav", "snd_propeller")
    SOUNDS["snd_propeller"].set_volume(.15)
    load_sound("sounds/spring.wav", "snd_spring")
    SOUNDS["snd_spring"].set_volume(.15)

def snap_to_grid(pos, screen_width, screen_height, grid_spacing, top_ui_boundary_y_height, left_ui_boundary_x_width=0):
    """
    Adjusts a given position to the top-left corner of the nearest grid cell, considering both top and left UI boundaries.
    
    :param pos: A tuple (x, y) representing the position to adjust.
    :param screen_width: Width of the screen or canvas.
    :param screen_height: Height of the screen or canvas.
    :param grid_spacing: The size of each grid cell.
    :param top_ui_boundary_y_height: The Y-coordinate from where the grid starts.
    :param left_ui_boundary_x_width: The X-coordinate from where the grid starts. Default is 0 if not specified.
    :return: A tuple (adjusted_x, adjusted_y) representing the adjusted position.
    """
    # Calculate column and row in the grid based on the position, including left offset
    col = max(0, (pos[0] - left_ui_boundary_x_width) // grid_spacing)
    row = max(0, (pos[1] - top_ui_boundary_y_height) // grid_spacing)

    # Calculate the adjusted position
    adjusted_x = col * grid_spacing + left_ui_boundary_x_width
    adjusted_y = row * grid_spacing + top_ui_boundary_y_height

    return adjusted_x, adjusted_y

def InfoScreen(info_screen, screen):
    screen.blit(info_screen, (0, 0))  # Display the Info Screen image

def draw_yellow_outline(screen, sprite_or_image, position, thickness=2):
    # Determine if we have a sprite or a direct image
    if hasattr(sprite_or_image, 'rect'):
        # It's a sprite
        rect = sprite_or_image.rect
    else:
        # It's a direct image; use position and image dimensions to create a rect
        rect = pygame.Rect(position[0], position[1], sprite_or_image.get_width(), sprite_or_image.get_height())
    
    # Draw the rectangle outline
    pygame.draw.rect(screen, pygame.Color('yellow'), rect, thickness)

def remove_placed_object(placed_sprites, mouse_pos, game_state):
    # Iterate over all lists except the player list, which is handled separately now.
    for placed_item_list in (PlacedWall.wall_list, PlacedFlyer.flyer_list,
                             PlacedSpring.spring_list, PlacedDiamonds.diamonds_list, PlacedReverseWall.reverse_wall_list,
                             PlacedSmilyRobot.smily_robot_list, PlacedStickyBlock.sticky_block_list,
                             PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(mouse_pos):
                placed_sprites.remove(placed_item)
                placed_item_list.remove(placed_item)

    # Check if the placed player exists and if the mouse position collides with it.
    if game_state.placed_player and game_state.placed_player.rect.collidepoint(mouse_pos):
        placed_sprites.remove(game_state.placed_player)
        game_state.placed_player = None  # Directly set the player to None since it's no longer a list.
    if game_state.placed_door and game_state.placed_door.rect.collidepoint(mouse_pos):
        placed_sprites.remove(game_state.placed_door)
        game_state.placed_door = None  # Directly set the player to None since it's no longer a list.

    return placed_sprites


def restart_start_objects(start, start_positions):
    start.player.rect.topleft = start_positions['player']
    start.wall.rect.topleft = start_positions['wall']
    start.reverse_wall.rect.topleft = start_positions['reverse_wall']
    start.spring.rect.topleft = start_positions['spring']
    start.flyer.rect.topleft = start_positions['flyer']
    start.smily_robot.rect.topleft = start_positions['smily_robot']
    start.door.rect.topleft = start_positions['door']
    start.diamonds.rect.topleft = start_positions['diamonds']
    start.sticky_block.rect.topleft = start_positions['sticky_block']
    start.fall_spikes.rect.topleft = start_positions['fall_spikes']
    start.stand_spikes.rect.topleft = start_positions['stand_spikes']
    return start

def load_file(PLACED_SPRITES, game_state):
    request_file_name = askopenfilename(defaultextension=".lvl")
    open_file = open(request_file_name, "r")
    loaded_file = open_file.read()
    loaded_dict = literal_eval(loaded_file)
            
    game_state.play_player.destroy()
    game_state.play_door.destroy()
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
    remove_all_placed(game_state)
    
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
        #%% This needs to be changed in the future
        PlacedStandSpikes(stand_spikes_pos, PLACED_SPRITES)
    
    print("File Loaded")
    return PLACED_SPRITES

def save_file():
    try:
        if GameState.placed_player and GameState.placed_door:
            # default extension is optional, here will add .txt if missing
            save_file_prompt = asksaveasfilename(defaultextension=".lvl")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                obj_locations = copy.deepcopy(get_dict_rect_positions())
                save_file_name.write(str(obj_locations))
                save_file_name.close()
                print("File Saved Successfully.")
        else:
            print("Error! Need player and door to save!")
    except IOError:
        print("Save File Error, please restart game and try again.")
            
def draw_grid(screen, grid_spacing, screen_width, screen_height, top_ui_boundary_y_height, horizontal_offset):
    """
    Draws a grid on the screen with equal horizontal offsets on both sides.

    :param screen: The Pygame screen object where the grid will be drawn.
    :param grid_spacing: The spacing between each grid line, defining the size of grid cells.
    :param screen_width: The width of the screen or canvas.
    :param screen_height: The height of the screen or canvas.
    :param top_ui_boundary_y_height: The Y-coordinate from where the grid should start, to avoid UI overlap.
    :param horizontal_offset: The horizontal offset from the sides of the screen.
    """
    # Set the color of the grid lines
    grid_color = (0, 0, 0)  # Black

    # Calculate the drawable area considering offsets and top UI boundary
    drawable_width = screen_width - 2 * horizontal_offset
    drawable_height = screen_height - top_ui_boundary_y_height

    # Calculate the number of complete vertical and horizontal cells that fit within the drawable area
    num_complete_vertical_cells = drawable_width // grid_spacing
    num_complete_horizontal_cells = drawable_height // grid_spacing

    # Calculate the adjusted width and height to only include complete cells
    adjusted_width = num_complete_vertical_cells * grid_spacing
    adjusted_height = num_complete_horizontal_cells * grid_spacing

    # Draw vertical lines
    for i in range(num_complete_vertical_cells + 1):  # +1 to draw the last line on the right
        x_position = i * grid_spacing + horizontal_offset
        pygame.draw.line(screen, grid_color, (x_position, top_ui_boundary_y_height), (x_position, top_ui_boundary_y_height + adjusted_height))

    # Draw horizontal lines
    for j in range(num_complete_horizontal_cells + 1):  # +1 to draw the last line at the bottom
        y_position = j * grid_spacing + top_ui_boundary_y_height
        pygame.draw.line(screen, grid_color, (horizontal_offset, y_position), (horizontal_offset + adjusted_width, y_position))



class ArrowButton(pygame.sprite.Sprite):
    def __init__(self, play_sprites, images, direction):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.direction = direction
        if direction == "left":
            self.image_inactive = images["spr_blue_left_arrow"]
            self.image_active = images["spr_blue_left_arrow_active"]
        elif direction == "right":
            self.image_inactive = images["spr_blue_right_arrow"]
            self.image_active = images["spr_blue_right_arrow_active"]
        self.image = self.image_inactive
        self.rect = self.image.get_rect()
        if direction == "left":
            self.rect.topleft = (20, SCREEN_HEIGHT-210)
        elif direction == "right":
            self.rect.topleft = (130, SCREEN_HEIGHT-210)
        play_sprites.add(self)
    
    def set_active(self, active):
        self.image = self.image_active if active else self.image_inactive

        
class JumpButton(pygame.sprite.Sprite):
    def __init__(self, play_sprites, images):
        pygame.sprite.Sprite.__init__(self)
        self.image_inactive = images["spr_jump_button"]
        self.image_active = images["spr_jump_button_active"]
        self.image = self.image_inactive
        self.rect = self.image.get_rect()
        self.rect.topleft = (SCREEN_WIDTH-230, SCREEN_HEIGHT-235)
        play_sprites.add(self)
    
    def set_active(self, active):
        self.image = self.image_active if active else self.image_inactive


class StartDynamicObjectPlaceholder(pygame.sprite.Sprite):
    def __init__(self, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = images["spr_dynamic_object_placeholder"]
        self.rect = self.image.get_rect()
        
    def update(self):
        pass
    def reset(self):
        self.image = self.images["spr_dynamic_object_placeholder"]
    def start_sprite_with_yellow_outline(self, selected_object_type, pos, images, rotate=0):
        self.rect.topleft = pos
        if selected_object_type == "player":
            self.image = images["spr_player_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_player_start", pos)
        elif selected_object_type == "door":
            self.image = images["spr_door_closed_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_door_closed_start", pos)
        elif selected_object_type == "wall":
            self.image = images["spr_wall_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_wall_start", pos)
        elif selected_object_type == "diamonds":
            self.image = images["spr_diamonds_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_diamonds_start", pos)
        elif selected_object_type == "flyer":
            self.image = images["spr_flyer_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_flyer_start", pos)
        elif selected_object_type == "reverse_wall":
            self.image = images["spr_reverse_wall_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_reverse_wall_start", pos)
        elif selected_object_type == "smily_robot":
            self.image = images["spr_smily_robot_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_smily_robot_start", pos)
        elif selected_object_type == "spring":
            self.image = images["spr_spring_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_spring_start", pos)
        elif selected_object_type == "sticky_block":
            self.image = images["spr_sticky_block_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_sticky_block_start", pos)
        elif selected_object_type == "fall_spikes":
            self.image = images["spr_fall_spikes_start"]
            GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_fall_spikes_start", pos)
        elif selected_object_type == "stand_spikes":
            if rotate == 0:
                self.image = images["spr_stand_spikes_0_degrees_start"]
                GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_stand_spikes_0_degrees_start", pos)
            elif rotate == 90:
                self.image = images["spr_stand_spikes_90_degrees_start"]
                GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_stand_spikes_90_degrees_start", pos)
            elif rotate == 180:
                self.image = images["spr_stand_spikes_180_degrees_start"]
                GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_stand_spikes_180_degrees_start", pos)
            elif rotate == 270:
                self.image = images["spr_stand_spikes_270_degrees_start"]
                GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = ("spr_stand_spikes_270_degrees_start", pos)
        else:
            self.image = images["spr_dynamic_object_placeholder"]

class PlayEditSwitchButton(pygame.sprite.Sprite):
    def __init__(self, pos, GAME_MODE_SPRITES, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = images["spr_play_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GAME_MODE_SPRITES.add(self)
    def game_mode_button(self, game_mode):
        if game_mode == GameState.PLAY_MODE:
            self.image = self.images["spr_stop_button"]
        elif game_mode == GameState.EDIT_MODE:
            self.image = self.images["spr_play_button"]
        return self.image

class MusicPlayer():
    def __init__(self, game_mode):
        if game_mode == 1:
            pygame.mixer.music.load("Sounds/play_music.mp3")
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load("Sounds/editing_mode.wav")
            pygame.mixer.music.play(-1)

class Grid(pygame.sprite.Sprite):
    grid_list = []
    ALL_GRIDS_ENABLED = True
    GRID_SPACING = 23
    def __init__(self, GRID_SPRITES, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_grid"]
        self.rect = self.image.get_rect()
        GRID_SPRITES.add(self)
        if self.rect.bottom > SCREEN_HEIGHT:
            GRID_SPRITES.remove(self)
        if self.rect.right > SCREEN_WIDTH:
            GRID_SPRITES.remove(self)
        Grid.grid_list.append(self)


class Dragging():
    def __init__(self):
        self.dragging_all_false()
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
    def __init__(self, start_sprites, start_positions):
        self.dynamic_object_placeholder = StartDynamicObjectPlaceholder(IMAGES)
        start_sprites.add(self.dynamic_object_placeholder)
        self.player = StartPlayer(start_positions['player'], IMAGES)
        start_sprites.add(self.player)
        self.wall = StartWall(start_positions['wall'], IMAGES)
        start_sprites.add(self.wall)
        self.flyer = StartFlyer(start_positions['flyer'], IMAGES)
        start_sprites.add(self.flyer)
        self.reverse_wall = StartReverseWall(start_positions['reverse_wall'], IMAGES)
        start_sprites.add(self.reverse_wall)
        self.spring = StartSpring(start_positions['spring'], IMAGES)
        start_sprites.add(self.spring)
        self.smily_robot = StartSmilyRobot(start_positions['smily_robot'], IMAGES)
        start_sprites.add(self.smily_robot)
        self.door = StartDoor(start_positions['door'], IMAGES)
        start_sprites.add(self.door)
        self.diamonds = StartDiamonds(start_positions['diamonds'], IMAGES)
        start_sprites.add(self.diamonds)
        self.sticky_block = StartStickyBlock(start_positions['sticky_block'], IMAGES)
        start_sprites.add(self.sticky_block)
        self.fall_spikes = StartFallSpikes(start_positions['fall_spikes'], IMAGES)
        start_sprites.add(self.fall_spikes)
        self.stand_spikes = StartStandSpikes(start_positions['stand_spikes'], IMAGES)
        start_sprites.add(self.stand_spikes)
        
class NotificationManager:
    def __init__(self):
        self.messages = []

    def add_message(self, text, duration, position, font, color=(255, 0, 0)):
        """ Adds a message to the queue. Duration in seconds. """
        message = {'text': text, 'duration': duration, 'position': position, 'font': font, 'color': color, 'start_time': pygame.time.get_ticks()}
        self.messages.append(message)

    def draw_messages(self, screen):
        """ Draws all messages that are still active. """
        current_time = pygame.time.get_ticks()
        active_messages = []
        for message in self.messages:
            if current_time - message['start_time'] < message['duration'] * 1000:  # Convert seconds to milliseconds
                text_surface = message['font'].render(message['text'], True, message['color'])
                text_rect = text_surface.get_rect(center=message['position'])
                screen.blit(text_surface, text_rect)
                active_messages.append(message)  # Keep this message for the next frame
        self.messages = active_messages  # Only keep active messages

class GameState:
    EDIT_MODE, PLAY_MODE = 0, 1
    START_POSITIONS = {'player': (10, 4), 'wall': (270, 12), 'reverse_wall': (405, 12),
                'spring': (205, 12), 'flyer': (525, 12), 'smily_robot': (465, 12),
                'door': (75, 2), 'diamonds': (140, 14), 'sticky_block': (337, 12),
                'fall_spikes': (590, 12), 'stand_spikes': (650, 12)}
    UI_ELEMENTS_POSITIONS = {'play_edit_switch_button': (SCREEN_WIDTH-80, 8),
                             'eraser_button': (SCREEN_WIDTH-250, 7),
                             'clear_button': (SCREEN_WIDTH-250, 300),
                             'info_button': (SCREEN_WIDTH-250, 100),
                             'grid_button': (SCREEN_WIDTH-250, 200),
                             'restart_button': (SCREEN_WIDTH-175, 10),
                             'save_file_button': (SCREEN_WIDTH-425, 10),
                             'load_file_button': (SCREEN_WIDTH-390, 10),
                             'rotate_button': (700, 7)}
    TOP_UI_BOUNDARY_Y_HEIGHT = 90
    HORIZONTAL_GRID_OFFSET = 250
    BOTTOM_Y_GRID_OFFSET = 5
    DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = None
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.grid_sprites = pygame.sprite.Group()
        self.start_sprites = pygame.sprite.Group()
        self.play_sprites = pygame.sprite.Group()
        self.game_mode_sprites = pygame.sprite.Group()
        self.placed_sprites = pygame.sprite.Group()
        self.dragging = Dragging()
        self.start = Start(self.start_sprites, self.START_POSITIONS)
        self.game_mode = GameState.EDIT_MODE
        self.mouse_pos = (0, 0)
        
        self.jump_key_released = True 
        
        self.placed_player = None
        self.play_player = None
        self.placed_door = None
        self.play_door = None
        self.is_paused = False
        
        self.is_dragging = False  # Initialize dragging state
        self.last_placed_pos = None  # Track the last placed position to avoid duplicates
        
        self.is_an_object_currently_being_dragged = False
        
        self.eraser_mode_active = False
        self.init_ui_elements()
        
        # Initialize mouse and movement states
        self.mouse_button_down = False
        self.moving_left = False
        self.moving_right = False
        self.want_to_jump = False
        self.jump_key_released = True
        self.jumping = False
        
        self.selected_object_type = None
        
        self.notification_manager = NotificationManager()


    def update_mouse_pos(self):
        self.mouse_pos = pygame.mouse.get_pos()
        
    def is_object_at_position(self, position):
        for sprite in self.placed_sprites:
            if sprite.rect.topleft == position:
                return True
        return False
    def init_ui_elements(self):
        self.play_edit_switch_button = PlayEditSwitchButton(self.UI_ELEMENTS_POSITIONS['play_edit_switch_button'],
                                                            self.game_mode_sprites,
                                                            IMAGES)
        self.clear_button = ClearButton(self.UI_ELEMENTS_POSITIONS['clear_button'], IMAGES)
        self.start_sprites.add(self.clear_button)
        self.eraser_button = EraserButton(self.UI_ELEMENTS_POSITIONS['eraser_button'], self.eraser_mode_active, IMAGES)
        self.start_sprites.add(self.eraser_button)
        self.info_button = InfoButton(self.UI_ELEMENTS_POSITIONS['info_button'], IMAGES)
        self.start_sprites.add(self.info_button)
        self.grid_button = GridButton(self.UI_ELEMENTS_POSITIONS['grid_button'], IMAGES)
        self.start_sprites.add(self.grid_button)
        self.restart_button = RestartButton(self.UI_ELEMENTS_POSITIONS['restart_button'], self.play_sprites, IMAGES)
        if not MOBILE_ACCESSIBILITY_MODE:
            self.save_file_button = SaveFileButton(self.UI_ELEMENTS_POSITIONS['save_file_button'], IMAGES)
            self.start_sprites.add(self.save_file_button)
            self.load_file_button = LoadFileButton(self.UI_ELEMENTS_POSITIONS['load_file_button'], IMAGES)
            self.start_sprites.add(self.load_file_button)
        self.rotate_button = RotateButton(self.UI_ELEMENTS_POSITIONS['rotate_button'], IMAGES)
        self.start_sprites.add(self.rotate_button)
            
    def reset_movement_flags(self, pos):
        if self.left_arrow_button.rect.collidepoint(pos):
            self.moving_left = False
        elif self.right_arrow_button.rect.collidepoint(pos):
            self.moving_right = False
        self.want_to_jump = False  # Stop jumping when any button is released
        
    def update_movement_directions_based_on_mouse_position(self, pos):
        self.moving_left = self.left_arrow_button.rect.collidepoint(pos)
        self.moving_right = self.right_arrow_button.rect.collidepoint(pos)
        # No jump updates here since jumping is a one-time action per click
        
    def interpolate_positions(self, start, end, grid_spacing):
        """Generate positions between start and end points on the grid."""
        interpolated_positions = []
        # Calculate steps needed based on the maximum difference in grid coordinates
        max_steps = max(abs(end[0] - start[0]), abs(end[1] - start[1])) // grid_spacing
        dx = (end[0] - start[0]) / max(1, max_steps)
        dy = (end[1] - start[1]) / max(1, max_steps)
    
        for step in range(max_steps + 1):
            next_pos = (start[0] + step * dx, start[1] + step * dy)
            # Snap each intermediate position to the grid
            snapped_pos = snap_to_grid(next_pos, SCREEN_WIDTH, SCREEN_HEIGHT, Grid.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT, GameState.HORIZONTAL_GRID_OFFSET)
            if snapped_pos not in interpolated_positions:
                interpolated_positions.append(snapped_pos)
    
        return interpolated_positions
    
    # Assume place_object_at_position is a method that places the selected object at the given grid position
    def place_object_at_position(self, position, object_type):
        """Place an object of the specified type at the given grid position."""
        if object_type == "player" and not self.placed_player:
            self.placed_player = PlacedPlayer(position, self.placed_sprites, IMAGES)
        elif object_type == "door" and not self.placed_door:
            self.placed_door = PlacedDoor(position, self.placed_sprites, IMAGES)
        elif object_type == 'wall':
            PlacedWall(position, self.placed_sprites, IMAGES)
        elif object_type == 'flyer':
            PlacedFlyer(position, self.placed_sprites, IMAGES)
        elif object_type == 'reverse_wall':
            PlacedReverseWall(position, self.placed_sprites, IMAGES)
        elif object_type == 'spring':
            PlacedSpring(position, self.placed_sprites, IMAGES)
        elif object_type == 'smily_robot':
            PlacedSmilyRobot(position, self.placed_sprites, IMAGES)
        elif object_type == 'diamonds':
            PlacedDiamonds(position, self.placed_sprites, IMAGES)
        elif object_type == 'sticky_block':
            PlacedStickyBlock(position, self.placed_sprites, IMAGES)
        elif object_type == 'fall_spikes':
            PlacedFallSpikes(position, self.placed_sprites, IMAGES)
        elif object_type == 'stand_spikes':
            PlacedStandSpikes(position, self.placed_sprites, IMAGES, self.rotate_button.current_stand_spikes_rotate)

            
    def handle_events(self, menu_on):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.info_button.rect.collidepoint(event.pos):
                    # Toggle info screen on/off
                    menu_on = 2 if menu_on == 1 else 1  # Toggle between game and info screen
                else:
                    # Make sure info menu is closed if clicked elsewhere
                    if menu_on == 2:
                        menu_on = 1
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    # Toggle pause state
                    self.is_paused = not self.is_paused
                    font = pygame.font.SysFont('Arial', 14)
                    pause_message = "Pause Toggled: " + str(self.is_paused)
                    self.notification_manager.add_message(pause_message, 1, (SCREEN_WIDTH-80, 100), font)
                    print(pause_message)
            if self.game_mode == GameState.EDIT_MODE:
                # Update dragging state with left click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left click hold down
                    self.is_dragging = True
                    self.last_placed_pos = None  # Reset last placed position on new click
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: # Left click release
                    self.is_dragging = False
                    self.last_placed_pos = None  # Clear the last placed position when releasing the button
            elif self.game_mode == GameState.PLAY_MODE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down_events(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up_events(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion_events(event)
                elif event.type == pygame.FINGERDOWN:
                    self.handle_finger_down_events(event)
                elif event.type == pygame.FINGERUP:
                    self.handle_finger_up_events(event)

            
            #################
            # LEFT CLICK (PRESSED DOWN) on right side (menu buttons)
            #################
            if(event.type == MOUSEBUTTONDOWN 
               and pygame.mouse.get_pressed()[0] 
               and self.mouse_pos[0] > SCREEN_WIDTH-GameState.HORIZONTAL_GRID_OFFSET): 
                    # BUTTONS
                    if self.grid_button.rect.collidepoint(self.mouse_pos):
                        if Grid.ALL_GRIDS_ENABLED:
                            Grid.ALL_GRIDS_ENABLED = False
                        else:
                            Grid.ALL_GRIDS_ENABLED = True
                    if self.eraser_button.rect.collidepoint(self.mouse_pos):
                        self.dragging.dragging_all_false()
                        self.is_an_object_currently_being_dragged = False
                        self.selected_object_type = None
                        self.toggle_eraser_mode()
                        GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = None
                    if not MOBILE_ACCESSIBILITY_MODE:
                        if self.save_file_button.rect.collidepoint(self.mouse_pos):
                            save_file()
                        if self.load_file_button.rect.collidepoint(self.mouse_pos):
                            self.placed_sprites = load_file(self.placed_sprites, self)
            #################
            # LEFT CLICK (PRESSED DOWN) at Top of Screen (start objects and left of clear button)
            #################
            if(event.type == MOUSEBUTTONDOWN 
               and pygame.mouse.get_pressed()[0] 
               and self.mouse_pos[1] < GameState.TOP_UI_BOUNDARY_Y_HEIGHT
               and self.mouse_pos[0] < GameState.UI_ELEMENTS_POSITIONS['clear_button'][0]): 
                if self.game_mode == GameState.EDIT_MODE:
                    # Click on Start object at top (which will then drag to mouse cursor)
                    # Restarts all drag objects
                    if self.eraser_mode_active:
                        # Turn off eraser mode so we can select for the start object
                        self.toggle_eraser_mode()
                        
                    def select_object_for_placement():
                        start_objects = {'player': self.start.player,
                                         'door': self.start.door,
                                         'wall': self.start.wall,
                                         'flyer': self.start.flyer,
                                         'reverse_wall': self.start.reverse_wall,
                                         'spring': self.start.spring,
                                         'smily_robot': self.start.smily_robot,
                                         'diamonds': self.start.diamonds,
                                         'sticky_block': self.start.sticky_block,
                                         'fall_spikes': self.start.fall_spikes,
                                         'stand_spikes': self.start.stand_spikes
                                         }
                        for start_object_key, start_object_value in start_objects.items():
                            if start_object_value.rect.collidepoint(self.mouse_pos):
                                if self.selected_object_type == start_object_key:
                                    # Start object already was selected, toggle it off
                                    self.selected_object_type = None
                                    self.start.dynamic_object_placeholder.reset()
                                    return
                                else:
                                    # Start object was not selected yet
                                    self.selected_object_type = start_object_key
                                    self.start.dynamic_object_placeholder.start_sprite_with_yellow_outline(self.selected_object_type, start_objects[start_object_key].rect.topleft, IMAGES, self.rotate_button.current_stand_spikes_rotate)
                                    return  # Exit after selecting the object
                    
                    select_object_for_placement()
                        
            #################
            # LEFT CLICK (PRESSED DOWN)
            #################
            elif(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and \
            self.mouse_pos[0] >= GameState.HORIZONTAL_GRID_OFFSET and \
            self.mouse_pos[0] <= SCREEN_WIDTH-(GameState.HORIZONTAL_GRID_OFFSET+(Grid.GRID_SPACING/2)) and \
            self.mouse_pos[1] <= SCREEN_HEIGHT-GameState.BOTTOM_Y_GRID_OFFSET):
                if not self.eraser_mode_active:
                    # Place object on location of mouse release
                    if self.selected_object_type:
                        grid_pos = snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, Grid.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT, GameState.HORIZONTAL_GRID_OFFSET)
                        # Delete object that's already at the grid
                        remove_placed_object(self.placed_sprites, self.mouse_pos, self)
                        # Example for placing a player, replicate for other types
                        if self.selected_object_type == 'player' and not self.placed_player:
                            self.placed_player = PlacedPlayer(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'door' and not self.placed_door:
                            self.placed_door = PlacedDoor(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'wall':
                            PlacedWall(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'flyer':
                            PlacedFlyer(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'reverse_wall':
                            PlacedReverseWall(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'spring':
                            PlacedSpring(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'smily_robot':
                            PlacedSmilyRobot(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'diamonds':
                            PlacedDiamonds(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'sticky_block':
                            PlacedStickyBlock(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'fall_spikes':
                            PlacedFallSpikes(grid_pos, self.placed_sprites, IMAGES)
                        elif self.selected_object_type == 'stand_spikes':
                            PlacedStandSpikes(grid_pos, self.placed_sprites, IMAGES, self.rotate_button.current_stand_spikes_rotate)

                elif self.eraser_mode_active:
                    # Either delete object being dragged or delete object on grid (if not currently dragging an object)
                    if self.is_an_object_currently_being_dragged:
                        # If there is a current dragged object, delete it
                        self.dragging.dragging_all_false()
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        self.is_an_object_currently_being_dragged = False
                    else:
                        # No object is currently being dragged, attempt to delete object at grid position
                        remove_placed_object(self.placed_sprites, self.mouse_pos, self)
            #################
            # RIGHT CLICK (RELEASE)
            #################           
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:  # Right click is button 3
                # Either delete object being dragged or delete object on grid (if not currently dragging an object)
                if self.is_an_object_currently_being_dragged:
                    # If there is a current dragged object, delete it
                    self.dragging.dragging_all_false()
                    self.start = restart_start_objects(self.start, self.START_POSITIONS)
                    self.is_an_object_currently_being_dragged = False
                    GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = None
                    self.start.dynamic_object_placeholder.reset()
                else:
                    # No object is currently being dragged, attempt to delete object at grid position
                    remove_placed_object(self.placed_sprites, self.mouse_pos, self)
            
            #################
            # CLICK AND DRAG (ERASER)
            #################   
            elif (event.type == pygame.MOUSEMOTION and self.eraser_mode_active):
                self.update_mouse_pos()
                if self.is_dragging and self.game_mode == GameState.EDIT_MODE and self.mouse_pos[1] > GameState.TOP_UI_BOUNDARY_Y_HEIGHT:
                    remove_placed_object(self.placed_sprites, self.mouse_pos, self)
                    

            
            # CLICK AND DRAG OBJECT TO GRID
            elif (event.type == pygame.MOUSEMOTION and not self.eraser_mode_active):

                self.update_mouse_pos()
                if(self.is_dragging and self.game_mode == GameState.EDIT_MODE and self.mouse_pos[1] > GameState.TOP_UI_BOUNDARY_Y_HEIGHT \
                   and self.mouse_pos[0] >= GameState.HORIZONTAL_GRID_OFFSET and \
                   self.mouse_pos[0] <= SCREEN_WIDTH-(GameState.HORIZONTAL_GRID_OFFSET+(Grid.GRID_SPACING/2)) and \
                   self.mouse_pos[1] <= SCREEN_HEIGHT-GameState.BOTTOM_Y_GRID_OFFSET):
                    new_grid_pos = snap_to_grid(self.mouse_pos, SCREEN_WIDTH, SCREEN_HEIGHT, Grid.GRID_SPACING, GameState.TOP_UI_BOUNDARY_Y_HEIGHT, GameState.HORIZONTAL_GRID_OFFSET)
    
                    if new_grid_pos != self.last_placed_pos:
                        interpolated_positions = self.interpolate_positions(self.last_placed_pos or new_grid_pos, new_grid_pos, Grid.GRID_SPACING)
                        
                        for position in interpolated_positions:
                            # Use the selected object type stored in self.selected_object_type
                            self.place_object_at_position(position, self.selected_object_type)
                        
                        self.last_placed_pos = new_grid_pos
            if event.type == MOUSEBUTTONUP:            
                #################
                # PLAY BUTTON
                #################
                if(self.play_edit_switch_button.rect.collidepoint(self.mouse_pos) and self.game_mode == self.EDIT_MODE):
                    self.switch_to_play_mode()
                #################
                # LEFT CLICK (RELEASE) STOP BUTTON
                #################
                elif(self.play_edit_switch_button.rect.collidepoint(self.mouse_pos) and self.game_mode == self.PLAY_MODE):
                    # Makes sure you are not in editing mode to enter editing mode
                    self.switch_to_edit_mode()
                if self.restart_button.rect.collidepoint(self.mouse_pos):
                    if self.game_mode == self.PLAY_MODE:
                        restart_level(self)
                if self.clear_button.rect.collidepoint(self.mouse_pos):
                    if self.game_mode == self.EDIT_MODE: #Editing mode
                        self.start = restart_start_objects(self.start, self.START_POSITIONS)
                        # REMOVE ALL SPRITES
                        remove_all_placed(self)
                if self.rotate_button.rect.collidepoint(self.mouse_pos):
                    # Click rotate button
                    if not self.dragging.stand_spikes:
                        self.rotate_button.current_stand_spikes_rotate = (self.rotate_button.current_stand_spikes_rotate + 90) % 360
                        self.start.stand_spikes.change_image_rotation(self.rotate_button.current_stand_spikes_rotate)
                        if self.selected_object_type == "stand_spikes":
                            # Update the yellow outline spikes
                            self.start.dynamic_object_placeholder.start_sprite_with_yellow_outline(self.selected_object_type, self.start.stand_spikes.rect.topleft, IMAGES, self.rotate_button.current_stand_spikes_rotate)
        return menu_on

    def handle_mouse_down_events(self, event):
        self.mouse_button_down = True
        # Checks if the mouse interacts with movement buttons
        if self.left_arrow_button.rect.collidepoint(event.pos):
            self.moving_left = True
            self.left_arrow_button.set_active(True)  # Activate left arrow button image
        elif self.right_arrow_button.rect.collidepoint(event.pos):
            self.moving_right = True
            self.right_arrow_button.set_active(True)  # Activate right arrow button image
        elif self.jump_button.rect.collidepoint(event.pos) and self.play_player.can_jump():
            self.play_player.jump()
            self.jump_button.set_active(True)  # Activate jump button image
    
    def handle_mouse_up_events(self, event):
        # Mouse button is released
        self.mouse_button_down = False
        # Reset arrow buttons to inactive state
        self.left_arrow_button.set_active(False)
        self.right_arrow_button.set_active(False)
        self.jump_button.set_active(False)
    
        # Stop movement if the mouse button is released over any arrow button
        if self.left_arrow_button.rect.collidepoint(event.pos) or self.right_arrow_button.rect.collidepoint(event.pos):
            self.moving_left = False
            self.moving_right = False
            self.play_player.stop()  # This will halt the player's movement
        
    def handle_mouse_motion_events(self, event):
        # Ensure this is only active if the mouse button is currently pressed
        if self.mouse_button_down:
            # Reactivate the appropriate arrow button based on the new position
            if self.left_arrow_button.rect.collidepoint(event.pos):
                self.moving_left = True
                self.moving_right = False
                self.left_arrow_button.set_active(True)
                self.right_arrow_button.set_active(False)
            elif self.right_arrow_button.rect.collidepoint(event.pos):
                self.moving_left = False
                self.moving_right = True
                self.left_arrow_button.set_active(False)
                self.right_arrow_button.set_active(True)
    
    def handle_finger_down_events(self, event):
        # Convert touch position to Pygame coordinates
        touch_x, touch_y = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
    
        # For touch inputs, specifically handle the jump button activation
        if self.jump_button.rect.collidepoint(touch_x, touch_y):
            self.want_to_jump = True
            self.jump_button.set_active(True)  # Activate jump button image
            
    def handle_finger_up_events(self, event):
        # Convert the touch position to Pygame coordinates
        touch_x, touch_y = event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT
    
        # Check if the touch was within the jump button's rectangle
        # You might want to track if the jump button was previously activated by this touch
        if self.jump_button.rect.collidepoint(touch_x, touch_y):
            self.jump_button.set_active(False)
    
    def toggle_eraser_mode(self):
        # Toggle the eraser mode state
        self.eraser_mode_active = not self.eraser_mode_active
        # Update the eraser button visual state
        self.eraser_button.toggle_eraser_button_image(self.eraser_mode_active)
    def switch_to_edit_mode(self):
        # Makes sure you are not in editing mode to enter editing mode
        font = pygame.font.SysFont('Arial', 14)
        self.notification_manager.add_message("Editing Mode Activated", 1, (SCREEN_WIDTH-80, 100), font)
        print("Editing Mode Activated")
        self.game_mode = self.EDIT_MODE
        self.play_player.death_count = 0
        self.play_edit_switch_button.image = self.play_edit_switch_button.game_mode_button(self.game_mode)
        remove_all_play(self)
        self.play_sprites.empty()
        self.start = restart_start_objects(self.start, self.START_POSITIONS)
        
        #MUSIC_PLAYER = []
        #MUSIC_PLAYER = [MusicPlayer()]
    def switch_to_play_mode(self):
        # Remove all drag within current edit mode
        self.dragging.dragging_all_false()
        self.is_an_object_currently_being_dragged = False
        GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS = None
        self.selected_object_type = None
        # Makes sure there is at least one player to play game
        if self.placed_player:
            # Makes clicking play again unclickable
            self.game_mode = self.PLAY_MODE
            self.play_edit_switch_button.image = self.play_edit_switch_button.game_mode_button(self.game_mode)
            font = pygame.font.SysFont('Arial', 14)
            self.notification_manager.add_message("Play Mode Activated", 1, (SCREEN_WIDTH-80, 100), font, (0, 255, 0))
            print("Play Mode Activated")
            
            #MUSIC_PLAYER = [MusicPlayer()]
            self.play_player = PlayPlayer(self.placed_player.rect.topleft, self.play_sprites, IMAGES, SOUNDS)
            if self.placed_door:
                self.play_door = PlayDoor(self.placed_door.rect.topleft, self.play_sprites, IMAGES)
            for placed_wall in PlacedWall.wall_list:
                PlayWall(placed_wall.rect.topleft, self.play_sprites, IMAGES)
            for placed_flyer in PlacedFlyer.flyer_list:
                PlayFlyer(placed_flyer.rect.topleft, self.play_sprites, IMAGES)
            for placed_reverse_wall in PlacedReverseWall.reverse_wall_list:
                PlayReverseWall(placed_reverse_wall.rect.topleft, self.play_sprites, IMAGES)
            for placed_smily_robot in PlacedSmilyRobot.smily_robot_list:
                PlaySmilyRobot(placed_smily_robot.rect.topleft, self.play_sprites, IMAGES)
            for placed_spring in PlacedSpring.spring_list:
                PlaySpring(placed_spring.rect.topleft, self.play_sprites, IMAGES)
            for placed_diamond in PlacedDiamonds.diamonds_list:
                PlayDiamonds(placed_diamond.rect.topleft, self.play_sprites, IMAGES)
            for placed_sticky_block in PlacedStickyBlock.sticky_block_list:
                PlayStickyBlock(placed_sticky_block.rect.topleft, self.play_sprites, IMAGES)
            for placed_fall_spikes in PlacedFallSpikes.fall_spikes_list:
                PlayFallSpikes(placed_fall_spikes.rect.topleft, self.play_sprites, IMAGES)
            for placed_stand_spikes in PlacedStandSpikes.stand_spikes_list:
                PlayStandSpikes(placed_stand_spikes.rect.topleft, self.play_sprites, IMAGES, placed_stand_spikes.rotate)
            
            self.left_arrow_button = ArrowButton(self.play_sprites, IMAGES, "left")
            self.right_arrow_button = ArrowButton(self.play_sprites, IMAGES, "right")
            self.jump_button = JumpButton(self.play_sprites, IMAGES)
        else:
            font = pygame.font.SysFont('Arial', 14)
            self.notification_manager.add_message("You need a character!", 3, (SCREEN_WIDTH-80, 100), font, (255, 255, 0))
            print("You need a character!")
    def edit_mode_function(self):
        # DRAG- switch dynamic object placeholder with player sprite and vice versa
        if self.dragging.player and self.placed_player is None:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['player'] # Replaces in Menu
            self.start.player.rect.topleft = (self.mouse_pos[0]-(self.start.player.image.get_width()/2),
                                         self.mouse_pos[1]-(self.start.player.image.get_height()/3))
        else:
            # Player is no longer being dragged, restore the start image and position of the start player
            self.start.player.rect.topleft = self.START_POSITIONS['player']
            # Only one player is allowed, so remove yellow outline from start object
            if self.placed_player and self.selected_object_type == "player":
                self.selected_object_type = None
                self.start.dynamic_object_placeholder.reset()
        if self.dragging.door and self.placed_door is None:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['door'] # Replaces in Menu
            self.start.door.rect.topleft = (self.mouse_pos[0]-(self.start.door.image.get_width()/2),
                                       self.mouse_pos[1]-(self.start.door.image.get_height()/4))
            self.start.door.image = IMAGES["spr_door_closed"]
        else:
            self.start.door.rect.topleft = self.START_POSITIONS['door']
            # Only one door is allowed, so remove yellow outline from start object
            if self.placed_door and self.selected_object_type == "door":
                self.selected_object_type = None
                self.start.dynamic_object_placeholder.reset()
        if self.dragging.wall:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['wall'] # Replaces in Menu
            self.start.wall.rect.topleft = (self.mouse_pos[0]-(self.start.wall.image.get_width()/2),
                                       self.mouse_pos[1]-(self.start.wall.image.get_height()/2))
        else:
            self.start.wall.rect.topleft = self.START_POSITIONS['wall']
            
        if self.dragging.reverse_wall:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['reverse_wall'] # Replaces in Menu
            self.start.reverse_wall.rect.topleft = (self.mouse_pos[0]-(self.start.reverse_wall.image.get_width()/2),
                                               self.mouse_pos[1]-(self.start.reverse_wall.image.get_height()/2))
        else:
            self.start.reverse_wall.rect.topleft = self.START_POSITIONS['reverse_wall']
        if self.dragging.diamonds:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['diamonds'] # Replaces in Menu
            self.start.diamonds.rect.topleft = (self.mouse_pos[0]-(self.start.diamonds.image.get_width()/2),
                                           self.mouse_pos[1]-(self.start.diamonds.image.get_height()/2))
        else:
            self.start.diamonds.rect.topleft = self.START_POSITIONS['diamonds']
        if self.dragging.flyer:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['flyer'] # Replaces in Menu
            self.start.flyer.rect.topleft = (self.mouse_pos[0]-(self.start.flyer.image.get_width()/2),
                                        self.mouse_pos[1]-(self.start.flyer.image.get_height()/2))
        else:
            self.start.flyer.rect.topleft = self.START_POSITIONS['flyer']
        if self.dragging.smily_robot:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['smily_robot'] # Replaces in Menu
            self.start.smily_robot.rect.topleft = (self.mouse_pos[0]-(self.start.smily_robot.image.get_width()/2),
                                              self.mouse_pos[1]-(self.start.smily_robot.image.get_height()/2))
        else:
            self.start.smily_robot.rect.topleft = self.START_POSITIONS['smily_robot']
        if self.dragging.spring:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['spring'] # Replaces in Menu
            self.start.spring.rect.topleft = (self.mouse_pos[0]-(self.start.spring.image.get_width()/2),
                                         self.mouse_pos[1]-(self.start.spring.image.get_height()/2))
        else:
            self.start.spring.rect.topleft = self.START_POSITIONS['spring']
        if self.dragging.sticky_block:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['sticky_block'] # Replaces in Menu
            self.start.sticky_block.rect.topleft = (self.mouse_pos[0]-(self.start.sticky_block.image.get_width()/2),
                                               self.mouse_pos[1]-(self.start.sticky_block.image.get_height()/2))
        else:
            self.start.sticky_block.rect.topleft = self.START_POSITIONS['sticky_block']
        if self.dragging.fall_spikes:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['fall_spikes'] # Replaces in Menu
            self.start.fall_spikes.rect.topleft = (self.mouse_pos[0]-(self.start.fall_spikes.image.get_width()/2),
                                              self.mouse_pos[1]-(self.start.fall_spikes.image.get_height()/2))
        else:
            self.start.fall_spikes.rect.topleft = self.START_POSITIONS['fall_spikes']
        if self.dragging.stand_spikes:
            self.start.dynamic_object_placeholder.rect.topleft = self.START_POSITIONS['stand_spikes'] # Replaces in Menu
            self.start.stand_spikes.rect.topleft = (self.mouse_pos[0]-(self.start.stand_spikes.image.get_width()/2),
                                               self.mouse_pos[1]-(self.start.stand_spikes.image.get_height()/2))
        else:
            self.start.stand_spikes.rect.topleft = self.START_POSITIONS['stand_spikes']
        # When the start object is being dragged, then it is the original image size
        # When the start object is not being dragged, it is at a bigger size
        self.start.player.toggle_image_start_or_drag(self.dragging.player)
        self.start.door.toggle_image_start_or_drag(self.dragging.door)
        self.start.wall.toggle_image_start_or_drag(self.dragging.wall)
        self.start.reverse_wall.toggle_image_start_or_drag(self.dragging.reverse_wall)
        self.start.diamonds.toggle_image_start_or_drag(self.dragging.diamonds)
        self.start.flyer.toggle_image_start_or_drag(self.dragging.flyer)
        self.start.smily_robot.toggle_image_start_or_drag(self.dragging.smily_robot)
        self.start.spring.toggle_image_start_or_drag(self.dragging.spring)
        self.start.sticky_block.toggle_image_start_or_drag(self.dragging.sticky_block)
        self.start.fall_spikes.toggle_image_start_or_drag(self.dragging.fall_spikes)
        self.start.stand_spikes.toggle_image_start_or_drag(self.dragging.stand_spikes)
    def play_mode_function(self):
        self.handle_player_input()
        if self.moving_left:
            # Move the player left
            self.play_player.move_left()
        
        if self.moving_right:
            # Move the player right
            self.play_player.move_right()
        
        if self.jumping:
            # Make the player jump
            self.play_player.jump()
        # Dead
        if self.play_player.rect.top > SCREEN_HEIGHT and self.play_player.speed_y >= 0:
            restart_level(self)
        # Spikes fall when player goes underneath
        if PlayFallSpikes.fall_spikes_list:
            for fall_spike in PlayFallSpikes.fall_spikes_list:
                if(self.play_player.rect.right > fall_spike.rect.left and
                   self.play_player.rect.left < fall_spike.rect.right and
                   self.play_player.rect.top > fall_spike.rect.bottom):
                    fall_spike.fall_var = 1
                if fall_spike.fall_var == 1:
                    fall_spike.rect.top = fall_spike.rect.top + 5
        # Player wins when he captures all jewels and enters door
        if self.play_door:
            self.play_door.image = self.play_door.open_or_close(self.play_player.score, PlayDiamonds.diamonds_list)
            if pygame.sprite.collide_mask(self.play_player, self.play_door):
                if self.play_player.score == len(PlayDiamonds.diamonds_list):
                    font = pygame.font.SysFont('Arial', 96)
                    self.notification_manager.add_message("You Win!", 3, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), font)
                    print("You Win!")
                    self.notification_manager.draw_messages(self.screen)
                    pygame.display.update()
                    time.sleep(3)
                    self.switch_to_edit_mode()
                    #music_player = [MusicPlayer()]
                    

                
        #####################
        # COLLISIONS
        #####################
        for play_smily_robot in PlaySmilyRobot.smily_robot_list:
            if self.play_player.rect.colliderect(play_smily_robot.rect):
                if(self.play_player.rect.bottom <= play_smily_robot.rect.top + 10 and self.play_player.speed_y >= 0):
                    play_smily_robot.rect.topleft = PlaySmilyRobot.OUT_OF_PLAY_TOPLEFT
                    self.play_player.propeller = 0
                    self.play_player.speed_y = -4
                    self.play_player.jumps_left = 1 #Allows propeller in air
                elif(self.play_player.rect.right-play_smily_robot.rect.left <= 10 and
                     self.play_player.rect.bottom > play_smily_robot.rect.top + 10):
                    restart_level(self)
                elif(self.play_player.rect.left-play_smily_robot.rect.right <= 10 and
                     self.play_player.rect.bottom > play_smily_robot.rect.top + 10):
                    restart_level(self)
        for play_flyer in PlayFlyer.flyer_list:
            if self.play_player.rect.colliderect(play_flyer.rect):
                restart_level(self)
        for play_fall_spikes in PlayFallSpikes.fall_spikes_list:
            if self.play_player.rect.colliderect(play_fall_spikes.rect):
                restart_level(self)
        for play_stand_spikes in PlayStandSpikes.stand_spikes_list:
            if self.play_player.rect.colliderect(play_stand_spikes.rect):
                restart_level(self)
        for play_diamonds in PlayDiamonds.diamonds_list:
            if pygame.sprite.collide_mask(self.play_player, play_diamonds):
                self.play_player.score += 1
                play_diamonds.image = IMAGES["spr_dynamic_object_placeholder"]
        for spring in PlaySpring.spring_list:
            if pygame.sprite.collide_mask(self.play_player, spring):
                # Check if the collision is primarily on top of the spring
                if self.play_player.rect.bottom <= spring.rect.top + 20 and self.play_player.speed_y >= 0:
                    # This is a top collision, trigger the high jump
                    SOUNDS["snd_spring"].play()
                    self.play_player.propeller = 0
                    self.play_player.rect.bottom = spring.rect.top
                    self.play_player.speed_y = -10  # High jump
                    self.play_player.jumps_left = 1  # Allows for propeller in air
                else:
                    # Side collision handling
                    # Collision is primarily horizontal
                    if self.play_player.rect.centerx < spring.rect.centerx:
                        # Player is on the left side of the spring
                        self.play_player.rect.right = spring.rect.left
                    else:
                        # Player is on the right side of the spring
                        self.play_player.rect.left = spring.rect.right

    def initiate_room(self):
        self.start.player.rect.topleft = self.START_POSITIONS['player']
        self.start.wall.rect.topleft = self.START_POSITIONS['wall']
        self.start.flyer.rect.topleft = self.START_POSITIONS['flyer']
        self.start.reverse_wall.rect.topleft = self.START_POSITIONS['reverse_wall']
        self.start.spring.rect.topleft = self.START_POSITIONS['spring']
        self.start.smily_robot.rect.topleft = self.START_POSITIONS['smily_robot']
        self.start.door.rect.topleft = self.START_POSITIONS['door']
        self.start.diamonds.rect.topleft = self.START_POSITIONS['diamonds']
        self.start.sticky_block.rect.topleft = self.START_POSITIONS['sticky_block']
        self.start.fall_spikes.rect.topleft = self.START_POSITIONS['fall_spikes']
        self.start.stand_spikes.rect.topleft = self.START_POSITIONS['stand_spikes']
        
    def handle_player_input(self):
        keys_pressed = pygame.key.get_pressed()

        # Keyboard movement handling
        if keys_pressed[pygame.K_LEFT]:
            self.play_player.move_left()
            # When moving with the keyboard, ignore mouse movement flags
            self.moving_left, self.moving_right = False, False
        elif keys_pressed[pygame.K_RIGHT]:
            self.play_player.move_right()
            # When moving with the keyboard, ignore mouse movement flags
            self.moving_left, self.moving_right = False, False

        # Jump handling for keyboard
        if keys_pressed[pygame.K_UP] and self.jump_key_released:
            self.play_player.jump()
            self.jump_key_released = False  # Prevent continuous jumps from the keyboard
        elif not keys_pressed[pygame.K_UP]:
            self.jump_key_released = True  # Allow the next jump

        # Mouse-based movement takes effect only if there are no keyboard movement inputs
        if not keys_pressed[pygame.K_LEFT] and not keys_pressed[pygame.K_RIGHT]:
            if self.moving_left:
                self.play_player.move_left()
            elif self.moving_right:
                self.play_player.move_right()

        # If no movement input is detected from either keyboard or mouse, stop the player
        if not keys_pressed[pygame.K_LEFT] and not keys_pressed[pygame.K_RIGHT] and not self.moving_left and not self.moving_right:
            self.play_player.stop()

        # Handle jumping initiated by the mouse
        if self.want_to_jump:
            self.play_player.jump()
            self.want_to_jump = False  # Reset the jump flag to prevent continuous jumping from mouse input

# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions(game_state):
    # Handle player separately
    player_position = []
    if game_state.placed_player is not None:
        player_position = [game_state.placed_player.rect.topleft]
    if game_state.placed_door is not None:
        door_position = [game_state.placed_door.rect.topleft]

    # Dictionary for all other objects except player
    total_placed_list = {
        'wall': PlacedWall.wall_list,
        'flyer': PlacedFlyer.flyer_list,
        'reverse_wall': PlacedReverseWall.reverse_wall_list,
        'spring': PlacedSpring.spring_list,
        'smily_robot': PlacedSmilyRobot.smily_robot_list,
        'diamonds': PlacedDiamonds.diamonds_list,
        'sticky_block': PlacedStickyBlock.sticky_block_list,
        'fall_spikes': PlacedFallSpikes.fall_spikes_list,
        'stand_spikes': PlacedStandSpikes.stand_spikes_list
    }

    # Initialize the dictionary for storing object positions
    get_rect_for_all_obj = {'player': player_position,
                            'door': door_position}

    # Loop through all lists of placed objects (except player and door)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = [item.rect.topleft for item in item_list]
        get_rect_for_all_obj[item_key] = item_list_in_name

    return get_rect_for_all_obj

def remove_all_placed(game_state):
    for spr_list in [PlacedWall.wall_list, PlacedFlyer.flyer_list,
                     PlacedReverseWall.reverse_wall_list, PlacedSpring.spring_list, PlacedSmilyRobot.smily_robot_list,
                     PlacedDiamonds.diamonds_list, PlacedStickyBlock.sticky_block_list,
                     PlacedFallSpikes.fall_spikes_list, PlacedStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    if game_state.placed_player:
        game_state.placed_player.kill()
        game_state.placed_player = None
    if game_state.placed_door:
        game_state.placed_door.kill()
        game_state.placed_door = None
    PlacedWall.wall_list = []
    PlacedFlyer.flyer_list = []
    PlacedReverseWall.reverse_wall_list = []
    PlacedSpring.spring_list = []
    PlacedSmilyRobot.smily_robot_list = []
    PlacedDiamonds.diamonds_list = []
    PlacedStickyBlock.sticky_block_list = []
    PlacedFallSpikes.fall_spikes_list = []
    PlacedStandSpikes.stand_spikes_list = []

def remove_all_play(game_state):
    for spr_list in [PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    game_state.play_player.kill()
    game_state.play_player = None
    if game_state.play_door:
        game_state.play_door.kill()
        game_state.play_door = None
    PlayWall.wall_list = []
    PlayFlyer.flyer_list = []
    PlayReverseWall.reverse_wall_list = []
    PlaySpring.spring_list = []
    PlaySmilyRobot.smily_robot_list = []
    PlayDiamonds.diamonds_list = []
    PlayStickyBlock.sticky_block_list = []
    PlayFallSpikes.fall_spikes_list = []
    PlayStandSpikes.stand_spikes_list = []

def restart_level(game_state):
    for spr_list in [PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.restart()
    game_state.play_player.restart()
    if game_state.play_door:
        game_state.play_door.restart()

def main():
    # Tk box
    if not MOBILE_ACCESSIBILITY_MODE:
        ROOT = tk.Tk()
        ROOT.withdraw()
        
    MENU_ON = 1

    load_all_assets()
    

    
    game_state = GameState()
    
    #Fonts
    FONT_ARIAL = pygame.font.SysFont('Arial', 24)

    
    #Backgrounds
    START_MENU = pygame.image.load("sprites/start_menu.png").convert()
    START_MENU = pygame.transform.scale(START_MENU, (SCREEN_WIDTH, SCREEN_HEIGHT))
    INFO_SCREEN = pygame.image.load("sprites/info_screen.png").convert()
    INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    METROPOLIS_BACKGROUND = pygame.image.load("sprites/metropolis_background.png").convert()
    METROPOLIS_BACKGROUND = pygame.transform.scale(METROPOLIS_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
    #MUSIC_PLAYER = [MusicPlayer()]
        
    while True:
        clock.tick(FPS)
        game_state.update_mouse_pos()
        
        if MENU_ON == 1:  # Normal game state
        
            game_state.initiate_room()
            MENU_ON = game_state.handle_events(MENU_ON)
            
            if not game_state.is_paused:
                # Only update game logic if the game is not paused
                game_state.handle_events(MENU_ON)
                if game_state.game_mode == GameState.EDIT_MODE:
                    game_state.edit_mode_function()
                    game_state.start_sprites.update()
                    game_state.placed_sprites.update()
                elif game_state.game_mode == GameState.PLAY_MODE:
                    game_state.play_mode_function()
                    game_state.play_sprites.update()
            else:
                # Game is paused
                pass
            
            SCREEN.blit(METROPOLIS_BACKGROUND, (0, 0))
            
    
            game_state.game_mode_sprites.draw(SCREEN)
            if game_state.game_mode == game_state.EDIT_MODE: #Only draw placed sprites in editing mode
                if game_state.grid_button.grid_on_var:
                    game_state.grid_sprites.draw(SCREEN)
                
                game_state.placed_sprites.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("", 1, (0, 0, 0))
                if Grid.ALL_GRIDS_ENABLED:
                    draw_grid(SCREEN, Grid.GRID_SPACING, SCREEN_WIDTH, SCREEN_HEIGHT, GameState.TOP_UI_BOUNDARY_Y_HEIGHT, GameState.HORIZONTAL_GRID_OFFSET)
                game_state.start_sprites.draw(SCREEN)
                # Draw yellow outline around start object being dragged
                if game_state.selected_object_type is not None:
                    sprite_name, pos = GameState.DYNAMIC_OBJECT_PLACEHOLDER_YELLOW_OUTLINE_OBJ_AND_POS
                    draw_yellow_outline(SCREEN, IMAGES[sprite_name], pos, thickness=1)

    
            elif game_state.game_mode == game_state.PLAY_MODE: #Only draw play sprites in play mode
                if game_state.eraser_mode_active:
                    game_state.toggle_eraser_mode()
                game_state.play_sprites.draw(SCREEN)
                DEATH_COUNT_TEXT = FONT_ARIAL.render("Deaths: " + str(game_state.play_player.death_count), 1, (0, 0, 0))
            game_state.notification_manager.draw_messages(game_state.screen)
            SCREEN.blit(DEATH_COUNT_TEXT, ((SCREEN_WIDTH/2-50), 5))
    
            pygame.display.update()
        elif MENU_ON == 2:
            InfoScreen(INFO_SCREEN, SCREEN)  # Display the Info Screen
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Click anywhere to return to the game
                    MENU_ON = 1
            
            pygame.display.update()
        
if __name__ == "__main__":
    main()