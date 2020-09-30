#!/usr/bin/env python

import pygame, random, os
from pygame.locals import *

# Global constants

main_dir = os.path.split(os.path.abspath(__file__))[0]

SCORE = 0
LIFE = 10
LIVES = 3
KILLS = 0
# equipment
GUN = False
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen dimensions
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

def get_distance(bottom1,bottom2):
    if bottom1 > bottom2:
        return bottom1 - bottom2
    else:
        return bottom2 - bottom1

class Player(pygame.sprite.Sprite):

    frame = 48
    animcycle = 4
    images = []
    walk_right = []
    walk_left = []
    walk = 1
    facing = 1
    wait = 5
    hand = None
    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(0,0))

        # Set a referance to the image rect.
#        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        self.shot_list = pygame.sprite.Group()
        self.gun = None
        self.level = None

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

#        if self.change_x > 0:
#            self.frame = self.frame - 1
#            self.image = self.walk_right[self.frame//self.animcycle%3]
#        if self.change_x < 0:
#            self.frame = self.frame - 1
#            self.image = self.walk_left[self.frame//self.animcycle%3]
#        if self.frame == 0:
#            frame = 48

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

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

    def calc_grav(self):
        """ Calculate effect of gravity. """
        global LIVES
        global LIFE
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35



    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -12

    # Player-controlled movement:
    def go_left(self):
        self.change_x = -6
        self.image = self.images[4]
        self.facing = 0

    def go_right(self):
        self.facing = 1
        self.change_x = 6
        if self.walk == 1:
            self.image = self.images[2]
            self.walk = 0
        else:
            self.image = self.images[1]
            self.walk = 1


    def stop(self):
        if self.facing == 1:
            self.change_x = 0
            self.image = self.images[0]
        else:
            self.change_x = 0
            self.image = self.images[3]


    def hurt(self):
        if self.facing == 1:
            self.image = self.images[7]
        else:
            self.image = self.images[8]

    def shoot(self, what):
        if what == 'gun':
            shot = Shot()
            shot.rect.y = self.rect.y + 105
            if self.facing == 1:
                shot.rect.x = self.rect.right + 50
                shot.facing = 0
                self.image = self.images[0]
            else:
                shot.rect.x = self.rect.left - 50
                shot.facing = 1
                self.image = self.images[3]
#            print("shooting at %s %s" %(shot.rect.x,shot.rect.y))
            self.shot_list.add(shot)
        #else:
#            print('not shooting %'%what)

    def kick(self):
        if self.facing == 1:
            self.image = self.images[5]
        else:
            self.image = self.images[6]
        monster_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
#        for monster in monster_hit_list:
#            monster.kill()
        for monster in self.level.enemy_list:
            if monster.rect.x > self.rect.x:
                if monster.rect.left - self.rect.right <= 50:
                    #print("monster at %s %s" %(monster.rect.y, monster.rect.x))
                    #print("self at %s %s" %(self.rect.y,self.rect.x))
                    #if monster in monster_hit_list:
                    #    monster.kill()
                    distance = get_distance(self.rect.bottom,monster.rect.bottom)
                    if distance < 50:
                        Explosion(monster)
                        monster.kill()
            else:
                if self.rect.left - monster.rect.right <= 1:
                    if monster in monster_hit_list:
                        Explosion(monster)
                        monster.kill()
#                    if self.rect.bottom == monster.rect.bottom:
#                        monster.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.cracks = None
        self.damaged = False


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = self.images[0]
        self.rect = self.image.get_rect()

class Gun(pygame.sprite.Sprite):
    type = 'gun'
    def __init__(self):
        super().__init__()
        self.player = None
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


class Shot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.facing = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def update(self):
        if self.facing == 0:
            self.rect.x += 10
        else:
            self.rect.x -= 10


class Heart(pygame.sprite.Sprite):
    type = 'heart'
    wait = 10
    def __init__(self):
        super().__init__()
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

class Monster(pygame.sprite.Sprite):
    images = []
    change_x = -2
    change_y = 0
    wait = 10

    def __init__(self):
        super().__init__()
        self.level = None

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

class Explosion(pygame.sprite.Sprite):
    animcycle = 4
    frame = 12
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = actor.rect.x
        self.rect.y = actor.rect.y

    def update(self):
        self.frame = self.frame - 1
        self.image = self.images[self.frame//self.animcycle%3]
        if self.frame == 0:
            self.kill()

class StoneBurst(pygame.sprite.Sprite):
    animcycle = 4
    frame = 12
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = actor.rect.x
        self.rect.y = actor.rect.y

    def update(self):
        self.frame = self.frame - 1
        self.image = self.images[self.frame//self.animcycle%3]
        if self.frame == 0:
            self.kill()

class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 0)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "SCORE: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)

class Stats(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = Color('white')
        self.lastlife = -1
        self.update()
        self.rect = self.image.get_rect().move(SCREEN_WIDTH - 200, 0)

    def update(self):
        if LIFE != self.lastlife:
            self.lastlife = LIFE
            msg = "KP: %d | %d UP" %(LIFE,LIVES)
            self.image = self.font.render(msg, 0, self.color)

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

def main():
    """ Main Program """
    pygame.init()

    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Side-scrolling Platformer")
    Player.images = [load_image('player_platform_1.gif'),
                     load_image('player_platform_2.gif'),
                     load_image('player_platform_2.gif'),
                     pygame.transform.flip(load_image('player_platform_1.gif'),1,0),
                     pygame.transform.flip(load_image('player_platform_2.gif'),1,0),
                     load_image('player_platform_3.gif'),
                     pygame.transform.flip(load_image('player_platform_3.gif'),1,0),
                     load_image('player_platform_4.gif'),
                     pygame.transform.flip(load_image('player_platform_4.gif'),1,0),
                     ]
    Player.walk_right = [load_image('player_platform_2.gif'),
                         load_image('player_platform_2.gif'),
                         load_image('player_platform_walk.gif'),
                         load_image('player_platform_walk.gif'),
                     ]

    Player.walk_left = [pygame.transform.flip(load_image('player_platform_2.gif'),1,0),
                        pygame.transform.flip(load_image('player_platform_2.gif'),1,0),
                        pygame.transform.flip(load_image('player_platform_walk.gif'),1,0),
                        pygame.transform.flip(load_image('player_platform_walk.gif'),1,0),
                        ]
    Platform.images = [load_image('stone_1.gif'),
                       load_image('stone_1a.gif'),
                       load_image('stone_1b.gif'),
                       load_image('stone_2.gif'),
                       load_image('cracks_1.gif'),
                       ]
    Monster.images = [load_image('monster_platform_1.gif'),
                      pygame.transform.flip(load_image('monster_platform_1.gif'),1, 0),
                      load_image('monster_platform_2.gif'),
                      pygame.transform.flip(load_image('monster_platform_2.gif'),1, 0),
                      load_image('monster_platform_3.gif'),
                      pygame.transform.flip(load_image('monster_platform_3.gif'),1, 0),
                      ]
    Coin.images = [load_image('coin.gif')]
    Heart.images = [load_image('heart_1.gif'),
                    load_image('heart_1a.gif')]
    Gun.images = [load_image('gun_1.gif'),
                  pygame.transform.flip(load_image('gun_1.gif'),1, 0)]
    Shot.images = [load_image('shot.gif')]
    Explosion.images = [load_image('boom_1c.gif'),
        load_image('boom_1b.gif'),
        load_image('boom_1a.gif'),
        load_image('boom_1.gif'),
    ]
    StoneBurst.images = [load_image('stone_boom_1.gif'),
        load_image('stone_boom_1a.gif'),
        load_image('stone_boom_1b.gif'),
        load_image('stone_boom_1c.gif'),
    ]
    # Create the player
    player = Player()
    score = Score()
    stats = Stats()
    global SCORE
    global LIFE
    global LIVES
    global GUN
    global KILLS
    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))
    level_list.append(Level_03(player))
    level_list.append(Level_04(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    active_sprite_list.add(score)
    active_sprite_list.add(stats)
    player.level = current_level

    for monster in current_level.enemy_list:
        active_sprite_list.add(monster)
    player.rect.x = current_level.startx
    player.rect.y = current_level.starty
    active_sprite_list.add(player)

    for coin in current_level.coin_list:
        active_sprite_list.add(coin)

    for bonus in current_level.bonus_list:
        active_sprite_list.add(bonus)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_a:
                    if player.hand == 'gun':
#                        print("shooting %s" %player.hand)
                        player.shoot(player.hand)
                    if player.hand == None:
#                        print(player.hand)
                        player.kick()
                if event.key == pygame.K_s:
                    if player.hand == None:
                        if GUN:
                            player.hand = 'gun'
                            gun = Gun()
                            gun.rect.x = player.rect.x+35
                            gun.rect.y = player.rect.y+85
                            gun.player = player
                            player.gun = gun
                            active_sprite_list.add(gun)
                    elif player.hand == 'gun':
                        player.hand = None
                        player.gun.kill()

                if event.key == pygame.K_q:
                    done = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
                if event.key == pygame.K_a and player.hand == None:
                    player.stop()

        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= 300:
            diff = 300 - player.rect.left
            player.rect.left = 300
            current_position = player.rect.x - current_level.world_shift
            if current_position > 0:
                current_level.shift_world(diff)

        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            if current_level_no < len(level_list)-1:
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level
                player.rect.x = current_level.startx
                player.rect.y = current_level.starty
                current_level.update()
                active_sprite_list.update()
            else:
                done = True
                print("")
                print("##########################")
                print("#                        #")
                print("#  THE END - YOU WIN!    #")
                print("#                        #")
                print("#  COINS: %s             #" % SCORE)
                print("#  HEALTH: %s            #" % LIFE)
                print("#  LIVES LEFT: %s        #" % LIVES)
                print("#                        #")
                print("#  MONSTERS KILLED: %s   #" % KILLS)
                print("#                        #")
                print("#  G A M E O V E R !     #")
                print("#                        #")
                print("##########################")
                print("")
                print("--- thanks for playing the scroller.py ---")
                print("                   :)")

        # See if we are on the ground.
        if player.rect.y >= SCREEN_HEIGHT and player.change_y >= 0:
            player.hurt()
            if LIVES > 0:
                LIVES -= 1
                LIFE = 10
                player.rect.x = current_level.startx + current_level.world_shift
                player.rect.y = current_level.starty
            else:
                player.kill()
                done = True

        coin_hit_list = pygame.sprite.spritecollide(player,current_level.coin_list, False)
        for coin in coin_hit_list:
            coin.kill()
            SCORE = SCORE + 1

        bonus_hit_list = pygame.sprite.spritecollide(player,current_level.bonus_list, False)
        for bonus in bonus_hit_list:
            if bonus.type == 'gun' and GUN == False:
                bonus.rect.x = player.rect.x+35
                bonus.rect.y = player.rect.y+85
                player.hand = 'gun'
                bonus.player = player
                player.gun = bonus
                GUN = True
            if bonus.type == 'heart':
                bonus.kill()
                LIFE += 10

        enemy_hit_list = pygame.sprite.spritecollide(player,current_level.enemy_list, False)
        for enemy in enemy_hit_list:
            if enemy.wait >= 0:
                enemy.wait -= 1
            else:
                enemy.wait = 10
                enemy.attack()
                player.hurt()
                LIFE -= 1
            if LIFE <= 0:
                if LIVES > 0:
                    LIVES -= 1
                    LIFE = 10
                    player.rect.x = current_level.startx
                    player.rect.y = current_level.starty
                else:
                    player.kill()
                    done = True
        for shot in player.shot_list:
            active_sprite_list.add(shot)
            shot_hit_list = pygame.sprite.spritecollide(shot, current_level.enemy_list, False)
            for monster in shot_hit_list:
                explosion = Explosion(monster)
                explosion.rect.x = monster.rect.x
                explosion.rect.y = monster.rect.y
                active_sprite_list.add(explosion)
                current_level.cracks_list.add(explosion)
                monster.kill()
                KILLS += 1
                shot.kill()
            shot_hit_list = pygame.sprite.spritecollide(shot, current_level.platform_list, False)
            for stone in shot_hit_list:
                if stone.damaged == False:
#                    print("damaging stone...")
                    stone.damaged = True
                    cracks = Platform()
                    cracks.image = cracks.images[4]
                    cracks.rect.x = stone.rect.x
                    cracks.rect.y = stone.rect.y
                    stone.cracks = cracks
                    active_sprite_list.add(cracks)
                    current_level.cracks_list.add(cracks)
                else:
#                    print("stone already damaged - destroying stone...")
                    stone.cracks.kill()
                    explosion = StoneBurst(stone)
                    explosion.rect.x = stone.rect.x
                    explosion.rect.y = stone.rect.y
                    active_sprite_list.add(explosion)
                    current_level.cracks_list.add(explosion)
                    stone.kill()
                shot.kill()


        current_level.draw(screen)
        active_sprite_list.draw(screen)

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
