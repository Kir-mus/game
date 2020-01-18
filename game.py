import os
import pygame
import sys
from parameters import screen
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
cooldown = 0
mob_cord = []


def print_text(mes, x, y, font_color=(0, 0, 0), font_size=30, font_type='data/18897.otf'):
    font_type = pygame.font.Font(font_type, font_size)
    text = font_type.render(mes, True, font_color)
    screen.blit(text, (x, y))


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
    return image


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


tile_images = {'wall': load_image('sten.png'), 'empty': load_image('pol.png')}
player_image1 = load_image('mar.png')
x = None
y = None
xy = []


def generate_level(level):
    global x, y, xy, mob_cord
    new_player, new_mob, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '!':
                Tile('empty', x, y)
                new_mob = Mob(load_image("hero_proz.png", -1), 2, 1, x * 50, y * 50)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(load_image("hero_proz.png", -1), 2, 1, x * 50, y * 50)

    # вернем игрока, а также размер поля в клетках

    return new_player, new_mob, x, y


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

        self.columns = columns
        self.rows = rows
        self.sheet = sheet
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
        self.sheet = sprite
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
                    frame_location, self.test_rect.size)), (35, 35)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        # self.image = pygame.transform.scale(self.frames[self.cur_frame], (40, 40))
        self.image = self.frames[self.cur_frame]
        if not self.left:
            self.rect = pygame.Rect(self.playre.rect.x + 25, self.playre.rect.y, self.frames[self.cur_frame].get_width(),
                                    self.frames[self.cur_frame].get_height())
        else:
            self.rect = pygame.Rect(self.playre.rect.x - 25, self.playre.rect.y,
                                    self.frames[self.cur_frame].get_width(),
                                    self.frames[self.cur_frame].get_height())
        if self.trans:
            self.sheet = pygame.transform.flip(self.sheet, 1, 0)
            self.frames = []
            self.cut_sheet(self.sheet, self.columns, self.rows)
            self.trans = False


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.heath = 100
        self.stamin = 100
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
        if self.heath >= 0:
            pygame.draw.rect(screen, (144, 23, 1), (5, 5, self.heath * 4, 30))
        else:
            pygame.draw.rect(screen, (144, 144, 23), (5, 40, 0, 30))
        print_text('HP', 5, 5)
        if self.stamin >= 0:
            pygame.draw.rect(screen, (144, 144, 23), (5, 40, self.stamin * 4, 30))
        else:
            pygame.draw.rect(screen, (144, 144, 23), (5, 40, 0, 30))
        print_text('STAMIN', 5, 40)

    def shoot(self, weapon, zel, y):
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
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(mob_group, all_sprites)
        self.heat = 100
        self.terr_x = 4 * 50
        self.terr_y = 4 * 50
        self.columns = columns
        self.rows = rows
        self.sheet = sheet
        self.kil = False
        self.speed = 2
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
        self.cooldown_s = 0
        self.all_bullets = []
        self.width = 50
        self.heght = 50

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.heat > 0:
            pygame.draw.rect(screen, (144, 23, 1), (self.rect.x - 10, self.rect.y - 5, self.heat // 2, 5))
            pygame.draw.rect(screen, (0, 0, 0), (self.rect.x - 10, self.rect.y - 5, self.heat // 2, 5), 1)
        else:
            pygame.draw.rect(screen, (144, 23, 1), (self.rect.x - 10, self.rect.y - 5, 50, 5), 1)
        if self.kil:
            self.heat -= 5
            self.kil = False
        if self.heat <= 0:
            self.setSprite(load_image('kill.png', -1), 1, 1)

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

    def chek_dmg(self, bullet):
        if self.x <= bullet.x <= self.x + self.width:
            if self.y <= bullet.y <= self.y + self.heght:
                self.kil = True

    def shoot(self, weapon, zel):
        if not self.heat <= 0:
            if not self.cooldown_s:
                new_bullet = Bulletmob(bullet_img, 1, 1, weapon, zel)
                new_bullet.find_path(zel.rect.centerx, zel.rect.centery)
                self.all_bullets.append(new_bullet)

                self.cooldown_s = 200
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


bullet_img = load_image('strela.png', -1)


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


def pays():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        print_text('PAUSED', 210, 200, (75, 1, 1), 100)
        key = pygame.key.get_pressed()
        if key[pygame.K_RETURN]:
            paused = False
        pygame.display.flip()
        clock.tick(15)


def game():

    global cooldown, mob_cord
    player, mob, level_x, level_y = generate_level(load_level('BETA'))
    weapon = Weapon(load_image('weapon_4.png'), 1, 1, player)
    print(mob_group)
    weapon_sp = []

    for mobs in mob_group:
        weapon_sp.append(Weapon(load_image('weapon_3.png'), 1, 1, mobs))
    weapon2 = Weapon(load_image('weapon_3.png'), 1, 1, mob)
    s = 3
    s_mob = 1
    if level_x + level_y > 25:
        s = 4
    if level_x + level_y > 45:
        s = 5
    camera = Camera((level_x, level_y))
    # изменяем ракурс камеры

    mod = 'S'
    # обновляем положение всех спрайтов
    run = True
    left = False
    reath = False
    isjampcaunt = 5
    jamp = False
    went_r = load_image('hero_r.png', -1)
    stend = load_image('hero_proz.png', -1)
    went_l = load_image('hero_l.png', -1)
    went_beak = load_image('hero_beak.png', -1)
    went_lic = load_image('hero_lic.png', -1)
    up_mod = ''

    button = Button(100, 30)
    all_ms_bulets = []
    all_btn_bulets = []
    all_mob = []
    all_mob.append(mob)

    while run:
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
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
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

        for mob in mob_group:
            if pygame.sprite.spritecollideany(mob, bullet_group):
                mob.kil = True
            if pygame.sprite.spritecollideany(player, bullet_group_mob):
                player.heath -= 1

            for weap in weapon_sp:
                mob.shoot(weap, player)

            click = pygame.mouse.get_pressed()
            mouse = pygame.mouse.get_pos()
            if not cooldown:
                if keys[pygame.K_x]:
                    cooldown = 30
                    all_btn_bulets.append(Bullet(bullet_img, 1, 1, weapon, mob))
                elif click[0]:
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
        weapon_group.draw(screen)
        player_group.draw(screen)
        box_group.draw(screen)
        mob_group.draw(screen)
        bullet_group.draw(screen)
        bullet_group_mob.draw(screen)
        if keys[pygame.K_TAB]:
            inventory.draw_whole()
            print('i')

        if keys[pygame.K_1]:
            inventory.increase('weapon_1')
            sleep(0.1)
        if keys[pygame.K_2]:
            inventory.increase('weapon_2')
            sleep(0.1)
        if keys[pygame.K_3]:
            inventory.increase('weapon_3')
            sleep(0.1)

        for bullet in all_btn_bulets:
            if not bullet.move():
                all_btn_bulets.remove(bullet)
        for bullet in bullet_group:
            if not bullet.f:
                bullet_group.remove(bullet)
        for bullet in bullet_group_mob:
            if not bullet.f:
                bullet_group_mob.remove(bullet)
        button.draw(5, 110, 'quit', terminate)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(30)
        print(mob_cord)
    pygame.quit()


def start_screen():

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    text = 'DARKCASTLE'
    botton = Button(100, 50)
    botton_quit = Button(100, 50)
    for i in range(len(text)):
        print_text(text[i], 10, 70 * i, (75, 12 - i, 12 - i), 70)
    while True:
        botton.draw(50, 20, 'GAME', game, 50)
        botton_quit.draw(50, 60, 'QUIT', terminate, 50)
        pygame.event.get()
        pygame.display.flip()

start_screen()