import pygame

class StartGameObject(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image  # Assume image is already loaded
        self.rect = self.image.get_rect(topleft=position)