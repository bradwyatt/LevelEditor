from base_objects import PlayObject
import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT

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
    def restart(self):
        self.rect.topleft = self.pos
        self.image = self.images["spr_diamonds"]
    def add_to_class_list(self):
        PlayDiamonds.diamonds_list.append(self)
    def remove_from_class_list(self):
        PlayDiamonds.diamonds_list.remove(self)
        
class PlayDoor(PlayObject):
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_door_closed"])
        self.pos = pos
        self.images = images
        play_sprites.add(self)
    def open_or_close(self, score, diamonds_list):
        if score == len(diamonds_list):
            return self.images["spr_door_open"]
        return self.images["spr_door_closed"]
    def restart(self):
        self.rect.topleft = self.pos
        
class PlaySmilyRobot(PlayObject):
    smily_robot_list = []
    SPEED = 2
    GRAVITY = 0.25
    OUT_OF_PLAY_TOPLEFT = (-100, SCREEN_HEIGHT+100)

    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_smily_robot"])
        self.pos = pos
        self.rect.topleft = self.pos
        self.images = images
        self.speed_x = self.SPEED * random.choice([-1, 1])
        self.animatetimer = 0
        self.speed_y = 0
    
    def update(self):
        # Apply horizontal and vertical movements
        self.handle_movement()
    
        # Check and handle horizontal collisions first
        self.check_horizontal_collisions()
    
        # Apply gravity before checking vertical collisions to ensure accurate collision detection
        self.calc_grav()
    
        # Then check and handle vertical collisions
        self.check_vertical_collisions()
    
        # Handle interactions with reverse walls, which might affect horizontal direction
        self.handle_reverse_walls()
    
        # Update the animation based on the smily robot's current state
        self.animate()
        
    def restart(self):
        self.rect.topleft = self.pos
        self.speed_x = self.SPEED * random.choice([-1, 1])

    def handle_movement(self):
        # Move horizontally with boundary checking
        self.rect.x += self.speed_x
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1  # Change direction if hitting screen bounds
            
    def check_horizontal_collisions(self):
        # Predict the next horizontal position
        next_position = self.rect.x + self.speed_x
        self.rect.x = next_position
    
        # Detect horizontal collisions
        collided_blocks = pygame.sprite.spritecollide(self, PlayWall.wall_list + PlayStickyBlock.sticky_block_list, False)
        if collided_blocks:
            # If moving right but collided, place the robot to the left of the block
            if self.speed_x > 0:
                self.rect.right = min(block.rect.left for block in collided_blocks)
            # If moving left but collided, place the robot to the right of the block
            elif self.speed_x < 0:
                self.rect.left = max(block.rect.right for block in collided_blocks)
            # Reverse direction
            self.speed_x *= -1

    def check_vertical_collisions(self):
        # Predict the next vertical position
        next_position = self.rect.y + self.speed_y
        self.rect.y = next_position
    
        # Detect vertical collisions
        collided_blocks = pygame.sprite.spritecollide(self, PlayWall.wall_list + PlayStickyBlock.sticky_block_list, False)
        if collided_blocks:
            # If falling down but collided, place the robot on top of the block
            if self.speed_y > 0:
                self.rect.bottom = min(block.rect.top for block in collided_blocks)
                self.speed_y = 0  # Stop the fall
            # If moving up but collided, place the robot below the block
            elif self.speed_y < 0:
                self.rect.top = max(block.rect.bottom for block in collided_blocks)
                self.speed_y = 0  # Stop the ascent
    
    def handle_reverse_walls(self):
        # Detect collisions with reverse walls
        collided_reverse_walls = pygame.sprite.spritecollide(self, PlayReverseWall.reverse_wall_list, False)
        if collided_reverse_walls:
            # Immediately reverse direction upon collision
            self.speed_x *= -1
            # Slight position adjustment to prevent repeated collisions
            self.rect.x += self.speed_x




    def calc_grav(self):
        if self.rect.top < SCREEN_HEIGHT:
            self.speed_y += self.GRAVITY
        else:
            self.speed_y = 0
            self.rect.topleft = self.OUT_OF_PLAY_TOPLEFT
        # Apply vertical movement
        self.rect.y += self.speed_y

    def animate(self):
        # Animation logic remains the same
        self.animatetimer += 1
        if self.animatetimer > 5:
            self.image = self.images["spr_smily_robot_2"]
        if self.animatetimer > 10:
            self.image = self.images["spr_smily_robot"]
            self.animatetimer = 0
            
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
    def add_to_class_list(self):
        PlayStickyBlock.sticky_block_list.append(self)
    def remove_from_class_list(self):
        PlayStickyBlock.sticky_block_list.remove(self)
        
class PlayStandSpikes(PlayObject):
    stand_spikes_list = []
    def __init__(self, pos, play_sprites, images):
        super().__init__(pos, play_sprites, images["spr_stand_spikes"])
        self.pos = pos
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
    def restart(self):
        self.rect.topleft = self.pos
    def add_to_class_list(self):
        PlaySpring.spring_list.append(self)
    def remove_from_class_list(self):
        PlaySpring.spring_list.remove(self)

class PlayPlayer(PlayObject):
    # Constants for physics and gameplay adjustments
    GRAVITY = 0.25
    PROP_GRAVITY = 0.01
    MAX_PROP_SPEED = -2
    PROP_ACCELERATION = 0.25
    JUMP_SPEED = -7
    DOUBLE_JUMP_SPEED = -2
    MOVE_SPEED = 4
    def __init__(self, pos, play_sprites, images, sounds):
        pygame.sprite.Sprite.__init__(self)
        super().__init__(pos, play_sprites, images["spr_player"])
        self.images = images
        self.sounds = sounds
        self.pos = pos
        self.speed_x, self.speed_y = 0, 0
        self.jumps_left = 2
        self.propeller, self.playerproptimer = 0, 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count = 0
        self.wall_hit_list = []
        self.stickyblock_hit_list = []
        self.jump_counter = 0
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
        self.speed_x = -self.MOVE_SPEED
        self.last_pressed_r = 0  # Indicates moving left
    def go_right(self):
        self.speed_x = self.MOVE_SPEED
        self.last_pressed_r = 1  # Indicates moving right
    def stop(self):
        self.speed_x = 0
    def calc_grav(self):
        if self.speed_y == 0:
            self.speed_y = 1
        elif self.propeller:
            self.speed_y += self.PROP_GRAVITY
            if self.speed_y >= self.MAX_PROP_SPEED:
                self.sounds["snd_propeller"].play()
            if self.speed_y > -1.5:
                self.propeller = 0
                self.speed_y += self.PROP_ACCELERATION
        else:
            self.sounds["snd_propeller"].stop()
            self.speed_y += self.GRAVITY
    def on_ground(self):
        self.rect.y += 1  # Temporarily adjust position to check for collisions below
        wall_hit_list = pygame.sprite.spritecollide(self, PlayWall.wall_list, False)
        stickyblock_hit_list = pygame.sprite.spritecollide(self, PlayStickyBlock.sticky_block_list, False)
        self.rect.y -= 1  # Reset position
    
        on_ground = bool(wall_hit_list or stickyblock_hit_list)
        on_sticky = bool(stickyblock_hit_list)
        return on_ground, on_sticky
    def jump(self):
        on_ground, on_sticky = self.on_ground()
        if on_ground and not on_sticky:
            # Perform the first jump if on the ground and not on a sticky block.
            self.speed_y = self.JUMP_SPEED
            self.jumps_left = 1  # Set to allow for the propeller jump next.
            self.animate_jump()
        elif not on_ground and self.jumps_left >= 1:
            # Allows for a propeller jump if in the air and haven't used the propeller jump yet.
            self.speed_y = self.DOUBLE_JUMP_SPEED
            self.propeller = 1
            self.jumps_left = 0  # No more jumps left after this.
            self.animate_jump()

    def can_jump(self):
        return self.jumps_left > 0

    def perform_jump(self):
        if self.wall_hit_list:  # On a platform
            self.speed_y = self.JUMP_SPEED
            self.jumps_left -= 1
        elif not self.wall_hit_list and self.jumps_left == 1:  # Mid-air jump
            self.speed_y = self.DOUBLE_JUMP_SPEED
            self.propeller = 1
            self.jumps_left = 0
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
    def animate_jump(self):
        # Check if the propeller is to be used, indicating a second jump in a double jump
        if self.propeller:
            # Reset or initialize the propeller animation timer
            self.playerproptimer = 0
    
            # Play the propeller sound if it exists
            if "snd_propeller" in self.sounds:
                self.sounds["snd_propeller"].play()
    
            # The actual propeller animation logic will continue to be handled by `animate_images`
            # so no additional logic is needed here to change the image directly.
    
        else:
            # For a regular jump (first jump in the double jump sequence or a single jump),
            # you might want to reset the player image or set any initial jump animation
            # This is more relevant if you have a specific animation for the start of a jump.
            self.image = self.images["spr_player"]
            # If there's a jump sound, you could play it here as well
            if "snd_jump" in self.sounds:
                self.sounds["snd_jump"].play()
    
        # Note: The continuous animation of the propeller (if applicable) and resetting back to the normal
        # state after the propeller animation ends are handled within the `animate_images` method,
        # which should be called in your game loop's update phase.
    def restart(self):
        # Game Reset
        self.jumps_left = 2
        self.speed_y = 0
        self.propeller = 0
        self.last_pressed_r = 1
        self.score = 0
        self.death_count += 1
        self.rect.topleft = self.pos