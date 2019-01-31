import os
import random
import math
import pygame


class Background(pygame.sprite.Sprite):  # класс фона, нужен для прокрутки
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(name)
        self.rect = self.image.get_rect()
        self.rect.x = self.rect[0]
        self.rect.y = self.rect[1]


class Player(pygame.sprite.Sprite):  # класс игрока
    def __init__(self):
        super().__init__(all_sprites)
        self.images = [load_image('character.png'),
                       load_image('character2.png'),
                       load_image('character3.png'),
                       load_image('character2.png'),]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect[2] -= 5
        self.rect[3] -= 5
        self.rect.x = 0
        self.rect.y = 0
        self.killed = False
        self.hp = 100
        self.sprite_index = 0  # индекс кадра в анимации спрайта
        self.fps_index = 0  # интервал смены спрайтов

    def update(self):        # проверка на столкновения и выход за границы,
        self.fps_index += 1  # смена спрайта
        if self.fps_index >= 10:
            self.fps_index = 0
            self.sprite_index += 1
            try:
                self.image = self.images[self.sprite_index]
            except IndexError:
                self.sprite_index = 0
                self.image = self.images[self.sprite_index]        
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > width - 29:
            self.rect.x = width - 29
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > height - 36:
            self.rect.y = height - 36

        if pygame.sprite.spritecollideany(self, enemy_group):
            self.hp = 0
        elif pygame.sprite.spritecollideany(self, bullet_group):
            # self.hp -= 10
            self.hp = 0
        if self.hp <= 0:
            player.kill()

    def kill(self):  # замена "убийства" спрайта на конец игры
        all_sprites.remove(player)
        self.killed = True
        game_over()


class Enemy(pygame.sprite.Sprite):  # класс врагов
    def __init__(self, x, y, enemy_type):
        super().__init__(enemy_group, all_sprites)
        self.enemy_type = enemy_type
        self.extra = []
        if enemy_type == 'ghost':  # бродит в разные стороны
            self.images = [load_image('ghost1.png'), load_image('ghost2.png'),
                           load_image('ghost3.png'), load_image('ghost4.png')]
        elif enemy_type == 'ninja':  # стоит на месте, кидает сюрикен
                                    # и в это время совершает рывок к игроку
            self.images = [load_image('ninja1.png'), load_image('ninja2.png'),
                           load_image('ninja3.png'), load_image('ninja4.png')]
            self.extra = [load_image('ninja_e1.png'),
                          load_image('ninja_e2.png'),
                          load_image('ninja_e3.png'),
                          load_image('ninja_e4.png')]
        self.explode = [load_image('e_1.png'), load_image('e_2.png'),
                        load_image('e_3.png')]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 0
        self.sprite_index = 0  # индекс кадра в анимации спрайта
        self.fps_index = [0, 0, 0, 0]  # индексы для разных действий:
        # интервал смены спрайтов, счетчик кадров, интервал смены
        # экстра-спрайтов и метания сюрикенов

    def update(self):
        self.fps_index[0] += 1
        self.fps_index[1] += 1
        if self.fps_index[0] >= 10:
            self.fps_index[0] = 0
            self.sprite_index += 1
            try:
                self.image = self.images[self.sprite_index]
                if self.fps_index[2] and self.fps_index[2] != 4:
                    self.fps_index[2] += 1
            except IndexError:
                self.sprite_index = 0
                self.image = self.images[self.sprite_index]
        if self.fps_index[2] == 4:
            self.kill()
        if self.enemy_type == 'ghost':
            self.rect.y += 1
            if self.sprite_index == 0 and self.fps_index[0] == 0:
                self.direction = random.choice([-1, 1])
            self.rect.x += self.direction
        elif self.enemy_type == 'ninja':
            self.acting_like_a_ninja()

    def acting_like_a_ninja(self):  # отдельно вынесенное поведение ниндзи
        if self.fps_index[1] >= 600 and not self.fps_index[3]:
            self.images, self.extra = self.extra, self.images
            self.image = self.images[0]
            bullet = Bullet(self.rect.x, self.rect.y, player.rect.x,
                            player.rect.y, 'ninja')  # кидает сюрикен
            self.fps_index[2] += 1
            self.fps_index[3] = 1
        if self.rect.y < player.rect.y:
            self.rect.y += 1
        elif self.rect.y == player.rect.y:
            pass
        else:
            self.rect.y -= 1
        if self.rect.x < player.rect.x:
            self.rect.x += 1
        elif self.rect.x == player.rect.x:
            pass
        else:
            self.rect.x -= 1
        if self.rect.y == height or self.rect.x == (width or 0):
            self.kill()


class Bullet(pygame.sprite.Sprite):  # класс враждебных объектов
    def __init__(self, x, y, dest_x, dest_y, enemy_type):
        super().__init__(bullet_group, all_sprites)
        self.bullet_type = enemy_type
        if enemy_type == 'ninja':
            self.images = [load_image('shuriken1.png'),
                           load_image('shuriken2.png')]
            self.speed = [3, 3]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.destination = (dest_x, dest_y)  # координаты цели
        self.sprite_index, self.fps_index = 0, 0
        self.dir_x = random.choice([3, -3, 0])
        self.dir_y = random.choice([3, -3])

    def update(self):  # проверка направления и координат
        """
        angle = math.atan2(self.destination[0] - self.rect.x,
                           self.destination[1] - self.rect.y)
        self.fps_index += 1
        if self.fps_index >= 10:
            self.fps_index = 0
            self.sprite_index += 1
            try:
                self.image = self.images[self.sprite_index]
            except IndexError:
                self.sprite_index = 0
                self.image = self.images[self.sprite_index]
        self.rect.x += math.degrees(angle)
        self.rect.y += math.degrees(angle)
        """
        self.rect.x += self.dir_x
        self.rect.y += self.dir_y
        if self.rect.y == height or self.rect.x == (width or 0):
            self.kill()


def load_image(name, colorkey=None):  # загрузка изображения
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


def events():  # обработка событий из главного цикла
    global shift, speed
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


def game_over():  # анимация экрана конца игры
    # if hard_mode:
    #    color = (255, 0, 0)
    #    anticolor = (255, 255, 255)
    # else:
    color = (255, 255, 255)
    anticolor = (255, 0, 0)
    black_surface = pygame.Surface((width, height))
    black_surface.fill((0, 0, 0))
    black_surface.set_alpha(5)
    font = pygame.font.Font('data/font.ttf', 50)
    text = font.render("Игра окончена.", 1, (255, 255, 255))
    text_x, text_y = 50, 0  # 50, 170
    text_w = text.get_width()
    text_h = text.get_height()
    text2 = font.render("Ваш счет:", 1, (255, 255, 255))
    text2_x, text2_y = 70, 0  # 70, 240
    text2_w = text.get_width()
    text2_h = text.get_height()
    big_font = pygame.font.Font('data/font.ttf', 150)
    score_text = big_font.render(str(score), 1, color)
    score_text_x, score_text_y = 200, 0  # 200, 400
    score_text_w = text.get_width()
    score_text_h = text.get_height()
    clock = pygame.time.Clock()
    timer = 0
    while player.killed:
        timer += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        if text_y != 170:
            text_y += 1
        if text2_y != 240:
            text2_y += 1
        if score_text_y != 400:
            score_text_y += 1
        circleRect = pygame.draw.circle(screen, anticolor,
                                        (300, 400), 1 + timer, 1)
        screen.blit(black_surface, (0, 0))
        screen.blit(text, (text_x, text_y))
        screen.blit(text2, (text2_x, text2_y))
        screen.blit(score_text, (score_text_x, score_text_y))
        pygame.display.flip()
        clock.tick(100)
        if timer == 1000:
            break
    initialize()
    # while
    # здесь я доделаю возвращение к меню


def initialize():  # создание переменных вынесено в отдельную функцию для того,
    # чтобы можно было легко начать новую игру после проигрыша
    global all_sprites, enemy_group, bullet_group, background, player, speed
    global clock, shift, spawn_flag, max_spawn
    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    background = Background('bg.png')
    player = Player()
    player.rect = player.image.get_rect()
    player.rect.x = width // 2
    player.rect.y = (height // 4) * 3
    speed = 1
    clock = pygame.time.Clock()
    shift = False
    spawn_flag = True
    # if hard_mode:
    #     max_spawn = 100
    # else:
    max_spawn = 200
    game_main_cycle()


def game_main_cycle():  # выношу цикл в отдельную функцию по причине,
                        # указанной выше
    global score, max_spawn
    score = 0
    spawn_timer = 0
    background.rect.y = -3200
    while not player.killed:  # игровой цикл
        events()
        max_spawn -= 0.1
        spawn_timer += 1
        screen.blit(background.image, (background.rect.x, background.rect.y))
        if -32 <= background.rect.y:
            background.rect.y = -3232
        background.rect.y += 1
        all_sprites.draw(screen)
        all_sprites.update()
        if spawn_timer == 50:
            score += 100
        elif spawn_timer >= max_spawn and spawn_flag:
            enemy = Enemy(random.randint(0, width), -40,
                          random.choice(['ghost', 'ninja']))
            spawn_timer = 0
        clock.tick(fps)
        pygame.display.flip()
    game_over()

"""
def menu():  # главное меню
    global hard_mode
    hard_mode = False
    menu_images = [load_image('menu1.png'), load_image('menu2.png'),
                   load_image('menu3.png'), load_image('menu4.png')]
    menu_image = Background(menu_images[0])

"""

# инициализация и ввод основных переменных
pygame.init()
size = width, height = 500, 800
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
fps = 60

# menu()
initialize()
game_main_cycle()
