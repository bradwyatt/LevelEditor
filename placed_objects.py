from base_objects import PlacedObject

class PlacedWall(PlacedObject):
    wall_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_wall"])

    def add_to_class_list(self):
        PlacedWall.wall_list.append(self)

    def remove_from_class_list(self):
        PlacedWall.wall_list.remove(self)
        
class PlacedReverseWall(PlacedObject):
    reverse_wall_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_reverse_wall"])

    def add_to_class_list(self):
        PlacedReverseWall.reverse_wall_list.append(self)

    def remove_from_class_list(self):
        PlacedReverseWall.reverse_wall_list.remove(self)
        
class PlacedDiamonds(PlacedObject):
    diamonds_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_diamonds"])

    def add_to_class_list(self):
        PlacedDiamonds.diamonds_list.append(self)

    def remove_from_class_list(self):
        PlacedDiamonds.diamonds_list.remove(self)
        
class PlacedFlyer(PlacedObject):
    flyer_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_flyer"])

    def add_to_class_list(self):
        PlacedFlyer.flyer_list.append(self)

    def remove_from_class_list(self):
        PlacedFlyer.flyer_list.remove(self)
        
class PlacedSmilyRobot(PlacedObject):
    smily_robot_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_smily_robot"])

    def add_to_class_list(self):
        PlacedSmilyRobot.smily_robot_list.append(self)

    def remove_from_class_list(self):
        PlacedSmilyRobot.smily_robot_list.remove(self)
        
class PlacedSpring(PlacedObject):
    spring_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_spring"])

    def add_to_class_list(self):
        PlacedSpring.spring_list.append(self)

    def remove_from_class_list(self):
        PlacedSpring.spring_list.remove(self)
        
class PlacedStickyBlock(PlacedObject):
    sticky_block_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_sticky_block"])

    def add_to_class_list(self):
        PlacedStickyBlock.sticky_block_list.append(self)

    def remove_from_class_list(self):
        PlacedStickyBlock.sticky_block_list.remove(self)
        
class PlacedFallSpikes(PlacedObject):
    fall_spikes_list = []

    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_fall_spikes"])

    def add_to_class_list(self):
        PlacedFallSpikes.fall_spikes_list.append(self)

    def remove_from_class_list(self):
        PlacedFallSpikes.fall_spikes_list.remove(self)
        
class PlacedStandSpikes(PlacedObject):
    stand_spikes_list = []

    def __init__(self, pos, placed_sprites, images, rotate=0):
        super().__init__(pos, placed_sprites, images["spr_stand_spikes_0_degrees"])
        self.images = images
        self.rotate = rotate
        if self.rotate == 0:
            self.image = self.images["spr_stand_spikes_0_degrees"]
        elif self.rotate == 90:
            self.image = self.images["spr_stand_spikes_90_degrees"]
        elif self.rotate == 180:
            self.image = self.images["spr_stand_spikes_180_degrees"]
        elif self.rotate == 270:
            self.image = self.images["spr_stand_spikes_270_degrees"]

    def add_to_class_list(self):
        PlacedStandSpikes.stand_spikes_list.append(self)

    def remove_from_class_list(self):
        PlacedStandSpikes.stand_spikes_list.remove(self)
        
class PlacedPlayer(PlacedObject):
    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_player"])
        
class PlacedDoor(PlacedObject):
    def __init__(self, pos, placed_sprites, images):
        super().__init__(pos, placed_sprites, images["spr_door_closed"])