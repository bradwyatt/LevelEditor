from base_objects import StartGameObject
import pygame

class StartWall(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_wall"], position)
        
class StartReverseWall(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_reverse_wall"], position)
        
class StartDiamonds(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_diamonds"], position)
        
class StartDoor(StartGameObject):
    def __init__(self, position, images):
        super().__init__(pygame.transform.smoothscale(images["spr_door_closed"], (24, 40)),
                         position)
        
class StartFlyer(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_flyer"], position)
        
class StartSmilyRobot(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_smily_robot"], position)
        
class StartSpring(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_spring"], position)
        
class StartPlayer(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_player"], position)
        
class StartStickyBlock(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_sticky_block"], position)
        
class StartFallSpikes(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_fall_spikes"], position)
        
class StartStandSpikes(StartGameObject):
    def __init__(self, position, images):
        self.images = images
        self.image = self.images["spr_stand_spikes_0_degrees"]
        super().__init__(self.image, position)
    def change_image_rotation(self, rotate):
        self.rotate = rotate
        if self.rotate == 0:
            self.image = self.images["spr_stand_spikes_0_degrees"]
        elif self.rotate == 90:
            self.image = self.images["spr_stand_spikes_90_degrees"]
        elif self.rotate == 180:
            self.image = self.images["spr_stand_spikes_180_degrees"]
        elif self.rotate == 270:
            self.image = self.images["spr_stand_spikes_270_degrees"]
        
class RotateButton(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_rotate_button"], position)
        self.current_stand_spikes_rotate = 0