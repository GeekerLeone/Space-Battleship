from math import fabs, floor
import pygame as pg
import random
import os

from pygame.constants import BLEND_RGB_MAX
FPS = 60
WIDTH = 500
HEIGHT = 600
# Color choice
RED = (255,0,0) # Red
BLACK = (0,0,0) # (R,G,B)
WHITE = (255, 255, 255)
GREEN = (0,255,0) # Green
YELLOW = (255,255,204) # Yellow


ship_size = (30,20)
rock_size = (0,0)
def rock_size_create():
    size = random.randrange(30,100)
    rock_size = (size, size)
    return rock_size
bullet_size = (10,30)

def new_rock():
    rock_size = rock_size_create()
    r = Rock(rock_size)
    all_sprites.add(r) 
    rocks.add(r)
score = 0

# Initialize conditon
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
running = True
clock = pg.time.Clock()
pg.display.set_caption('SpaceBattleShip') # Window title

# Load resourse (images)
background_img = pg.image.load(os.path.join('img','background.png')).convert()
player_img = pg.image.load(os.path.join('img','player.png')).convert()
player_live_img = pg.transform.scale(player_img, (25,19))
player_live_img.set_colorkey(BLACK)
player_reborn_img = pg.image.load(os.path.join('img','ship_reborn.png')).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pg.image.load(os.path.join('img',f'rock{i}.png')).convert()) 
bullet_img = pg.image.load(os.path.join('img','bullet.png')).convert()
expl_anim = {} # dictionary
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pg.image.load(os.path.join('img',f'expl{i}.png')).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pg.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pg.transform.scale(expl_img, (30, 30)))
    player_expl_img = pg.image.load(os.path.join('img',f'player_expl{i}.png')).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(pg.transform.scale(player_expl_img, (75, 75)))
power_imgs = {}
power_imgs['shield'] = pg.image.load(os.path.join('img','shield.png')).convert()
power_imgs['gun'] = pg.image.load(os.path.join('img','gun.png')).convert()


# Load sound
shoot_sound = pg.mixer.Sound(os.path.join('sound','shoot.wav'))
shield_sound = pg.mixer.Sound(os.path.join('sound','pow0.wav'))
gun_sound = pg.mixer.Sound(os.path.join('sound','pow1.wav'))
Player_death_sound = pg.mixer.Sound(os.path.join('sound','rumble.ogg'))
rock_expl = [
    pg.mixer.Sound(os.path.join('sound','expl0.wav')),
    pg.mixer.Sound(os.path.join('sound','expl1.wav'))
    ]
pg.mixer.music.load(os.path.join('sound','background.ogg')) # BGM play
pg.mixer.music.set_volume(0.3) # Control the volume of BGM
# Load text
font_name = os.path.join('font.ttf')  #pg.font.match_font('arial black')
def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    pg.draw.rect(surf, GREEN, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    draw_text(screen, '雷霆战机', 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, 'control ship movement, fire bullets', 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, 'Press any Key to start!', 18, WIDTH/2, HEIGHT*3/4)
    pg.display.update()
    waiting = True
    while waiting :
        clock.tick(FPS) # The function only can be operated 60 times in a second
    # Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.KEYUP:
                waiting = False
                

class Player(pg.sprite.Sprite): # Battleship

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(player_img, (50,38))
        self.image.set_colorkey(BLACK)
        self.image_orignal = self.image.copy()
        self.rect = self.image.get_rect()
        self.radius = 23
        #pg.draw.circle(self.image, YELLOW, self.rect.center, 27)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.invincible = False
        self.reborn_time = 0
        self.gun_level = 1
        self.gun_time = 0
    
    def update(self):

        if self.gun_level > 1 and pg.time.get_ticks() - self.gun_time > 4000:
            self.gun_level -= 1
            self.gun_time = pg.time.get_ticks()


        if self.hidden and pg.time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        if self.invincible and pg.time.get_ticks() - self.reborn_time > 3000:
            self.invincible = False
            self.image = self.image_orignal

        key_pressed = pg.key.get_pressed()
        if key_pressed[pg.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pg.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.left > WIDTH:
            self.rect.right = 0
        elif self.rect.right <0:
            self.rect.left = WIDTH
    def shoot(self):
        if self.gun_level == 1:
            bullet = Bullet(self.rect.centerx, self.rect.top, 0)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
        elif self.gun_level == 2:
            bullet1 = Bullet(self.rect.left, self.rect.centery, 0)
            bullet2 = Bullet(self.rect.right, self.rect.centery, 0)
            all_sprites.add(bullet1)
            all_sprites.add(bullet2)
            bullets.add(bullet1)
            bullets.add(bullet2)
            shoot_sound.play()
        elif self.gun_level >= 3:
            bullet_center = Bullet(self.rect.centerx, self.rect.centery, 0)
            bullet_L = Bullet(self.rect.left, self.rect.centery, -1)
            bullet_R = Bullet(self.rect.right, self.rect.centery, 1)
            all_sprites.add(bullet_center)
            all_sprites.add(bullet_L)
            all_sprites.add(bullet_R)
            bullets.add(bullet_center)
            bullets.add(bullet_L)
            bullets.add(bullet_R)
            shoot_sound.play()


    
    def gunup(self):
        self.gun_level += 1
        self.gun_time = pg.time.get_ticks()


    def hide(self):
        self.hidden = True
        self.hide_time = pg.time.get_ticks()
        self.rect.center = (WIDTH/2, -1000)

    def reborn(self):
        self.invincible = True
        self.reborn_time = pg.time.get_ticks()
        self.image = pg.transform.scale(player_reborn_img, (60,60))
        self.image.set_colorkey(BLACK)
        

class Rock(pg.sprite.Sprite): # Rock

    def __init__(self,rock_size):
        pg.sprite.Sprite.__init__(self)
        self.image_orignal = pg.transform.scale(random.choice(rock_imgs), rock_size)
        self.image_orignal.set_colorkey(BLACK)
        self.image = self.image_orignal.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.85 / 2
        #pg.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -100)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-5, 5)
        self.total_degree = 0
        self.rotate_degree = random.randrange(-3, 3)
    
    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360
        self.image = pg.transform.rotate(self.image_orignal, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.left < 0:
            self.speedx = -self.speedx
            self.rect.x += self.speedx
        elif self.rect.right > WIDTH:
            self.speedx = -self.speedx
            self.rect.x += self.speedx
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.rect.left = random.randrange(0,390)

class Bullet(pg.sprite.Sprite): # Bullet

    def __init__(self,x,y,speedx):
        pg.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        self.speedx = speedx
    
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pg.sprite.Sprite): # Explosion

    def __init__(self,center, size):
        pg.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 50
    
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect =self.image.get_rect()
                self.rect.center = center

class Power(pg.sprite.Sprite): # Power

    def __init__(self,center):
        pg.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

all_sprites = pg.sprite.Group()
rocks = pg.sprite.Group()
bullets = pg.sprite.Group()
powers = pg.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(10): # The number of Rocks
 #  rock_size = random.randrange(10,70)
 #  rock_size = (rock_size, rock_size)
    new_rock()
pg.mixer.music.play(-1)

show_init = True


while running:
    if show_init:
        draw_init()
        show_init = False

    clock.tick(FPS) # The function only can be operated 60 times in a second
    # Input
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                player.shoot()

    # Update
    all_sprites.update()
    hits = pg.sprite.groupcollide(rocks, bullets, True, True ) # Bullets hit rocks  Dictionary pg.sprite.collide_circle 
    for hit in hits:
        score += int(hit.radius)
        random.choice(rock_expl).play() 
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        new_rock()
        if random.random() > 0.50: # Probability of power drop
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        
    hits = pg.sprite.spritecollide(player, powers, True )
    for hit in hits:
        if hit.type == 'shield':
            player.health += 25
            shield_sound.play()
            if player.health >= 100:
                player.health = 100
        elif hit.type == 'gun':
            gun_sound.play()
            player.gunup()

    crash = pg.sprite.spritecollide(player, rocks, True, pg.sprite.collide_circle)  # Rocks hit ship list
    for hit in crash:
        new_rock()
        if not(player.invincible):
            player.health -= 25
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)

        if player.health <= 0:
            dealth = Explosion(player.rect.center, 'player')
            all_sprites.add(dealth)
            Player_death_sound.play()
            player.lives -= 1
            player.gun_level = 1
            player.health = 100
            player.hide()
            player.reborn()
        
    if player.lives <= 0 and not(dealth.alive()):
        running = False    
    # Display 
    screen.fill(BLACK)
    screen.blit(background_img, (0,0)) # Put background_img at 0, 0
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 8, 15)
    draw_lives(screen, player.lives, player_live_img, WIDTH - 100, 15)
    pg.display.update()

pg.quit()