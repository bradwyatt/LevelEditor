import pygame

class StartGameObject(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image  # Assume image is already loaded
        self.rect = self.image.get_rect(topleft=position)
        
class PlacedObject(pygame.sprite.Sprite):
    object_list = []  # This could be overridden by subclasses if separate lists are needed

    def __init__(self, pos, placed_sprites, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        placed_sprites.add(self)
        self.add_to_class_list()
    
    def add_to_class_list(self):
        # This method will be overridden by subclasses to add the object to the specific list
        pass

    def update(self):
        pass

    def destroy(self):
        self.remove_from_class_list()
        self.kill()
    
    def remove_from_class_list(self):
        # This method will be overridden by subclasses to remove the object from the specific list
        pass
