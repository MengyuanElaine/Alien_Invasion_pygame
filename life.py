import pygame
from pygame.sprite import Sprite

class Life(Sprite):
    def __init__(self,screen):
        super(Life,self).__init__()
        self.screen=screen
        self.screen_rect=screen.get_rect()
        self.image=pygame.image.load("image//heart.jpg")
        self.rect=self.image.get_rect()

        
        
