import pygame
import os
import random

# General settings and asset initialization
pygame.display.set_caption("GALACTIC INVADERS")
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 1000
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ENEMY_SHIP_3 = pygame.image.load(os.path.join("assets", "enemy_spaceship_3.png"))
ENEMY_SHIP_2 = pygame.image.load(os.path.join("assets", "enemy_spaceship_2.png"))
ENEMY_SHIP_1 = pygame.image.load(os.path.join("assets", "enemy_spaceship_1.png"))
PLAYER_1_SPACESHIP = pygame.image.load(os.path.join("assets", "player_spaceship.png"))
PLAYER_2_SPACESHIP = pygame.image.load(os.path.join("assets", "player_2_spaceship.png"))
PLAYER_LASER = pygame.image.load(os.path.join("assets", "red_laser.png"))
ENEMY_LASER = pygame.image.load(os.path.join("assets", "green_laser.png"))
MENU_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "menu_background.jpg")),
                                         (SCREEN_WIDTH, SCREEN_HEIGHT))
GAME_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "game_background.jpg")),
                                         (SCREEN_WIDTH, SCREEN_HEIGHT))
GAME_TITLE = pygame.image.load(os.path.join("assets", "game_title.png"))
pygame.font.init()
MAIN_FONT = pygame.font.Font("Grand9K_Pixel.ttf", 50)
HELP_FONT = pygame.font.Font("Grand9K_Pixel.ttf", 25)

PLAY_IMAGE = pygame.image.load(os.path.join("assets", "button_play.png")).convert_alpha()
EXIT_IMAGE = pygame.image.load(os.path.join("assets", "button_exit.png")).convert_alpha()
SOLO_IMAGE = pygame.image.load(os.path.join("assets", "solo_button.png")).convert_alpha()
DUO_IMAGE = pygame.image.load(os.path.join("assets", "duo_button.png")).convert_alpha()
INSTRUCTIONS_IMAGE = pygame.image.load(os.path.join("assets", "instructions_button.png")).convert_alpha()


class Button:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        WINDOW.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class SpaceShip:
    SHOT_COOLDOWN = 5  # Shot rate

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(SCREEN_HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.SHOT_COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Bullet(self.x + 42, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(SpaceShip):
    player_ships = {
        1: PLAYER_1_SPACESHIP,
        2: PLAYER_2_SPACESHIP
    }

    def __init__(self, x, y, health=100, player_number=1):
        super().__init__(x, y, health)
        self.ship_img = self.player_ships[player_number]
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(SCREEN_HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))


class Enemy(SpaceShip):
    ENEMY_SHIPS = [ENEMY_SHIP_1, ENEMY_SHIP_2, ENEMY_SHIP_3]

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.ENEMY_SHIPS[random.randrange(0, 3)], ENEMY_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Bullet(self.x + 30, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


# detecting collision by measuring the distance between the two offsets of the objects
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main(num_of_players=1):
    is_running = True
    refreshing_rate = 60
    level = 0
    lives = 5

    enemies = []
    wave_duration = 5
    enemy_speed = 3

    player_speed = 12
    enemy_laser_speed = 8
    player_laser_speed = -16

    players = [Player(300, 630)]
    if num_of_players == 2:
        players.append(Player(600, 650, 100, 2))
        players[0].x = 150

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WINDOW.blit(GAME_BACKGROUND, (0, 0))

        lives_title = MAIN_FONT.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_title = MAIN_FONT.render(f"Level: {level}", 1, (255, 255, 255))

        WINDOW.blit(lives_title, (10, 10))
        WINDOW.blit(level_title, (SCREEN_WIDTH - level_title.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WINDOW)

        for player in players:
            player.draw(WINDOW)

        if lost:
            you_lost_screen(num_of_players)

        pygame.display.update()

    while is_running:
        clock.tick(refreshing_rate)
        redraw_window()

        # lost-status for two players
        if num_of_players > 1:
            for i in range(0, 2):
                if lives <= 0 or players[i].health <= 0:
                    lost = True
                    lost_count += 1
        else:
            if lives <= 0 or players[0].health <= 0:
                lost = True
                lost_count += 1

        # if the two players died
        if lost:
            if lost_count > refreshing_rate * 3:
                is_running = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_duration += 5
            for i in range(wave_duration):
                enemy = Enemy(random.randrange(50, SCREEN_WIDTH - 100), random.randrange(-1500, -100))
                enemies.append(enemy)
                if i % 5 == 0:
                    pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and players[0].x - player_speed > 0:  # left
            players[0].x -= player_speed
        if keys[pygame.K_d] and players[0].x + player_speed + players[0].get_width() < SCREEN_WIDTH:  # right
            players[0].x += player_speed
        if keys[pygame.K_w] and players[0].y - player_speed > 0:  # up
            players[0].y -= player_speed
        if keys[pygame.K_s] and players[0].y + player_speed + players[0].get_height() + 15 < SCREEN_HEIGHT:  # down
            players[0].y += player_speed
        if keys[pygame.K_SPACE]:
            players[0].shoot()
        if num_of_players > 1:
            if keys[pygame.K_LEFT] and players[1].x - player_speed > 0:  # left
                players[1].x -= player_speed
            if keys[pygame.K_RIGHT] and players[1].x + player_speed + players[1].get_width() < SCREEN_WIDTH:  # right
                players[1].x += player_speed
            if keys[pygame.K_UP] and players[1].y - player_speed > 0:  # up
                players[1].y -= player_speed
            if keys[pygame.K_DOWN] and players[1].y + player_speed + players[1].get_height() + 15 < SCREEN_HEIGHT: #down
                players[1].y += player_speed
            if keys[pygame.K_SPACE]:
                players[1].shoot()

        for player in players:
            for enemy in enemies[:]:
                enemy.move(enemy_speed)
                enemy.move_lasers(enemy_laser_speed, player)
                if random.randrange(0, 2 * 60) == 1:
                    enemy.shoot()
                if collide(enemy, player):
                    player.health -= 10
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > SCREEN_HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)

        for player in players:
            player.move_lasers(player_laser_speed, enemies)


# menu variables
play_btn = Button(350, 600, PLAY_IMAGE)
exit_btn = Button(350, 690, EXIT_IMAGE)
solo_btn = Button(200, SCREEN_HEIGHT / 2 - SOLO_IMAGE.get_height() / 2, SOLO_IMAGE)
duo_btn = Button(500, SCREEN_HEIGHT / 2 - DUO_IMAGE.get_height() / 2, DUO_IMAGE)
help_button = Button(SCREEN_WIDTH - 106, 10, INSTRUCTIONS_IMAGE)
help_title = MAIN_FONT.render("INSTRUCTIONS", 1, (255, 255, 255))
help_description = "Use (A,W,S,D) keys to move your spaceship and press SPACE \nto shoot." \
                   " Shoot the alien ships and dodge their shots to survive.\n" \
                   "Pay attention to your health bar! once it runs out - you lose.\n" \
                   "2 player mode is available - use the arrow keys to move the \nsecond " \
                   "spaceship."
exit_help_text = HELP_FONT.render("Press ESC to go back to menu", 1, (255, 255, 255))
choose_mode_text = MAIN_FONT.render("CHOOSE A MODE", 1, (255, 255, 255))
you_lost_text = MAIN_FONT.render("GAME OVER", 1, (255, 255, 255))
play_again_text = HELP_FONT.render("Press SPACE to rematch or ESC to quit to menu", 1, (255, 255, 255))


# a function that lets you print more than one line of text on the screen
def render_multi_line(text):
    lines = text.splitlines()
    y = 300
    for i, l in enumerate(lines):
        WINDOW.blit(HELP_FONT.render(l, 0, (255, 255, 255)), (50, y))
        y += 50


def main_menu():
    play = True
    while play:
        WINDOW.blit(MENU_BACKGROUND, (0, 0))
        WINDOW.blit(GAME_TITLE, (SCREEN_WIDTH * 0.29, SCREEN_HEIGHT * 0.25))
        if play_btn.draw():
            choose_mode_menu()
        if exit_btn.draw():
            play = False
        if help_button.draw():
            instructions_menu()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
    pygame.quit()


def instructions_menu():
    running = True
    while running:
        WINDOW.blit(MENU_BACKGROUND, (0, 0))
        WINDOW.blit(help_title, (SCREEN_WIDTH / 2 - help_title.get_width() / 2, 150))
        render_multi_line(help_description)
        WINDOW.blit(exit_help_text, (SCREEN_WIDTH / 2 - exit_help_text.get_width() / 2, 600))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False


def choose_mode_menu():
    running = True
    while running:
        WINDOW.blit(MENU_BACKGROUND, (0, 0))
        WINDOW.blit(choose_mode_text, (SCREEN_WIDTH / 2 - choose_mode_text.get_width() / 2, 150))
        if solo_btn.draw():
            main()
        if duo_btn.draw():
            main(2)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False


def you_lost_screen(num_of_players):
    running = True
    while running:
        WINDOW.blit(MENU_BACKGROUND, (0, 0))
        WINDOW.blit(you_lost_text, (SCREEN_WIDTH / 2 - you_lost_text.get_width() / 2, 150))
        WINDOW.blit(play_again_text, (SCREEN_WIDTH / 2 - play_again_text.get_width() / 2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu()
                if event.key == pygame.K_SPACE:
                    running = False
                    main(num_of_players)


main_menu()
