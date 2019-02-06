import os
import random
import sys
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
        super().__init__(all_sprites, player_group)
        self.images = [load_image('character.png'),
                       load_image('character2.png'),
                       load_image('character3.png'),
                       load_image('character2.png')]
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
            self.death_sound = pygame.mixer.Sound('data/ghost.wav')
            self.explode = [load_image('minus_ghost.png'),
                            load_image('minus_ghost2.png'),
                            load_image('minus_ghost3.png')]
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
            self.death_sound = pygame.mixer.Sound('data/ghost.wav')
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 0
        self.sprite_index = 0  # индекс кадра в анимации спрайта
        self.fps_index = [0, 0, 0, 0, 0]  # индексы для разных действий:
        # интервал смены спрайтов, счетчик кадров, интервал смены
        # особых спрайтов, метания сюрикенов и взрывов
        self.random_attack = random.randint(10, 700)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_bullet_group):
            self.images, self.explode = self.explode, self.images
            self.death_sound.play()
            self.image = self.images[0]
            self.sprite_index = 0
            self.fps_index[4] = 1
        if self.fps_index[4]:
            if self.fps_index[4] == 4:
                self.kill()
            self.fps_index[4] += 1
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
        if self.fps_index[1] >= self.random_attack and not self.fps_index[3]:
            self.images, self.extra = self.extra, self.images
            self.image = self.images[0]
            bullet = Bullet(self.rect.x, self.rect.y, (player.rect.x,
                            player.rect.y), 'ninja')  # кидает сюрикен
            pygame.mixer.Sound('data/attack.wav').play()
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
    def __init__(self, x, y, dest, enemy_type):
        super().__init__(bullet_group, all_sprites)
        self.bullet_type = enemy_type
        if enemy_type == 'ninja':
            self.images = [load_image('shuriken1.png'),
                           load_image('shuriken2.png')]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dest_x, self.dest_y = dest[0], dest[1]  # координаты цели
        self.sprite_index, self.fps_index = 0, 0
        self.distance = math.sqrt((self.dest_x - self.rect.x) ** 2 +
                                  (self.dest_y - self.rect.y) ** 2)
        self.timer = 500

    def update(self):  # проверка направления и координат
        if not self.timer:
            self.kill()
        self.fps_index += 1
        if self.fps_index >= 10:
            self.fps_index = 0
            self.sprite_index += 1
            try:
                self.image = self.images[self.sprite_index]
            except IndexError:
                self.sprite_index = 0
                self.image = self.images[self.sprite_index]
        k = 7 / self.distance
        self.rect.x = self.rect.x + (self.dest_x - self.rect.x) * k
        self.rect.y = self.rect.y + (self.dest_y - self.rect.y) * k
        if self.rect.y == height or self.rect.x == (width or 0) or k < 0.01:
            self.kill()
        self.timer -= 1


class PlayerBullet(pygame.sprite.Sprite):  # класс пуль игрока
    def __init__(self, dir_x, dir_y):
        pygame.mixer.Sound('data/attack.wav').play()
        super().__init__(player_bullet_group, all_sprites)
        self.image = load_image('player_bullet.png')
        self.dir_x, self.dir_y = dir_x, dir_y
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x + 7
        self.rect.y = player.rect.y

    def update(self):
        global score
        if pygame.sprite.spritecollideany(self, enemy_group):
            pygame.mixer.Sound('data/attack.wav').play()
            score += 1
            self.kill()
        if pygame.sprite.spritecollideany(self, bullet_group):
            pygame.mixer.Sound('data/collision.wav').play()
            pygame.sprite.spritecollideany(self, bullet_group).kill()
            self.kill()
        self.rect.x += self.dir_x
        self.rect.y += self.dir_y


class ScoreBox(pygame.sprite.Sprite):  # экземпляры этого класса дают игроку
                                    # +10 очков при столкновении с ними
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image('score_stuff.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(19, 479)
        self.rect.y = 0

    def update(self):
        global score
        if pygame.sprite.spritecollideany(self, player_group):
            pygame.mixer.Sound('data/got.wav').play()
            score += 1
            self.kill()
        self.rect.y += 1


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
    global shift, speed, shooting
    keys = pygame.key.get_pressed()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            terminate()
        elif e.type == pygame.KEYDOWN:
            if e.mod in [pygame.KMOD_LSHIFT, pygame.KMOD_RSHIFT]:
                if not shift:
                    speed *= 2
                shift = True
            elif shift:
                speed //= 2
                shift = False
            elif e.key == pygame.K_SPACE:
                global score
                dir_x, dir_y = 0, -5
                if score * 10 >= 3:
                    player_bullet = PlayerBullet(dir_x, dir_y)
                    score -= 0.3
            elif e.key == pygame.K_t:
                pause()
    if keys[pygame.K_UP]:
        player.rect.y -= speed
    if keys[pygame.K_DOWN]:
        player.rect.y += speed
    if keys[pygame.K_LEFT]:
        player.rect.x -= speed
    if keys[pygame.K_RIGHT]:
        player.rect.x += speed


def pause():  # пауза
    pause = True
    for e in pygame.event.get():
        if e.key == pygame.K_t and pause:
            pause = False
            game_main_cycle()
        text1 = font.render("Нажмите t для", 1, (255, 255, 255))
        text2 = font.render("продолжения игры", 1, (255, 255, 255))
        screen.blit(text1, (100, 300))
        screen.blit(text2, (80, 500))


def game_over():  # анимация экрана конца игры
    global score
    score = str(int(score * 10))
    save_score()
    color = (255, 255, 255)
    anticolor = (255, 0, 0)
    black_surface = pygame.Surface((width, height))
    black_surface.fill((0, 0, 0))
    black_surface.set_alpha(5)
    font = pygame.font.Font('data/font.ttf', 50)
    text = font.render("Игра окончена.", 1, (255, 255, 255))
    text_x, text_y = 50, 0  # 50, 170
    text2 = font.render("Ваш счет:", 1, (255, 255, 255))
    text2_x, text2_y = 70, 0  # 70, 240
    big_font = pygame.font.Font('data/font.ttf', 150)
    score_text = big_font.render(str(int(score)), 1, color)
    score_text_x, score_text_y = 150, 0  # 150, 400
    max_score_text = font.render(
        'Макс. очки: ' + str(int(max_score)), 1, color)
    max_score_text_x, max_score_text_y = 100, 900  # 100, 700
    clock = pygame.time.Clock()
    button1_text = font.render("Заново", 1, (255, 255, 255))
    button2_text = font.render("В меню", 1, (255, 255, 255))
    timer = 0
    current = COLOR
    while player.killed:
        timer += 1
        circle = pygame.draw.circle(screen, anticolor,
                                    (300, 400), 1 + timer, 1)
        screen.blit(black_surface, (0, 0))
        screen.blit(text, (text_x, text_y))
        screen.blit(text2, (text2_x, text2_y))
        screen.blit(score_text, (score_text_x, score_text_y))
        screen.blit(max_score_text, (max_score_text_x, max_score_text_y))
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if text_y != 100:
            text_y += 2
        if text2_y != 170:
            text2_y += 2
        if score_text_y != 300:
            score_text_y += 2
        if max_score_text_y != 500:
            max_score_text_y -= 2
        if 245 > mouse[0] > 20 and 765 > mouse[1] > 700:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                initialize()
                game_main_cycle()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 700, 225, 65))
        pygame.draw.rect(screen, current, (22, 702, 221, 61))
        screen.blit(button1_text, (50, 710))
        if 475 > mouse[0] > 250 and 765 > mouse[1] > 700:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                menu()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (250, 700, 225, 65))
        pygame.draw.rect(screen, current, (252, 702, 221, 61))
        screen.blit(button2_text, (270, 710))
        pygame.display.flip()
        clock.tick(100)
    menu()


def initialize():  # создание переменных вынесено в отдельную функцию для того,
    # чтобы можно было легко начать новую игру после проигрыша
    global all_sprites, enemy_group, bullet_group, background, player, speed
    global clock, shift, spawn_flag, max_spawn, level, player_bullet_group
    global score, player_group
    all_sprites = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player_bullet_group = pygame.sprite.Group()
    player = Player()
    player.rect = player.image.get_rect()
    player.rect.x = width // 2
    player.rect.y = (height // 4) * 3
    speed = 2
    shooting = False
    score = 0
    clock = pygame.time.Clock()
    shift = False
    spawn_flag = True


def game_main_cycle():  # выношу цикл в отдельную функцию по причине,
                        # указанной выше
    global score
    max_spawn = 200
    spawn_timer = 0
    if level == 1:
        e_type = ['ghost']
        background = Background('bg.png')
        pygame.mixer.music.load('data/level_music.mp3')
        pygame.mixer.music.play(-1)
        minus_spawn = 0
        time_left = 50
        speed = 1
    elif level == 2:
        e_type = ['ghost', 'ninja']
        background = Background('bg2.png')
        pygame.mixer.music.load('data/level2_music.mp3')
        pygame.mixer.music.play(-1)
        minus_spawn = 0.01
        time_left = 100
        speed = 2
    elif level == 3:
        e_type = ['ghost', 'ninja']
        background = Background('bg3.png')
        pygame.mixer.music.load('data/level3_music.mp3')
        pygame.mixer.music.play(-1)
        minus_spawn = 0.03
        time_left = 500
        speed = 3
    font = pygame.font.Font('data/font.ttf', 25)
    background.rect.y = -3200
    while not player.killed:  # игровой цикл
        text = font.render('Очки: ' + str(int(score * 10)), 1, (255, 255, 255))
        text2 = font.render('Осталось: ' + str(int(time_left)),
                            1, (255, 255, 255))
        events()
        if int(time_left) == 0:
            pygame.mixer.music.stop()
            victory()
        time_left -= 0.01
        max_spawn -= minus_spawn
        spawn_timer += 1
        screen.blit(background.image, (background.rect.x, background.rect.y))
        if 0 <= background.rect.y:
            background.rect.y = -3200
        background.rect.y += speed
        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(text, (10, 5))
        screen.blit(text2, (300, 5))
        score += 0.001
        if spawn_timer >= max_spawn and spawn_flag:
            spawn_box = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 1])
            if spawn_box:
                ScoreBox()
            enemy = Enemy(random.randint(0, width), -40, random.choice(e_type))
            spawn_timer = 0
        clock.tick(fps)
        pygame.display.flip()
    pygame.mixer.music.stop()


def victory():  # экран победы
    global score, level
    pygame.mixer.Sound('data/victory.ogg').play()
    score = str(int(score * 10))
    save_score()
    black_surface = pygame.Surface((width, height))
    black_surface.fill((0, 0, 0))
    black_surface.set_alpha(5)
    text = font.render("Вам удалось", 1, (255, 255, 255))
    text_x, text_y = 40, 0
    text1 = font.render("пройти уровень!", 1, (255, 255, 255))
    text1_x, text1_y = 60, 0
    text2 = font.render("Ваш счет:", 1, (255, 255, 255))
    text2_x, text2_y = 70, 0  # 70, 240
    big_font = pygame.font.Font('data/font.ttf', 150)
    score_text = big_font.render(str(int(score)), 1, (255, 255, 255))
    score_text_x, score_text_y = 150, 0  # 150, 400
    max_score_text = font.render(
        'Макс. очки: ' + str(int(max_score)), 1, (255, 255, 255))
    max_score_text_x, max_score_text_y = 100, 900  # 100, 700
    clock = pygame.time.Clock()
    if level != 3:
        button1_text = font.render("След. ур.", 1, (255, 255, 255))
        level += 1
    else:
        button1_text = font.render("Уровень 1", 1, (255, 255, 255))
        level = 1
    button2_text = font.render("В меню", 1, (255, 255, 255))
    timer = 0
    current = COLOR
    while player:
        timer += 1
        circle = pygame.draw.circle(screen, (0, 0, 255),
                                    (300, 400), 1 + timer, 1)
        screen.blit(black_surface, (0, 0))
        screen.blit(text, (text_x, text_y))
        screen.blit(text1, (text1_x, text1_y))
        screen.blit(text2, (text2_x, text2_y))
        screen.blit(score_text, (score_text_x, score_text_y))
        screen.blit(max_score_text, (max_score_text_x, max_score_text_y))
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if text_y != 60:
            text_y += 2
        if text1_y != 100:
            text1_y += 2
        if text2_y != 170:
            text2_y += 2
        if score_text_y != 300:
            score_text_y += 2
        if max_score_text_y != 500:
            max_score_text_y -= 2
        if 245 > mouse[0] > 20 and 765 > mouse[1] > 700:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                initialize()
                game_main_cycle()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 700, 225, 65))
        pygame.draw.rect(screen, current, (22, 702, 221, 61))
        screen.blit(button1_text, (30, 710))
        if 475 > mouse[0] > 250 and 765 > mouse[1] > 700:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                menu()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (250, 700, 225, 65))
        pygame.draw.rect(screen, current, (252, 702, 221, 61))
        screen.blit(button2_text, (270, 710))
        pygame.display.flip()
        clock.tick(100)


def menu():  # главное меню
    menu_image = load_image('menu1.png')
    pygame.mixer.music.load('data/level2_music.mp3')
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    button1_text = font.render("Начать игру", 1, (255, 255, 255))
    button2_text = font.render("Таблица рекордов", 1, (255, 255, 255))
    button3_text = font.render("Выйти из игры", 1, (255, 255, 255))
    current = COLOR
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if pygame.mouse.get_pressed()[0] == 1 and exit_pos:
                terminate()
        screen.blit(menu_image, (0, 0))
        mouse = pygame.mouse.get_pos()
        if 480 > mouse[0] > 20 and 620 > mouse[1] > 555:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                pygame.time.wait(1)
                choose_level()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 555, 460, 65))
        pygame.draw.rect(screen, current, (22, 557, 456, 61))
        screen.blit(button1_text, (100, 565))
        if 480 > mouse[0] > 20 and 690 > mouse[1] > 625:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                save_score()
                score_screen()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 625, 460, 65))
        pygame.draw.rect(screen, current, (22, 627, 456, 61))
        screen.blit(button2_text, (25, 635))
        if 480 > mouse[0] > 20 and 760 > mouse[1] > 695:
            exit_pos = True
            current = HOVER_COLOR
        else:
            exit_pos = False
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 695, 460, 65))
        pygame.draw.rect(screen, current, (22, 697, 456, 61))
        screen.blit(button3_text, (80, 705))
        pygame.display.flip()


def choose_level():  # выбор уровня
    global level
    initialize()
    image = load_image('gradient.png')
    button1_text = font.render("Уровень 1", 1, (255, 255, 255))
    button2_text = font.render("Уровень 2", 1, (255, 255, 255))
    button3_text = font.render("Уровень 3", 1, (255, 255, 255))
    button4_text = font.render("Выйти в меню", 1, (255, 255, 255))
    current = COLOR
    while 1:
        screen.blit(image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        mouse = pygame.mouse.get_pos()
        if 480 > mouse[0] > 20 and 120 > mouse[1] > 55:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                level = 1
                game_main_cycle()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 55, 460, 65))
        pygame.draw.rect(screen, current, (22, 57, 456, 61))
        screen.blit(button1_text, (150, 65))
        if 480 > mouse[0] > 20 and 190 > mouse[1] > 125:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                level = 2
                game_main_cycle()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 125, 460, 65))
        pygame.draw.rect(screen, current, (22, 127, 456, 61))
        screen.blit(button2_text, (150, 135))
        if 480 > mouse[0] > 20 and 260 > mouse[1] > 195:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                level = 3
                game_main_cycle()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 195, 460, 65))
        pygame.draw.rect(screen, current, (22, 197, 456, 61))
        screen.blit(button3_text, (150, 205))
        if 480 > mouse[0] > 20 and 365 > mouse[1] > 300:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                menu()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 300, 460, 65))
        pygame.draw.rect(screen, current, (22, 302, 456, 61))
        screen.blit(button4_text, (80, 310))
        pygame.display.flip()


def save_score():  # сохранение и сортировка очков в порядке убывания
    global max_score, record_list
    with open('data/records.txt', 'a') as rec:
        rec.write('\n' + str(score))
    with open('data/records.txt', 'r') as rec:
        record_list = rec.read().split()
    record_list = list(map(int, record_list))
    record_list.sort(reverse=True)
    if len(record_list) > 5:
        record_list = record_list[:5]
    with open('data/records.txt', 'w') as rec:
        for i in record_list:
            rec.write(str(i) + '\n')
    max_score = max(record_list)


def terminate():  # выход из игры
    pygame.quit()
    sys.exit()


def score_screen():  # таблица рекордов
    records = record_list
    font = pygame.font.Font('data/font.ttf', 60)
    bg = Background('record_table.png')
    x, y = 90, 140
    clock = pygame.time.Clock()
    button_text = font.render("Выйти в меню", 1, (255, 255, 255))
    while 1:
        y = 140
        mouse = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                terminate()
        screen.blit(bg.image, (bg.rect.x, bg.rect.y))
        if 480 > mouse[0] > 20 and 735 > mouse[1] > 670:
            current = HOVER_COLOR
            if pygame.mouse.get_pressed()[0] == 1:
                menu()
        else:
            current = COLOR
        pygame.draw.rect(screen, (255, 255, 255), (20, 670, 460, 65))
        pygame.draw.rect(screen, current, (22, 672, 456, 61))
        screen.blit(button_text, (50, 680))
        for i in records:
            text = font.render(str(i), 1, (255, 255, 255))
            screen.blit(text, (x, y))
            y += 100
        pygame.display.flip()

# инициализация и ввод основных переменных
pygame.init()
size = width, height = 500, 800
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))
fps = 60
font = pygame.font.Font('data/font.ttf', 50)
COLOR, HOVER_COLOR = (170, 50, 50), (190, 60, 60)
current = COLOR

initialize()
menu()
game_main_cycle()
