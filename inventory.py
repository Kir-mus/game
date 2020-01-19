import pygame
from parameters import screen, display_height, display_width
from f import print_text
pygame.init()


class Resource:
    def __init__(self, name, image_path):
        self.name = name
        self.amount = 0
        self.image = pygame.image.load(image_path)


class Inventory:
    def __init__(self):
        self.resources = {
            "sword": Resource('sword', r'data/sword.png'),
            "weapon_2": Resource('weapon_2', r'data/weapon_2.png'),
            "bow": Resource('bow', r'data/bow.png'),
            "shell": Resource('shell', r'data/shell.png'),
            "weapon_5": Resource('shell', r'data/shell.png')
        }

        self.inventory_panel = [None] * 5
        self.whole_inventoty = [None] * 8
        self.start_cell = 0
        self.end_cell = 0

    def get_amout(self, name):
        try:
            return self.resources[name].amount
        except KeyError:
            return -1

    def increase(self, name):
        try:
            self.resources[name].amount += 1
            self.update()
            print(self.whole_inventoty)
        except KeyError:
            print('Error inventar')

    def update(self):
        for name, resource in self.resources.items():
            if resource.amount != 0 and resource not in self.whole_inventoty and resource not in self.inventory_panel:
                self.whole_inventoty.insert(self.whole_inventoty.index(None), resource)
                self.whole_inventoty.remove(None)

    def draw_whole(self):
        x = 40
        y = 150
        side = 80
        step = 100
        pygame.draw.rect(screen, (182, 195, 206), (x - 20, y - 20, 420, 220), 2)
        for cell in self.whole_inventoty:
            pygame.draw.rect(screen, (200, 215, 227), (x, y, side, side), 2)
            if cell is not None:
                screen.blit(cell.image, (x + 15, y + 15))
                print_text(str(cell.amount), x + 50, y + 50, font_size=20, font_color=(143, 123, 121))
            x += step
            if x == 440:
                x = 40
                y += step

    def draw_panel(self):
        x = display_width // 4 + 50
        y = display_height - 100
        side = 80
        step = 100

        for cell in self.inventory_panel:
            pygame.draw.rect(screen, (200, 215, 227), (x, y, side, side), 2)
            if cell is not None:
                screen.blit(cell.image, (x + 15, y + 15))
                print_text(str(cell.amount), x + 50, y + 50, font_size=20, font_color=(143, 123, 121))
            x += step

    def set_start_cell(self, mouse_x, mouse_y):
        start_x = 40
        start_y = 150
        step = 100
        side = 80

        for y in range(0, 2):
            for x in range(0, 4):
                cell_x = start_x + x * step
                cell_y = start_y + y * step

                if cell_x <= mouse_x <= cell_x + side and cell_y <= mouse_y <= cell_y + side:
                    self.start_cell = y * 4 + x
                    print('Start' + str(y * 4 + x))
                    return

        start_x = display_width // 4 + 50
        start_y = display_height - 100
        for x in range(0, 5):
            cell_x = start_x + x * step
            cell_y = start_y

            if cell_x <= mouse_x <= cell_x + side and cell_y <= mouse_y <= cell_y + side:
                self.start_cell = 8 + x
                print('Start' + str(8 + x))
                return

    def set_end_cell(self, mouse_x, mouse_y):
        start_x = 40
        start_y = 150
        step = 100
        side = 80

        for y in range(0, 2):
            for x in range(0, 4):
                cell_x = start_x + x * step
                cell_y = start_y + y * step

                if cell_x <= mouse_x <= cell_x + side and cell_y <= mouse_y <= cell_y + side:
                    self.end_cell = y * 4 + x
                    print('End' + str(y * 4 + x))
                    self.swap_cells()
                    return
        start_x = display_width // 4 + 50
        start_y = display_height - 100
        for x in range(0, 5):
            cell_x = start_x + x * step
            cell_y = start_y

            if cell_x <= mouse_x <= cell_x + side and cell_y <= mouse_y <= cell_y + side:
                self.end_cell = 8 + x
                print('End' + str(8 + x))
                self.swap_cells()
                return

    def swap_cells(self):
        if self.end_cell < 8:
            temp = self.whole_inventoty[self.end_cell]
            if self.start_cell < 8:
                self.whole_inventoty[self.end_cell] = self.whole_inventoty[self.start_cell]
                self.whole_inventoty[self.start_cell] = temp
            else:
                self.start_cell -= 8
                self.whole_inventoty[self.end_cell] = self.inventory_panel[self.start_cell]
                self.inventory_panel[self.start_cell] = temp
        else:
            self.end_cell -= 8
            temp = self.inventory_panel[self.end_cell]
            if self.start_cell < 8:
                self.inventory_panel[self.end_cell] = self.whole_inventoty[self.start_cell]
                self.whole_inventoty[self.start_cell] = temp
            else:
                self.start_cell -= 8
                self.inventory_panel[self.end_cell] = self.inventory_panel[self.start_cell]
                self.inventory_panel[self.start_cell] = temp


inventory = Inventory()