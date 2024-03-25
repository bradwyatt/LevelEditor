from base_objects import StartGameObject
import pygame

class StartWall(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_wall_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_wall"]
        else:
            self.image = self.images["spr_wall_start"]
        
class StartReverseWall(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_reverse_wall_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_reverse_wall"]
        else:
            self.image = self.images["spr_reverse_wall_start"]
        
class StartDiamonds(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_diamonds_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_diamonds"]
        else:
            self.image = self.images["spr_diamonds_start"]
        
class StartDoor(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_door_closed_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_door_closed"]
        else:
            self.image = self.images["spr_door_closed_start"]
        
class StartFlyer(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_flyer_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_flyer"]
        else:
            self.image = self.images["spr_flyer_start"]
        
class StartSmilyRobot(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_smily_robot_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_smily_robot"]
        else:
            self.image = self.images["spr_smily_robot_start"]
        
class StartSpring(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_spring_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_spring"]
        else:
            self.image = self.images["spr_spring_start"]
        
class StartPlayer(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_player_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_player"]
        else:
            self.image = self.images["spr_player_start"]
        
class StartStickyBlock(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_sticky_block_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_sticky_block"]
        else:
            self.image = self.images["spr_sticky_block_start"]
        
class StartFallSpikes(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_fall_spikes_start"], position)
        self.images = images
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            self.image = self.images["spr_fall_spikes"]
        else:
            self.image = self.images["spr_fall_spikes_start"]
        
class StartStandSpikes(StartGameObject):
    def __init__(self, position, images):
        self.images = images
        self.image = self.images["spr_stand_spikes_0_degrees_start"]
        super().__init__(self.image, position)
        self.rotate = 0
    def change_image_rotation(self, rotate):
        self.rotate = rotate
        if self.rotate == 0:
            self.image = self.images["spr_stand_spikes_0_degrees_start"]
        elif self.rotate == 90:
            self.image = self.images["spr_stand_spikes_90_degrees_start"]
        elif self.rotate == 180:
            self.image = self.images["spr_stand_spikes_180_degrees_start"]
        elif self.rotate == 270:
            self.image = self.images["spr_stand_spikes_270_degrees_start"]
    def toggle_image_start_or_drag(self, dragging_bool):
        if dragging_bool:
            if self.rotate == 0:
                self.image = self.images["spr_stand_spikes_0_degrees"]
            elif self.rotate == 90:
                self.image = self.images["spr_stand_spikes_90_degrees"]
            elif self.rotate == 180:
                self.image = self.images["spr_stand_spikes_180_degrees"]
            elif self.rotate == 270:
                self.image = self.images["spr_stand_spikes_270_degrees"]
        else:
            if self.rotate == 0:
                self.image = self.images["spr_stand_spikes_0_degrees_start"]
            elif self.rotate == 90:
                self.image = self.images["spr_stand_spikes_90_degrees_start"]
            elif self.rotate == 180:
                self.image = self.images["spr_stand_spikes_180_degrees_start"]
            elif self.rotate == 270:
                self.image = self.images["spr_stand_spikes_270_degrees_start"]
        
class RotateButton(StartGameObject):
    def __init__(self, position, images):
        super().__init__(images["spr_rotate_button"], position)
        self.current_stand_spikes_rotate = 0