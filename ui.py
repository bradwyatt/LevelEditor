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
        

def _make_button_with_bg(icon, size=72, bg_color=(240, 200, 50), border_color=(180, 140, 20), border=3):
    surf = pygame.Surface((size, size))
    surf.fill(border_color)
    surf.fill(bg_color, (border, border, size - border * 2, size - border * 2))
    icon_scaled = pygame.transform.scale(icon, (size - 16, size - 16))
    offset = (size - icon_scaled.get_width()) // 2
    surf.blit(icon_scaled, (offset, offset))
    return surf


def _make_text_button(label, size=(72, 72), bg_color=(240, 200, 50), border_color=(180, 140, 20), text_color=(70, 52, 10), border=3):
    surf = pygame.Surface(size)
    surf.fill(border_color)
    surf.fill(bg_color, (border, border, size[0] - border * 2, size[1] - border * 2))
    font = pygame.font.SysFont("Arial", 18, bold=True)
    lines = label.split("\n")
    text_surfaces = [font.render(line, True, text_color) for line in lines]
    total_height = sum(text.get_height() for text in text_surfaces) + max(0, len(text_surfaces) - 1) * 4
    y = (size[1] - total_height) // 2
    for text_surface in text_surfaces:
        text_rect = text_surface.get_rect(centerx=size[0] // 2, y=y)
        surf.blit(text_surface, text_rect)
        y += text_surface.get_height() + 4
    return surf


class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = _make_button_with_bg(images["spr_save_file_button"])
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos, images):
        pygame.sprite.Sprite.__init__(self)
        self.image = _make_button_with_bg(images["spr_load_file_button"])
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class MainMenuButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = _make_text_button("Main\nMenu")
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
