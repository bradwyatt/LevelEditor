from base_objects import PlayObject
import pygame
import random
from utils import SCREEN_WIDTH

class PlayWall(PlayObject):
    wall_list = []

    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_wall"])
        self.add_to_class_list()

    def add_to_class_list(self):
        PlayWall.wall_list.append(self)

    def remove_from_class_list(self):
        PlayWall.wall_list.remove(self)
        
class PlayReverseWall(PlayObject):
    reverse_wall_list = []

    def __init__(self, pos, play_sprites, images):
        # Assuming you need a transparent surface for reverse walls
        image = pygame.Surface((24, 24), pygame.SRCALPHA)  # Adjust dimensions as necessary
        image.fill((0, 0, 0, 0))  # Completely transparent
        super().__init__(pos, play_sprites, image)
        self.add_to_class_list()

    def add_to_class_list(self):
        PlayReverseWall.reverse_wall_list.append(self)

    def remove_from_class_list(self):
        PlayReverseWall.reverse_wall_list.remove(self)
        
class PlayFlyer(PlayObject):
    flyer_list = []
    SPEED = 1
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_flyer"])
        self.images = images
        self.left_speed = PlayFlyer.SPEED*-1
        self.right_speed = PlayFlyer.SPEED
        self.right_or_left = random.choice([self.left_speed, self.right_speed])
        self.add_to_class_list()
        
    def update(self):
        self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
        for wall in PlayWall.wall_list:
            if self.rect.colliderect(wall.rect):
                self.right_or_left = self.right_or_left*-1
                self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
        for reverse_wall in PlayReverseWall.reverse_wall_list:
            if self.rect.colliderect(reverse_wall.rect):
                self.right_or_left = self.right_or_left*-1
                self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.right_or_left = self.right_or_left*-1
            self.rect.topleft = (self.rect.topleft[0]+self.right_or_left, self.rect.topleft[1])
        self.sprite_direction(self.images)

    def add_to_class_list(self):
        PlayFlyer.flyer_list.append(self)

    def remove_from_class_list(self):
        PlayFlyer.flyer_list.remove(self)

    def sprite_direction(self, images):
        if self.right_or_left == self.right_speed:
            self.image = images["spr_flyer"]
        elif self.right_or_left == self.left_speed:
            self.image = pygame.transform.flip(images["spr_flyer"], 1, 0)
            
class PlayDiamonds(PlayObject):
    diamonds_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_diamonds"])
        self.images = images
        self.pos = pos
        self.add_to_class_list()
    def restart(self):
        self.rect.topleft = self.pos
        self.image = self.images["spr_diamonds"]
    def add_to_class_list(self):
        PlayDiamonds.diamonds_list.append(self)
    def remove_from_class_list(self):
        PlayDiamonds.diamonds_list.remove(self)
        
class PlayDoor(PlayObject):
    door_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_door_closed"])
        self.pos = pos
        self.images = images
        play_sprites.add(self)
        self.add_to_class_list()
    def open_or_close(self, score, diamonds_list):
        if score == len(diamonds_list):
            print("HOORAY!")
            return self.images["spr_door_open"]
        return self.images["spr_door_closed"]
    def restart(self):
        self.rect.topleft = self.pos
    def add_to_class_list(self):
        PlayDoor.door_list.append(self)
    def remove_from_class_list(self):
        PlayDoor.door_list.remove(self)
        
class PlaySmilyRobot(PlayObject):
    smily_robot_list = []
    SPEED = 2
    OUT_OF_PLAY_TOPLEFT = (0, -100)
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_smily_robot"])
        self.pos = pos
        self.rect.topleft = self.pos
        self.images = images
        self.left_speed = PlaySmilyRobot.SPEED*-1
        self.right_speed = PlaySmilyRobot.SPEED
        self.right_or_left = random.choice([self.left_speed, self.right_speed])
        self.animatetimer = 0
        self.speed_y = 0
        self.jumps_left = 1
        self.wall_hit_list = []
        self.stickyblock_hit_list = []
        self.add_to_class_list()
    def update(self):
        if self.rect.topleft != PlaySmilyRobot.OUT_OF_PLAY_TOPLEFT: # This is its out of play location
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
            self.image = self.images["spr_smily_robot_2"]
        if self.animatetimer > 10:
            self.image = self.images["spr_smily_robot"]
            self.animatetimer = 0
    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        else:
            self.speed_y += .25
    def add_to_class_list(self):
        PlaySmilyRobot.smily_robot_list.append(self)
    def remove_from_class_list(self):
        PlaySmilyRobot.smily_robot_list.remove(self)

class PlayStickyBlock(PlayObject):
    sticky_block_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_sticky_block"])
        self.pos = pos
        self.rect.topleft = self.pos
        PlayStickyBlock.sticky_block_list.append(self)
    def restart(self):
        self.rect.topleft = self.pos    
    def add_to_class_list(self):
        PlayStickyBlock.sticky_block_list.append(self)
    def remove_from_class_list(self):
        PlayStickyBlock.sticky_block_list.remove(self)
        
class PlayStandSpikes(PlayObject):
    stand_spikes_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_stand_spikes"])
        self.pos = pos
        PlayStandSpikes.stand_spikes_list.append(self)
        self.fall_var = 0
    def restart(self):
        self.rect.topleft = self.pos
    def add_to_class_list(self):
        PlayStandSpikes.stand_spikes_list.append(self)
    def remove_from_class_list(self):
        PlayStandSpikes.stand_spikes_list.remove(self)
        
class PlayFallSpikes(PlayObject):
    fall_spikes_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_fall_spikes"])
        self.pos = pos
        PlayFallSpikes.fall_spikes_list.append(self)
        self.fall_var = 0
    def restart(self):
        self.rect.topleft = self.pos
        self.fall_var = 0
    def add_to_class_list(self):
        PlayFallSpikes.fall_spikes_list.append(self)
    def remove_from_class_list(self):
        PlayFallSpikes.fall_spikes_list.remove(self)


class PlaySpring(PlayObject):
    spring_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_spring"])
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        PlaySpring.spring_list.append(self)
    def restart(self):
        self.rect.topleft = self.pos
    def add_to_class_list(self):
        PlaySpring.spring_list.append(self)
    def remove_from_class_list(self):
        PlaySpring.spring_list.remove(self)

class PlayPlayer(PlayObject):
    player_list = []
    def __init__(self, pos, play_sprites, images, sounds):
        pygame.sprite.Sprite.__init__(self)
        super().__init__(pos, play_sprites, images["spr_player"])
        self.images = images
        self.sounds = sounds
        self.pos = pos
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
                self.sounds["snd_propeller"].play()
            if self.speed_y > -1.5:
                self.propeller = 0
                self.speed_y += .25
        else:
            self.sounds["snd_propeller"].stop()
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
                    self.image = self.images["spr_player_propeller"]
                if self.playerproptimer > 3:
                    self.image = self.images["spr_player"]
                    self.playerproptimer = 0
            if self.last_pressed_r == 0:
                if self.playerproptimer > 1:
                    self.image = pygame.transform.flip(self.images["spr_player_propeller"], 1, 0)
                if self.playerproptimer > 3:
                    self.image = pygame.transform.flip(self.images["spr_player"], 1, 0)
                    self.playerproptimer = 0
        else:
            if self.last_pressed_r == 1:
                self.image = self.images["spr_player"]
            else:
                self.image = pygame.transform.flip(self.images["spr_player"], 1, 0)
    def restart(self):
        # Game Reset
        self.jumps_left = 1
        self.speed_y = 0
        self.propeller = 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count += 1
        self.rect.topleft = self.pos    
    def add_to_class_list(self):
        PlayPlayer.player_list.append(self)
    def remove_from_class_list(self):
        PlayPlayer.player_list.remove(self)