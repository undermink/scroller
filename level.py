import pygame, random, os
from pygame.locals import *
from monster import Monster

main_dir = os.path.split(os.path.abspath(__file__))[0]

BLUE = (0, 0, 255)

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

class Level():
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.bonus_list = pygame.sprite.Group()
        self.shot_list = pygame.sprite.Group()
        self.cracks_list = pygame.sprite.Group()
        self.player = player
        self.startx = 40
        self.starty = 0

        # How far this world has been scrolled left/right
        self.world_shift = 0

    # Update everything in this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
        self.coin_list.update()
        self.bonus_list.update()
        self.shot_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """

        # Draw the background
        screen.fill(BLUE)

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.coin_list.draw(screen)
        self.shot_list.draw(screen)
        self.bonus_list.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for coin in self.coin_list:
            coin.rect.x += shift_x

        for bonus in self.bonus_list:
            bonus.rect.x += shift_x

        for shot in self.shot_list:
            shot.rect.x += shift_x

        for cracks in self.cracks_list:
            cracks.rect.x += shift_x

    def parse_level(self, level):
        x = 0
        y = 0
        for platform in level.strip():
            if platform == '#':
                block = Platform()
                block.rect.x = x
                block.rect.y = y
                block.image = random.choice(block.images[0:3])
                block.player = self.player
                self.platform_list.add(block)
            if platform == '.':
                pass
            if platform == 'f':
                gun = Gun()
                gun.rect.x = x
                gun.rect.y = y+15
                self.type = 'gun'
                self.bonus_list.add(gun)
            if platform == 'x':
                monster = Monster()
                monster.rect.x = x
                monster.rect.y = y
                monster.level = self
                self.enemy_list.add(monster)
            if platform == 'o':
                coin = Coin()
                coin.rect.x = x+15
                coin.rect.y = y+15
                coin.level = self
                self.coin_list.add(coin)
            if platform == 'v':
                heart = Heart()
                heart.rect.x = x
                heart.rect.y = y
                heart.level = self
                self.bonus_list.add(heart)
            if platform == 'p':
                self.startx = x
                self.starty = y
            if x < self.parser_limit:
                x += 100
            else:
                x = 0
                y += 100

# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -3000
        self.parser_limit = 4000
        ground = """
........................................
........................................
......................o.v.o.............
..............x.............x...........
..v.#..oo.....#...x..###.####...........
..##....x....##.#.#.#......o..#....x....
p.ooo.........#o..o.....................
#......##...###......x..#.........##....
########################################
########################################
"""
        self.parse_level(ground.strip())

class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -2950
        self.parser_limit = 4000

        ground = """
########################################
#......................................#
#oo...v.........oo.............o.......#
#....x.........x..x..........#..x......#
#....###.......####x.........####......#
#p..#....x.#..#.oo.#...#...........#...#
#..#ovo................................#
#.#......#.........f#....#....x..#...###
########################################
########################################
"""
        self.parse_level(ground.strip())

class Level_03(Level):
    """ Definition for level 3. """

    def __init__(self, player):
        """ Create level 3. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -3000
        self.parser_limit = 4000

        ground = """
........................................
.p......................................
###...v.........oo.....o.......v........
.....x.........x..x....o.....#..x#......
....####.......####x...o..#..#####......
....#......####....#...#.......ooo.#....
..####................ooo...............
..#.fv.o##..........######....####...###
..##...x.#..................oo..........
..########.................####.........
"""
        self.parse_level(ground.strip())

class Level_04(Level):
    """ Definition for level 4. """

    def __init__(self, player):
        """ Create level 4. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.level_limit = -3000
        self.parser_limit = 4000

        ground = """
........v...............................
#.o..o..o..o..o..o..................ovo.
##x..x..#..xf.#......o.............#.x.#
##############...#...#.............#####
.........................x.....#####....
..p....................x.###............
..#...x.....x.........###...............
#..................###.......o....o.....
##....#.....#....##.....................
############.####............#....#....#
"""
        self.parse_level(ground.strip())

class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [load_image('stone_1.gif'),
                       load_image('stone_1a.gif'),
                       load_image('stone_1b.gif'),
                       load_image('stone_2.gif'),
                       load_image('cracks_1.gif'),
                       ]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.cracks = None
        self.damaged = False


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [load_image('coin.gif')]
        self.images = [load_image('coin.gif')]
        self.image = self.images[0]
        self.rect = self.image.get_rect()

class Gun(pygame.sprite.Sprite):
    type = 'gun'
    def __init__(self):
        super().__init__()
        self.player = None
        self.images = [load_image('gun_1.gif'),
                       pygame.transform.flip(load_image('gun_1.gif'),1, 0)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def update(self):
        if self.player:
            if self.player.facing == 0:
                self.image = self.images[1]
                self.rect.x = self.player.rect.x-35
                self.rect.y = self.player.rect.y+85

            else :
                self.image = self.images[0]
                self.rect.x = self.player.rect.x+35
                self.rect.y = self.player.rect.y+85

class Heart(pygame.sprite.Sprite):
    type = 'heart'
    wait = 10
    def __init__(self):
        super().__init__()
        self.images = [load_image('heart_1.gif'),
                        load_image('heart_1a.gif')]

        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def update(self):
        if self.wait > 0:
            self.wait -= 1
        else:
            self.wait = 10
            if self.image == self.images[0]:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
