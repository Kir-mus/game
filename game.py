import os
import pygame
import sys
from f import print_text
from parameters import screen
import time
from parameters import screen_2
from inventory import inventory
from time import sleep
import random

pygame.init()

saze = WIDTH, HEIGHT = 1200, 700

clock = pygame.time.Clock()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
box_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bullet_group_mob = pygame.sprite.Group()
mob_group = pygame.sprite.Group()
hellca_group = pygame.sprite.Group()
cooldown = 0
mob_cord = []


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(message)
    if color_key != None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
        image.set_alpha(50)
    else:
        image = image.convert_alpha()
    return image, name[:-4]


def load_level(f):
    if len(f) - 4 != '.txt':
        filename = "data/" + f + ".txt"
    elif len(f) - 4 == '.txt':
        filename = "data/" + f
    # читаем уровень, убирая символы перевода строки
    try:
        with open(filename.lower(), 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
    except FileNotFoundError as message:
        print('Не могу загрузить txt: ', f)
        raise SystemExit(message)
    # и подсчитываем максимальную длин
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'wall': load_image('sten.png')[0], 'empty': load_image('pol.png')[0], 'grass': load_image('grass.png')[0]}
player_image1 = load_image('mar.png')[0]
x = None
y = None
xy = []
sp_mob = []


def generate_level(level):
    global x, y, xy, sp_mob
    new_player, new_mob, new_hellca, x, y = None, None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '^':
                Tile('grass', x, y)
            elif level[y][x] == '+':
                Tile('empty', x, y)
                new_hellca = Hellca(load_image("hellca_2.png", -1)[0], 1, 1, x * 50, y * 50)
            elif level[y][x] == '!':
                Tile('empty', x, y)
                sp_mob.append(Mob(load_image("hero_proz.png", -1)[0], 2, 1, x * 50, y * 50, 2, 2, new_player))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(load_image("hero_proz.png", -1)[0], 2, 1, x * 50, y * 50)

    # вернем игрока, а также размер поля в клетках

    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'wall':
            self.add(box_group, tiles_group, all_sprites)
        else:
            self.add(tiles_group, all_sprites)


class Weapon(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, playre):
        super().__init__(weapon_group, all_sprites)
        self.live = True
        self.columns = columns
        self.shooting = False
        self.rows = rows
        self.sheet = sheet[0]
        self.weapon_name = sheet[1]
        self.w = 35
        self.h = 35
        self.playre = playre
        self.frames = []
        self.left = False
        self.cut_sheet(self.sheet, self.columns, self.rows)
        self.cur_frame = 0
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(self.playre.rect.x + 25, self.playre.rect.y + 25, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())
        self.trans = False

    def setSprite(self, sprite, columns, rows):
        self.sheet = sprite[0]
        self.weapon_name = sprite[1]
        self.shooting = False
        self.playre.block = False
        if self.weapon_name == 'shell':
            self.w = 25
            self.h = 40
        if self.weapon_name == 'sword':
            self.w = 35
            self.h = 40
        if self.weapon_name == 'bow':
            self.w = 35
            self.h = 35

        self.columns = columns
        self.rows = rows
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)

    def cut_sheet(self, sheet, columns, rows):
        self.test_rect = pygame.Rect(0, 0, self.sheet.get_width() // self.columns,
                                     self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.columns):
                frame_location = (self.test_rect.w * i, self.test_rect.h * j)
                self.frames.append(pygame.transform.scale(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.test_rect.size)), (self.w, self.h)))

    def update(self):
        if self.weapon_name == 'bow':
            self.shooting = True
        else:
            self.shooting = False
        if self.weapon_name == 'shell':
            self.playre.block = True
        else:
            self.playre.block = False
        if self.playre.heath <= 0:
            self.live = False

        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        if not self.left:
            if self.weapon_name != 'shell':
                self.rect = pygame.Rect(self.playre.rect.x + 25, self.playre.rect.y,
                                            self.frames[self.cur_frame].get_width(),
                                            self.frames[self.cur_frame].get_height())
            else:
                self.rect = pygame.Rect(self.playre.rect.x + 25, self.playre.rect.y + 6,
                                            self.frames[self.cur_frame].get_width(),
                                            self.frames[self.cur_frame].get_height())
        else:
            if self.weapon_name != 'shell':
                self.rect = pygame.Rect(self.playre.rect.x - 25, self.playre.rect.y,
                                            self.frames[self.cur_frame].get_width(),
                                            self.frames[self.cur_frame].get_height())
            else:
                self.rect = pygame.Rect(self.playre.rect.x - 15, self.playre.rect.y,
                                            self.frames[self.cur_frame].get_width(),
                                            self.frames[self.cur_frame].get_height())

        if self.trans:
            self.sheet = pygame.transform.flip(self.sheet, 1, 0)
            self.frames = []
            self.cut_sheet(self.sheet, self.columns, self.rows)
            self.trans = False


class Hellca(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(hellca_group, all_sprites)
        self.rows = rows
        self.sheet = sheet
        self.columns = columns
        self.x = x
        self.y = y
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)
        self.cur_frame = 0
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(self.x + 15, self.y + 15, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())

    def cut_sheet(self, sheet, columns, rows):
        self.test_rect = pygame.Rect(0, 0,  self.sheet.get_width() // self.columns,
                                     self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.columns):
                frame_location = (self.test_rect.w * i, self.test_rect.h * j)
                self.frames.append(pygame.transform.scale(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.test_rect.size)), (25, 25)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.heath = 100
        self.stamin = 100
        self.shooting = False
        self.block = False
        self.rows = rows
        self.sheet = sheet
        self.columns = columns
        self.x = x
        self.y = y
        self.all_bullets = []
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)
        self.cur_frame = 0
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())

    def setSprite(self, sprite, columns, rows):
        self.sheet = sprite
        self.columns = columns
        self.rows = rows
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)

    def cut_sheet(self, sheet, columns, rows):
        self.test_rect = pygame.Rect(0, 0,  self.sheet.get_width() // self.columns,
                                     self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.columns):
                frame_location = (self.test_rect.w * i, self.test_rect.h * j)
                self.frames.append(pygame.transform.scale(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.test_rect.size)), (35, 45)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        pygame.draw.rect(screen, (75, 3, 1), (5, 5, 100 * 4, 30))
        pygame.draw.rect(screen, (200, 23, 1), (5, 5, 100 * 4, 30), 3)
        if self.heath <= 0:
            pygame.draw.rect(screen, (5, 0, 0), (5, 5, 100 * 4, 30))
            pygame.draw.rect(screen, (20, 3, 1), (5, 5, 100 * 4, 30), 3)
        pygame.draw.rect(screen, (110, 110, 23), (5, 40, 100 * 4, 30), 3)
        if self.heath > 100:
            self.heath = 100
        if self.stamin > 100:
            self.stamin = 100
        if self.stamin < 0:
            self.stamin = 0

        if self.heath >= 0:
            pygame.draw.rect(screen, (144, 23, 1), (5, 7, self.heath * 4, 30 - 4))
        else:
            pygame.draw.rect(screen, (144, 144, 23), (5, 40, 0, 30))
        print_text('HP', 5, 5)
        if self.stamin >= 0:
            pygame.draw.rect(screen, (20, 20, 3), (5, 40, 100 * 4, 30))
            pygame.draw.rect(screen, (144, 144, 23), (5, 42, self.stamin * 4, 30 - 4))
        else:
            pygame.draw.rect(screen, (20, 20, 3), (5, 40, 100 * 4, 30))
            pygame.draw.rect(screen, (144, 144, 23), (5, 40, 0, 30))

        print_text('STAMIN', 5, 40)

    def shoot(self, weapon, zel, y):
        if weapon.shooting:
            new_bullet = Bullet(bullet_img, 1, 1, weapon)
            new_bullet.find_path(zel, y)
            self.all_bullets.append(new_bullet)

            for bullet in self.all_bullets:
                if not bullet.move_to(zel, reverse=True):
                    self.all_bullets.remove(bullet)


def chek_mob_dmg(bullets, mob):
    for mob in mob:
        for bullet in bullets:
            mob.chek_dmg(bullet)


class Mob(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, move_x, move_y, zel):
        super().__init__(mob_group, all_sprites)
        self.sledovat = False
        self.patrulirovat = False
        self.move_x = move_x
        self.move_y = move_y
        self.heath = 100
        self.zel = zel
        self.tick = 100 * 100 ** 2
        self.terr_x = 4 * 50
        self.terr_y = 4 * 50
        self.columns = columns
        self.rows = rows
        self.sheet = sheet
        self.f = False
        self.live = True
        self.speed_x = 0
        self.speed_y = 0
        self.x = x
        self.x_w = 1
        self.y = y
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)
        self.cur_frame = 0
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())
        self.post_rect = self.rect
        self.cooldown_s = 0
        self.all_bullets = []
        self.width = 50
        self.heght = 50

    def update(self):

        if self.live:
            if self.zel.rect.x + 280 > self.rect.x and\
                        self.zel.rect.x - 280 < self.rect.x and\
                        self.zel.rect.y + 280 > self.rect.y and self.zel.rect.y - 280 < self.rect.y:
                self.sledovat = True
            else:
                self.sledovat = False
            if self.sledovat:
                if self.f:
                    if self.zel.rect.x - 80 < self.rect.x and self.zel.rect.x + 280 > self.rect.x and\
                            self.zel.rect.x - 280 < self.rect.x and\
                            self.zel.rect.y + 280 > self.rect.y and self.zel.rect.y - 280 < self.rect.y:
                        self.speed_x = -2

                    if self.zel.rect.x - 80 > self.rect.x and self.zel.rect.x + 280 > self.rect.x and\
                            self.zel.rect.x - 280 < self.rect.x and\
                            self.zel.rect.y + 280 > self.rect.y and self.zel.rect.y - 280 < self.rect.y:
                        self.speed_x = 2

                    if self.zel.rect.y > self.rect.y and self.zel.rect.x + 280 > self.rect.x and\
                            self.zel.rect.x - 280 < self.rect.x and\
                            self.zel.rect.y + 280 > self.rect.y and self.zel.rect.y - 280 < self.rect.y:
                        self.speed_y = 2

                    if self.zel.rect.y < self.rect.y and self.zel.rect.x + 280 > self.rect.x and\
                            self.zel.rect.x - 280 < self.rect.x and\
                            self.zel.rect.y + 280 > self.rect.y and self.zel.rect.y - 280 < self.rect.y:
                        self.speed_y = -2


                    self.move_to(self.speed_x, self.speed_y)
                    self.f = False
                elif self.speed_x == -2 and not self.f:
                    self.move_to(1, 1)
                elif self.speed_x == 2 and not self.f:
                    self.move_to(0, 1)
                elif self.speed_y == 2 and not self.f:
                    self.move_to(0, -1)
                elif self.speed_y == -2 and not self.f:
                    self.move_to(0, 1)
            else:
                self.rect = self.post_rect


        else:
            print_text('dead', self.rect.x - 10, self.rect.y - 35, (255, 0, 0))
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.heath > 0:
            pygame.draw.rect(screen, (144, 23, 1), (self.rect.x - 10, self.rect.y - 5, self.heath // 2, 5))

        pygame.draw.rect(screen, (144, 23, 1), (self.rect.x - 10, self.rect.y - 5, 50, 5), 1)

        if self.heath <= 0:
            self.setSprite(load_image('kill.png', -1)[0], 1, 1)
            self.live = False

    def move_to(self, speed_x, speed_y):
        self.rect.move_ip(speed_x, speed_y)


    def setSprite(self, sprite, columns, rows):
        self.sheet = sprite
        self.columns = columns
        self.rows = rows
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)

    def cut_sheet(self, sheet, columns, rows):
        self.test_rect = pygame.Rect(5, 5,  self.sheet.get_width() // self.columns,
                                     self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.columns):
                frame_location = (self.test_rect.w * i, self.test_rect.h * j)
                self.frames.append(pygame.transform.scale(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.test_rect.size)), (35, 35)))

    def chek_dmg(self, bullet):
        if self.x <= bullet.x <= self.x + self.width:
            if self.y <= bullet.y <= self.y + self.heght:
                self.kil = True

    def shoot(self, weapon, zel):
        if self.live:
            if not self.cooldown_s:
                new_bullet = Bulletmob(bullet_img, 1, 1, weapon, zel)
                new_bullet.find_path(zel.rect.centerx, zel.rect.centery)
                self.all_bullets.append(new_bullet)
                self.cooldown_s = 10 * len(mob_group)
            else:
                self.cooldown_s -= 1
            for bullet in self.all_bullets:
                if not bullet.move_to(reverse=True):
                    self.all_bullets.remove(bullet)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, sizze):
        self.dx = 0
        self.dy = 0
        self.sizze = sizze

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Button:
    def __init__(self, width, height, invitev_color=(31, 1, 1), active_color=(71, 1, 1), click_color=(200, 50, 1)):
        self.width = width
        self.height = height
        self.invitev_color = invitev_color
        self.active_color = active_color
        self.click_color = click_color

    def draw(self, x, y, mes, f=None, font_saze=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(screen, self.active_color, (x, y, self.width, self.height))
            if click[0] == 1:
                pygame.draw.rect(screen, self.click_color, (x, y, self.width, self.height))
                if f is not None:
                    f()
        else:
            pygame.draw.rect(screen, self.invitev_color, (x, y, self.width, self.height))
        print_text(mes, x, y, (0, 0, 0), font_saze)


bullet_img = load_image('strela.png', -1)[0]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, weapon):
        super().__init__(bullet_group, all_sprites)
        self.sheet = sheet
        self.columns = columns
        self.rows = rows
        self.x_wea = weapon.rect.x
        self.y_wea = weapon.rect.y
        self.x = weapon.rect.x
        self.y = weapon.rect.y + 13
        self.speed_x = 10
        self.speed_y = 0
        self.dest_x = 0
        self.f = False
        self.dest_y = 0
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)
        self.cur_frame = 0
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())

    def cut_sheet(self, sheet, columns, rows):
        self.test_rect = pygame.Rect(0, 0,  self.sheet.get_width() // self.columns,
                                     self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.columns):
                frame_location = (self.test_rect.w * i, self.test_rect.h * j)
                self.frames.append(pygame.transform.scale(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.test_rect.size)), (45, 15)))

    def move(self):
        self.x += self.speed_x
        if self.x <= WIDTH:
            print(self.x, self.y)
            self.rect = self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())
            return True
        else:
            return False

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.move_to(self.dest_x)

    def find_path(self, dest_x, dest_y):
        self.dest_x = dest_x
        self.dest_y = dest_y
        delta_x = self.dest_x - self.x
        count_up = delta_x // self.speed_x

        if count_up != 0:
            if self.y >= self.dest_y:
                delta_y = self.y - self.dest_y
                self.speed_y = delta_y / count_up
            elif not self.y >= self.dest_y:
                delta_y = self.dest_y - self.y
                self.speed_y = -(delta_y / count_up)

    def move_to(self, x, reverse=True):
        if x < self.x_wea:
            reverse = True
        if x > self.x_wea:
            reverse = False
        if not reverse:
            self.x += self.speed_x
            self.y -= self.speed_y
        else:
            self.x -= self.speed_x
            self.y += self.speed_y
        if self.x <= WIDTH and not reverse:
            self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                    self.frames[self.cur_frame].get_height())

            self.f = True
        elif self.x >= 0 and reverse:
            self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                    self.frames[self.cur_frame].get_height())
            self.f = True
        else:
            self.f = False


class Bulletmob(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, weapon, zel):
        super().__init__(bullet_group_mob, all_sprites)
        self.zel = zel
        self.sheet = sheet
        self.columns = columns
        self.rows = rows
        self.weapon = weapon
        self.x_wea = weapon.rect.x
        self.y_wea = weapon.rect.y
        self.x = weapon.rect.x
        self.y = weapon.rect.y + 13
        self.speed_x = 10
        self.speed_y = 0
        self.dest_x = 0
        self.f = False
        self.dest_y = 0
        self.frames = []
        self.cut_sheet(self.sheet, self.columns, self.rows)
        self.cur_frame = 0
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())

    def cut_sheet(self, sheet, columns, rows):
        self.test_rect = pygame.Rect(0, 0,  self.sheet.get_width() // self.columns,
                                     self.sheet.get_height() // self.rows)
        for j in range(self.rows):
            for i in range(self.columns):
                frame_location = (self.test_rect.w * i, self.test_rect.h * j)
                self.frames.append(pygame.transform.scale(self.sheet.subsurface(pygame.Rect(
                    frame_location, self.test_rect.size)), (45, 15)))

    def move(self):
        self.x += self.speed_x
        if self.x <= WIDTH:
            print(self.x, self.y)
            self.rect = self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                self.frames[self.cur_frame].get_height())
            return True
        else:
            return False

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.move_to()

    def find_path(self, dest_x, dest_y):
        self.dest_x = dest_x
        self.dest_y = dest_y

        delta_x = dest_x - self.x
        count_up = delta_x // self.speed_x

        if count_up != 0:
            if self.y >= dest_y:
                delta_y = self.y - dest_y
                self.speed_y = delta_y / count_up
            elif not self.y >= dest_y:
                delta_y = dest_y - self.y
                self.speed_y = -(delta_y / count_up)

    def move_to(self, reverse=True):
        if self.zel.rect.x < self.x_wea:
            reverse = True
        if self.zel.rect.x > self.x_wea:
            reverse = False
        if not reverse:
            self.x += self.speed_x
            self.y -= self.speed_y
        else:
            self.x -= self.speed_x
            self.y += self.speed_y
        if self.x <= WIDTH and not reverse and not self.x >= self.weapon.rect.x + 200 and\
                (self.y - 200 <= self.weapon.rect.y or self.y + 200 <= self.weapon.rect.y):
            print('not_reverse')
            self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                    self.frames[self.cur_frame].get_height())

            self.f = True
        elif self.x >= 0 and reverse and self.x >= self.weapon.rect.x - 200 and\
                (self.y - 200 <= self.weapon.rect.y or self.y + 200 <= self.weapon.rect.y):
            print('reverse')
            self.rect = pygame.Rect(self.x, self.y, self.frames[self.cur_frame].get_width(),
                                    self.frames[self.cur_frame].get_height())
            self.f = True

        else:
            self.f = False


paused = True
deadd = True


def set_p():
    global paused
    paused = False


def set_d():
    global dead
    dead = False


def dead():
    global dead
    bottn = Button(650, 500)
    bottn_2 = Button(650, 500)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        bottn.draw(320, 150, 'DEAD', start_screen, 300)
        bottn.draw(320, 150, 'DEAD', terminate, 300)

        pygame.display.flip()
        clock.tick(15)


def pays():
    bottn = Button(350, 100)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        bottn.draw(120, 200, 'RETURN', set_p)

        print_text('PAUSED', 210, 200, (75, 1, 1), 100)

        pygame.display.flip()
        clock.tick(15)



lvl = load_level('BETA')
for i in lvl:
    print(i)

timer = [0,0,0]


def game():
    global cooldown, sp_mob, lvl, paused, timer
    player, level_x, level_y = generate_level(lvl)
    weapon = Weapon(load_image('bow.png'), 1, 1, player)
    weapon_sp = []

    for mobs in sp_mob:
        weapon_sp.append(Weapon(load_image('sword.png'), 1, 1, mobs))

    s = 3
    s_mob = 1
    if level_x + level_y > 25:
        s = s + 1
    if level_x + level_y > 45:
        s = s + 2
    camera = Camera((level_x, level_y))
    # изменяем ракурс камеры

    mod = 'S'
    # обновляем положение всех спрайтов
    run = True
    left = False
    reath = False
    isjampcaunt = 5
    jamp = False
    went_r = load_image('hero_r.png', -1)[0]
    stend = load_image('hero_proz.png', -1)[0]
    went_l = load_image('hero_l.png', -1)[0]
    went_beak = load_image('hero_beak.png', -1)[0]
    went_lic = load_image('hero_lic.png', -1)[0]
    up_mod = ''
    hold_left = True
    inventory.increase('sword')
    inventory.increase('weapon_1')
    inventory.increase('bow')
    inventory.increase('shell')

    button = Button(100, 30)
    all_ms_bulets = []
    all_btn_bulets = []
    all_mob = []
    CorrentTime = time.time()
    while run:
        timers = time.time() - CorrentTime
        print(timers, 'time')
        if player.heath <= 0:
            dead()




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            key = pygame.key.get_pressed()

            if key[pygame.K_DOWN]:
                player.setSprite(went_lic, 3, 1)
                if mod == 'L':
                    up_mod = 'DL'
                if mod == 'R':
                    up_mod = 'DR'
                else:
                    mod = 'D'

            if key[pygame.K_UP]:
                player.setSprite(went_beak, 3, 1)
                weapon.left = True
                weapon.trans = True
                if mod == 'L':
                    up_mod = 'UL'
                if mod == 'R':
                    up_mod = 'UR'
                else:
                    mod = 'U'

            if key[pygame.K_RIGHT]:
                player.setSprite(went_r, 3, 1)
                if mod == 'U':
                    up_mod = 'RU'
                if mod == 'D':
                    up_mod = 'RD'
                else:
                    mod = 'R'

            if key[pygame.K_LEFT]:
                player.setSprite(went_l, 3, 1)
                weapon.left = True
                weapon.trans = True
                if mod == 'U':
                    up_mod = 'LU'
                if mod == 'D':
                    up_mod = 'LD'
                else:
                     mod = 'L'

            if key[pygame.K_ESCAPE]:
                mod = 'S'
                paused = True
                weapon.left = False
                player.setSprite(stend, 2, 1)
                pays()

            if event.type == pygame.KEYUP:
                if event.key == 274 or event.key == 275 or event.key == 276 or event.key == 273:
                    mod = 'S'
                if event.key == 274:    # down
                    player.setSprite(stend, 2, 1)
                if event.key == 275:    # raeth
                    player.setSprite(stend, 2, 1)
                if event.key == 276:    # left
                    weapon.trans = True
                    weapon.left = False
                    player.setSprite(stend, 2, 1)
                if event.key == 273:    # up
                    weapon.trans = True
                    weapon.left = False
                    player.setSprite(stend, 2, 1)

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if click[2] and not hold_left:
            print(mouse)
            inventory.set_start_cell(mouse[0], mouse[1])
            hold_left = True
        if hold_left and not click[2]:
            print(pygame.mouse.get_pos())
            inventory.set_end_cell(mouse[0], mouse[1])
            hold_left = False

        if not jamp:
            if keys[pygame.K_SPACE]:
                weapon.trans = False
                jamp = True
        else:
            weapon.trans = False
            if isjampcaunt >= -5:
                if isjampcaunt < 0:
                    player.rect.top += (isjampcaunt ** 2) // 2
                else:
                    player.rect.top -= (isjampcaunt ** 2) // 2
                isjampcaunt -= 1
            else:
                jamp = False
                isjampcaunt = 5
        s_m = 10
        if player.heath <= 0:
            dead()

        if mod == 'S':
            pass
        if mod == 'L':
            player.rect.left -= s
            if pygame.sprite.spritecollideany(player, box_group):
                player.rect.left += s
        if mod == 'R':
            player.rect.left += s
            if pygame.sprite.spritecollideany(player, box_group):
                player.rect.left -= s

        if mod == 'D':
            player.rect.top += s
            if pygame.sprite.spritecollideany(player, box_group):
                player.rect.top -= s
        if mod == 'U':
            player.rect.top -= s
            if pygame.sprite.spritecollideany(player, box_group):
                player.rect.top += s

        for i in range(len(sp_mob)):
            if sp_mob[i].heath > 0:
                print(sp_mob[i].heath)
                if pygame.sprite.spritecollideany(sp_mob[i], bullet_group):
                    sp_mob[i].heath -= 25
                if pygame.sprite.spritecollideany(sp_mob[i], box_group):
                    sp_mob[i].f = False

                if pygame.sprite.spritecollideany(sp_mob[i], player_group):
                    sp_mob[i].f = False

                if pygame.sprite.spritecollideany(sp_mob[i], player_group):
                    sp_mob[i].f = False

                if not pygame.sprite.spritecollideany(sp_mob[i], box_group):
                    sp_mob[i].f = True

                if pygame.sprite.spritecollideany(player, bullet_group_mob) and not player.block:
                    player.heath -= 10 // len(mob_group)

                sp_mob[i].shoot(weapon_sp[i], player)
                for bullet in bullet_group_mob:
                    if pygame.sprite.spritecollideany(bullet, player_group) or \
                            pygame.sprite.spritecollideany(bullet, box_group) or not bullet.f:
                        bullet_group_mob.remove(bullet)

        click = pygame.mouse.get_pressed()
        mouse = pygame.mouse.get_pos()
        if not cooldown:
            if click[0]:
                print(10)
                player.shoot(weapon, mouse[0], mouse[1])
                cooldown = 30
        else:
            cooldown -= 1
            print_text('cooldown - ' + str(cooldown // 10), 150, 150 - 50, (50, 50, 1))
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill(pygame.Color('white'))
        tiles_group.draw(screen)
        hellca_group.draw(screen)
        player_group.draw(screen)
        weapon_group.draw(screen)
        box_group.draw(screen)
        mob_group.draw(screen)
        bullet_group.draw(screen)
        bullet_group_mob.draw(screen)
        print(timer)
        inventory.draw_panel()
        if keys[pygame.K_LSHIFT]:
            player.stamin -= 1
            if player.stamin > 0:
                s = 10
            else:
                s = 5
        else:
            s = 5
            player.stamin += 0.4

        if keys[pygame.K_TAB]:
            inventory.draw_whole()

        if keys[pygame.K_1]:
            print(1)
            try:
                weapon.setSprite(load_image(inventory.inventory_panel[0].name + '.png'), 1, 1)
            except AttributeError:
                pass

        if keys[pygame.K_2]:
            print(2)
            try:
                weapon.setSprite(load_image(inventory.inventory_panel[1].name + '.png'), 1, 1)
            except AttributeError:
                pass

        if keys[pygame.K_3]:
            print(3)
            try:
                weapon.setSprite(load_image(inventory.inventory_panel[2].name + '.png'), 1, 1)
            except AttributeError:
                pass

        if keys[pygame.K_4]:
            print(4)
            try:
                weapon.setSprite(load_image(inventory.inventory_panel[3].name + '.png'), 1, 1)
            except AttributeError:
                pass

        if keys[pygame.K_5]:
            print(5)
            try:
                weapon.setSprite(load_image(inventory.inventory_panel[4].name + '.png'), 1, 1)
            except AttributeError:
                pass
        for hellca in hellca_group:
            if pygame.sprite.spritecollideany(hellca, player_group):
                player.heath += 10
                hellca_group.remove(hellca)
        for bullet in all_btn_bulets:
            if not bullet.move():
                all_btn_bulets.remove(bullet)
        for bullet in bullet_group:
            if pygame.sprite.spritecollideany(bullet, mob_group) or\
                    pygame.sprite.spritecollideany(bullet, box_group) or not bullet.f:
                bullet_group.remove(bullet)

        button.draw(5, 110, 'quit', start_screen)
        tm_sp = str(timers).split('.')
        print_text('Time  ' + tm_sp[0] + ' :' + tm_sp[1][:2], 1007, 0, (200, 200, 50), 45)
        all_sprites.update()
        pygame.display.flip()

        clock.tick(60)
    pygame.quit()


def lvl_1():
    global lvl, cooldown, sp_mob, lvl, paused, mod, run, left, reath, isjampcaunt, jamp, sp_mob, s, player, level_x, level_y, \
        tiles_group, player_group, all_sprites, box_group, weapon_group, bullet_group, bullet_group_mob, mob_group, hellca_group, \
        mob_cord
    player, level_x, level_y = None, None, None
    weapon = None
    weapon_sp = []
    sp_mob = []

    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    box_group = pygame.sprite.Group()
    weapon_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    bullet_group_mob = pygame.sprite.Group()
    mob_group = pygame.sprite.Group()
    hellca_group = pygame.sprite.Group()
    cooldown = 0
    mob_cord = []
    s = 5

    # изменяем ракурс камеры

    mod = 'S'
    # обновляем положение всех спрайтов
    run = True
    left = False
    reath = False
    isjampcaunt = 5
    jamp = False
    lvl = load_level('BETA')
    game()


def lvl_2():
    global lvl, cooldown, sp_mob, lvl, paused, mod, run, left,reath,isjampcaunt,jamp, sp_mob, s, player, level_x,level_y, \
        tiles_group, player_group, all_sprites, box_group, weapon_group, bullet_group, bullet_group_mob, mob_group,hellca_group,\
    mob_cord
    player, level_x, level_y = None, None, None
    weapon = None
    weapon_sp = []
    sp_mob = []

    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    box_group = pygame.sprite.Group()
    weapon_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    bullet_group_mob = pygame.sprite.Group()
    mob_group = pygame.sprite.Group()
    hellca_group = pygame.sprite.Group()
    cooldown = 0
    mob_cord = []
    s = 5


    # изменяем ракурс камеры

    mod = 'S'
    # обновляем положение всех спрайтов
    run = True
    left = False
    reath = False
    isjampcaunt = 5
    jamp = False
    lvl = load_level('BETA_2')
    game()

def lvl_up():
    fon = pygame.transform.scale(load_image('fon.png')[0], (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    text = 'DARKCASTLE'
    botton_lvl1 = Button(100, 50)
    botton_lvl2 = Button(100, 50)
    botton_quit = Button(100, 50)
    for i in range(len(text)):
        print_text(text[i], 10, 70 * i, (75, 12 - i, 12 - i), 70)
    while True:
        botton_lvl1.draw(50, 110, 'lvl_1', lvl_1, 50)
        botton_lvl2.draw(50, 171, 'lvl_2', lvl_2, 50)
        botton_quit.draw(50, 271, 'quit', terminate, 50)
        pygame.event.get()
        pygame.display.flip()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png')[0], (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    text = 'DARKCASTLE'
    botton = Button(100, 50)
    botton_quit = Button(100, 50)
    for i in range(len(text)):
        print_text(text[i], 10, 70 * i, (75, 12 - i, 12 - i), 70)
    while True:
        botton.draw(50, 20, 'GAME', lvl_up, 50)
        botton_quit.draw(50, 71, 'EXIT', terminate, 50)
        pygame.event.get()
        pygame.display.flip()


start_screen()

