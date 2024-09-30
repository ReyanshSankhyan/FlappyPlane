import pygame
from random import randint
from sys import exit
from settings import *

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy plane")

def image(path):
    return pygame.image.load("graphics/"+path).convert_alpha()

SCALE_FACTOR = SCREEN_HEIGHT / image("environment/background.png").get_height()

class Sky(pygame.sprite.Sprite):
    def __init__(self, num):
        super().__init__()
        self.image = pygame.transform.scale_by(image("environment/background.png"), SCALE_FACTOR)
        self.rect = self.image.get_rect(topleft=(self.image.get_width() * num, 0))

    def update(self):
        self.rect.x -= SCROLL_SPEED // 2
        if self.rect.right <= 0:
            self.rect.left = self.rect.width

class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale_by(image("environment/ground.png"), SCALE_FACTOR)
        self.rect = self.image.get_rect(bottomleft=(0, SCREEN_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos.x -= SCROLL_SPEED
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = round(self.pos.x)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, num):
        super().__init__()
        self.image = pygame.transform.scale_by(image(f"obstacles/{randint(0, 1)}.png"), SCALE_FACTOR * 1.2)
        if num == 0:
            self.rect = self.image.get_rect(bottomleft=(SCREEN_WIDTH, SCREEN_HEIGHT+randint(0, 150)))
        else:
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, randint(-150, 0)))

        self.mask = pygame.mask.from_surface(self.image)
        self.added_score = False

    def update(self, player_x):
        global score
        self.rect.x -= int(SCROLL_SPEED * 1.2)
        if self.rect.x <= player_x and self.added_score == False:
            score += 1
            self.added_score = True
        if self.rect.right <= 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.anim_frames = [image("plane/red0.png"), image("plane/red1.png"), image("plane/red2.png"), image("plane/red1.png")]
        self.anim_index = 0
        self.image = pygame.transform.scale_by(self.anim_frames[self.anim_index], SCALE_FACTOR / 1.5)
        self.rect = self.image.get_rect(center=(80, SCREEN_HEIGHT // 2))
        self.y_velocity = 0
        self.direction = 0

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.anim_index += 0.3
        if self.anim_index >= 4:
            self.anim_index = 0
        self.image = pygame.transform.scale_by(self.anim_frames[int(self.anim_index)], SCALE_FACTOR / 1.5)
        self.y_velocity += GRAVITY
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.y_velocity > -8:
                jump_sound.play()
            self.y_velocity = -JUMP_HEIGHT

        self.direction = self.y_velocity
        self.image = pygame.transform.rotozoom(self.image, -self.direction, 1)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.y += int(self.y_velocity)

big_font = pygame.font.Font("graphics/font/BD_Cartoon_Shout.ttf", 50)
title_text = big_font.render("Flappy plane", True, (64, 64, 64))

ground = Ground()
backgrounds = pygame.sprite.Group()
backgrounds.add(Sky(0), Sky(1), ground)
player = Player()

menu_img = pygame.transform.scale_by(image("ui/menu.png"), SCALE_FACTOR / 1.5)
menu_rect = menu_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

obstacles = pygame.sprite.Group()
spawn_obstacle = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_obstacle, 1600)

def exit_game():
    pygame.quit()
    exit()

def start_game():
    global game_active
    game_active = True

jump_sound = pygame.mixer.Sound("sounds/jump.wav")
jump_sound.set_volume(0.1)
bg_music = pygame.mixer.Sound("sounds/music.wav")
bg_music.set_volume(0.2)
bg_music.play(loops=-1)
score = 0
game_active = False

while True:
    for event in  pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()

        if event.type == spawn_obstacle and game_active:
            obstacles.add(Obstacle(randint(0, 1)))

    backgrounds.draw(screen)
    backgrounds.update()

    if game_active:
        screen.blit(player.image, player.rect)
        player.update()

        obstacles.draw(screen)
        obstacles.update(player.rect.x)

        score_text = pygame.font.Font("graphics/font/BD_Cartoon_Shout.ttf", 35).render(str(score), True, "black")
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 14))
        screen.blit(score_text, score_rect)

        if pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask) or pygame.sprite.collide_mask(player, ground) or player.rect.bottom <= 0:
            obstacles.empty()
            score = 0
            player = Player()
            game_active = False

    else:
        screen.blit(title_text, (SCREEN_WIDTH // 2 - (title_text.get_width() // 2), 100))
        new_img = menu_img
        mouse_pos = pygame.mouse.get_pos()
        if menu_rect.collidepoint(mouse_pos):
            new_img = pygame.transform.scale_by(menu_img, 1.1)
            if pygame.mouse.get_pressed()[0]:
                start_game()
        menu_rect = new_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(new_img, menu_rect)

    pygame.display.update()
    pygame.time.Clock().tick(60)
