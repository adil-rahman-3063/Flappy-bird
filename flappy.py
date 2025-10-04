import os
import sys
import pygame, random, time
from pygame.locals import *

#VARIABLES
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT= 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images =  [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY

        #UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]




class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self. image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))


        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize


        self.mask = pygame.mask.from_surface(self.image)


    def update(self):
        self.rect[0] -= GAME_SPEED

        

class Ground(pygame.sprite.Sprite):
    
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    def update(self):
        self.rect[0] -= GAME_SPEED

def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


pygame.init()
# Initialize the mixer after pygame.init() for better compatibility
try:
    pygame.mixer.init()
except Exception:
    # Mixer may fail on some systems; continue without sound
    print('Warning: pygame.mixer failed to initialize. Audio will be disabled.')

screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption('Sayip Bird')

# Basic asset checks to help surface missing file problems early
missing = []
assets_to_check = [
    'assets/sprites/background-day.png',
    'assets/sprites/message.png',
    'assets/sprites/bluebird-upflap.png',
    'assets/sprites/bluebird-midflap.png',
    'assets/sprites/bluebird-downflap.png',
    'assets/sprites/base.png',
    'assets/sprites/pipe-green.png',
    wing,
    hit,
]
for p in assets_to_check:
    if not os.path.exists(p):
        missing.append(p)
if missing:
    print('Error: the following asset files are missing:')
    for m in missing:
        print('  -', m)
    print('\nMake sure you run the script from the project root where the `assets/` folder is located.')
    sys.exit(1)

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()
# Resize the start message so it doesn't touch the edges.
# Keep aspect ratio and limit to a fraction of the screen.
try:
    max_w = int(SCREEN_WIDHT * 0.5)   # at most 50% of screen width
    max_h = int(SCREEN_HEIGHT * 0.12) # at most 12% of screen height
    iw, ih = BEGIN_IMAGE.get_width(), BEGIN_IMAGE.get_height()
    scale = min(1.0, max_w / iw, max_h / ih)
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    BEGIN_IMAGE = pygame.transform.scale(BEGIN_IMAGE, (new_w, new_h))
except Exception:
    # if scaling fails, keep original
    pass

# Compute the Y position to place the message (centered-ish, not touching edges)
BEGIN_POS_Y = int(SCREEN_HEIGHT * 0.12)

# Initialize font for on-screen instructions (helpful for debugging blank windows)
try:
    pygame.font.init()
    FONT = pygame.font.SysFont(None, 22)
except Exception:
    FONT = None

bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()

for i in range (2):
    ground = Ground(GROUND_WIDHT * i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range (2):
    pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])



clock = pygame.time.Clock()

begin = True

while begin:

    clock.tick(15)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # Allow keyboard or mouse click to start
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                try:
                    pygame.mixer.music.load(wing)
                    pygame.mixer.music.play()
                except Exception:
                    pass
                begin = False
        if event.type == MOUSEBUTTONDOWN:
            # left click to start
            if event.button == 1:
                bird.bump()
                try:
                    pygame.mixer.music.load(wing)
                    pygame.mixer.music.play()
                except Exception:
                    pass
                begin = False

    screen.blit(BACKGROUND, (0, 0))
    # center the begin image horizontally for different window sizes
    begin_x = (SCREEN_WIDHT - BEGIN_IMAGE.get_width()) // 2
    screen.blit(BEGIN_IMAGE, (begin_x, BEGIN_POS_Y))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])

        new_ground = Ground(GROUND_WIDHT - 20)
        ground_group.add(new_ground)

    bird.begin()
    ground_group.update()

    bird_group.draw(screen)
    # draw a visible rectangle around the bird to make it easier to see
    try:
        pygame.draw.rect(screen, (255, 0, 0), bird.rect, 2)
    except Exception:
        pass

    # draw an instruction overlay
    if FONT:
        instr = FONT.render('Press Space/Up or Left-click to start', True, (255, 255, 255))
        screen.blit(instr, (10, 10))
    ground_group.draw(screen)

    pygame.display.update()


while True:

    clock.tick(15)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # Allow keyboard or mouse click for bump
        if event.type == KEYDOWN:
            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                try:
                    pygame.mixer.music.load(wing)
                    pygame.mixer.music.play()
                except Exception:
                    pass
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                bird.bump()
                try:
                    pygame.mixer.music.load(wing)
                    pygame.mixer.music.play()
                except Exception:
                    pass

    screen.blit(BACKGROUND, (0, 0))

    if is_off_screen(ground_group.sprites()[0]):
        ground_group.remove(ground_group.sprites()[0])

        new_ground = Ground(GROUND_WIDHT - 20)
        ground_group.add(new_ground)

    if is_off_screen(pipe_group.sprites()[0]):
        pipe_group.remove(pipe_group.sprites()[0])
        pipe_group.remove(pipe_group.sprites()[0])

        pipes = get_random_pipes(SCREEN_WIDHT * 2)

        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    bird_group.update()
    ground_group.update()
    pipe_group.update()

    bird_group.draw(screen)
    pipe_group.draw(screen)
    ground_group.draw(screen)
    # draw a visible rectangle around the bird so it's easy to spot
    try:
        pygame.draw.rect(screen, (255, 0, 0), bird.rect, 2)
    except Exception:
        pass

    # show a small instruction overlay
    if FONT:
        instr = FONT.render('Press Space/Up or Left-click to flap', True, (255, 255, 255))
        screen.blit(instr, (10, 10))

    pygame.display.update()

    if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
        pygame.mixer.music.load(hit)
        pygame.mixer.music.play()
        time.sleep(1)
        break

