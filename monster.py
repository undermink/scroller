import pygame, random, os
from pygame.locals import *

main_dir = os.path.split(os.path.abspath(__file__))[0]

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

class Monster(pygame.sprite.Sprite):
    images = []
    change_x = -2
    change_y = 0
    wait = 10

    def __init__(self):
        super().__init__()
        self.level = None
        self.images = [load_image('monster_platform_1.gif'),
                      pygame.transform.flip(load_image('monster_platform_1.gif'),1, 0),
                      load_image('monster_platform_2.gif'),
                      pygame.transform.flip(load_image('monster_platform_2.gif'),1, 0),
                      load_image('monster_platform_3.gif'),
                      pygame.transform.flip(load_image('monster_platform_3.gif'),1, 0),
                       ]

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(0,0))

    def update(self):
        self.calc_grav()
        self.rect.move_ip(self.change_x,0)
        #self.rect.x += self.change_x
        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
                self.image = self.images[0]
                self.change_x = -2
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
                self.change_x = 2
                self.image = self.images[1]

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

    def attack(self):
        if self.change_x > 0:
            if self.image == self.images[5]:
                self.image = self.images[1]
            else:
                self.image = self.images[5]
        else:
            if self.image == self.images[4]:
                self.image = self.images[0]
            else:
                self.image = self.images[4]

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT and self.change_y >= 0:
            self.kill()
