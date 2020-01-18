import pygame
from parameters import screen
pygame.init()

class Resource:
    def __init__(self, name, image_path):
        self.name = name
        self.amount = 0
        self.image = pygame.image.load(image_path)


class Inventory:
    def __init__(self):
        self.resources = {
            "weapon_1": Resource('weapon_1', r'data/weapon_1.png'),
            "weapon_2": Resource('weapon_2', r'data/weapon_2.png'),
            "weapon_3": Resource('weapon_3', r'data/weapon_3.png'),
        }

        self.inventory_panel = [None] * 4
        self.whole_inventoty = [None] * 8

    def get_amout(self, name):
        try:
            return self.resources[name].amount
        except KeyError:
            return -1

    def increase(self, name):
        try:
            self.resources[name].amount += 1
            self.update_whole()
        except KeyError:
            print('Error inventar')

    def update_whole(self):
        for name, resource in self.resources.items():
            if resource.amount != 0 and resource not in self.whole_inventoty:
                self.whole_inventoty.insert(self.whole_inventoty.index(None), resource)
                self.whole_inventoty.remove(None)

    def draw_whole(self):
        x = 60
        y = 60
        side = height = 80
        step = 100
        for cell in self.whole_inventoty:
            pygame.draw.rect(screen, (200, 215, 227), (x, y, side, side))
            x += step
            if x == 460:
                x = 60
                y += step


inventory = Inventory()

