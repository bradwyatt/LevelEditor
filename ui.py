import pygame

class ClearButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_clear_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class InfoButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_info_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class EraserButton(pygame.sprite.Sprite):
    def __init__(self, pos, eraser_mode_active, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        self.image = images["spr_eraser_not_selected_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def toggle_eraser_button_image(self, eraser_mode_active):
        if eraser_mode_active == True:
            self.image = self.images["spr_eraser_selected_button"]
        else:
            self.image = self.images["spr_eraser_not_selected_button"]
        
        

class RestartButton(pygame.sprite.Sprite):
    def __init__(self, pos, play_sprites, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_restart_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        play_sprites.add(self)

class GridButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_grid_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
        self.grid_on_var = 1
        

class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_save_file_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        

class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["spr_load_file_button"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
