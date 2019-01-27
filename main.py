import os
import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(name)
        self.rect = self.image.get_rect()
        self.rect.x = self.rect[0]
        self.rect.y = self.rect[1]


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group)
        self.image = load_image('character.png')
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self):
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > width - 29:
            self.rect.x = width - 29
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > height - 36:
            self.rect.y = height - 36


class Enemy(pygame.sprite.Sprite):
    def __init__(self, type='ghost'):
        super().__init__(enemy_group)
        if type == 'ghost':
            self.image = load_image('ghost.png')
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

pygame.init()
size = width, height = 500, 800
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
background = Background('bg.png')
player = Player()
player.rect = player.image.get_rect()
player.rect.x = width // 2
player.rect.y = (height // 4) * 3

fps = 60
speed = 1
clock = pygame.time.Clock()
shift = False
bg_flag = True
bg_number = -1

while 1:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
        elif e.type == pygame.KEYDOWN:
            if e.mod == pygame.KMOD_LSHIFT:
                if not shift:
                    speed *= 2
                shift = True
            elif shift:
                speed //= 2
                shift = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.rect.y -= speed
    if keys[pygame.K_DOWN]:
        player.rect.y += speed
    if keys[pygame.K_LEFT]:
        player.rect.x -= speed
    if keys[pygame.K_RIGHT]:
        player.rect.x += speed
    screen.blit(background.image, background.rect)
    if -1500 >= background.rect.y and bg_flag:
        bg_number = -bg_number
        bg_flag = False
    elif background.rect.y >= 0 and not bg_flag:
        bg_number = -bg_number
        bg_flag = True
    background.rect.y += bg_number
    player_group.draw(screen)
    player_group.update()
    clock.tick(fps)
    pygame.display.flip()

pygame.quit()