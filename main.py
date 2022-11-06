import pygame
from pygame import mixer
import os
import random
import csv
import button

# initializing
mixer.init()
pygame.init()

# set screen size
SCREEN_WIDTH = 850
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.9)
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

# set window icon and title
pygame.display.set_caption('YingHaiTai')
gameIcon = pygame.image.load('assets/img/icons/game_icon.png')
pygame.display.set_icon(gameIcon)

#set FPS
clock = pygame.time.Clock()
FPS = 60

#def game vars
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 30
MAX_LEVELS = 3
MISSIONS = {1: 'CurryLand! YIN DEE TON RUB', 2: "120$ Curry", 3: "SuperCurry"}
ENEMY_NAME = ['enemy', 'enemy_two']
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
total_time = 0

#player actions
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#load music 
pygame.mixer.music.load('assets/audio/music.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0, 5000)

#load sound effect
jump_fx = pygame.mixer.Sound('assets/audio/jump.wav')
jump_fx.set_volume(0.03)
shoot_fx = pygame.mixer.Sound('assets/audio/shoot.wav')
shoot_fx.set_volume(0.02)
grenade_fx = pygame.mixer.Sound('assets/audio/grenade.wav')
grenade_fx.set_volume(0.03)

#-------------load images---------------#
intro_bg = pygame.image.load("assets/img/buttons/intro.png").convert_alpha()
intro_bg = pygame.transform.scale(intro_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
# Buttons
start_img = pygame.image.load(f'assets/img/buttons/start_btn.png').convert_alpha()
exit_img = pygame.image.load(f'assets/img/buttons/exit_btn.png').convert_alpha()
restart_img = pygame.image.load(f'assets/img/buttons/restart_btn.png').convert_alpha()

# backgrounds
tree1_img = pygame.image.load(f'assets/img/background/level{level}/tree1.png').convert_alpha()
tree2_img = pygame.image.load(f'assets/img/background/level{level}/tree2.png').convert_alpha()
mountain_img = pygame.image.load(f'assets/img/background/level{level}/mountain.png').convert_alpha()
sky_img = pygame.image.load(f'assets/img/background/level{level}/sky.png').convert_alpha()

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'assets/img/tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

#bullet and grenade
bullet_img = pygame.image.load('assets/img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('assets/img/icons/grenade.png').convert_alpha()

#boxes
health_box_img = pygame.image.load('assets/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('assets/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('assets/img/icons/grenade_box.png').convert_alpha()
item_boxes = {
	'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

#define colors
BG = (126, 149, 141)
RED = (129, 27, 27)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (5, 162, 0)
YELLOW = (252, 237, 24)
SKYBLUE = (193, 243, 255)
MINT = (22, 108, 129)

#define font
font = pygame.font.SysFont('Avenir', 30)

def draw_text(text, font, text_color, x, y):
	# to display some texts (i.e. enemies health and etc.)
	img = font.render(text, True, text_color)
	screen.blit(img, (x, y))

def draw_lvl_info_text(text, font, text_color, x, y):
    # this function is responsible for displaying level title and etc
    img = font.render(text, True, text_color)
    if total_time < 200:
        screen.blit(img, (x, y))

def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 250))
		screen.blit(tree1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - tree1_img.get_height() - 130))
		screen.blit(tree2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - tree2_img.get_height()))

#function to reset level
def reset_level():
	global trees1_img,trees2_img,mountains_img,sky_img
	if level_complete:
		trees1_img = pygame.image.load(f'assets/img/background/level{level}/tree1.png').convert_alpha()
		trees2_img = pygame.image.load(f'assets/img/background/level{level}/tree2.png').convert_alpha()
		mountains_img = pygame.image.load(f'assets/img/background/level{level}/mountain.png').convert_alpha()
		sky_img = pygame.image.load(f'assets/img/background/level{level}/sky.png').convert_alpha()

    # to reset everything if player died or completed the level
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	exit_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()
	live_entity_group.empty()
	damage_text_group.empty()

	#create empty tile list
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)

	return data

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        self.rect.y -= 1
        # delete after a few seconds
        self.counter += 1
        if self.counter > 100:
            self.kill()

class Soldier(pygame.sprite.Sprite):
	def __init__(self, soldier_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.soldier_type = soldier_type
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.health = 100
		self.max_health = self.health
		self.direction = 1
		self.vel_y = 0 #y - velocity
		self.jump = False
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		
		self.action = 0
		self.update_time = pygame.time.get_ticks()

		#ai specific vars
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20) #x,y,width,height
		self.idling = False
		self.idling_counter = 0
		
		#load all images for the players
				             #0      1     2        3
		animation_types = ['idle', 'run','jump', 'death']
		for animation in animation_types:
			#reset temporary list of images
			temp_list = []
			#count number of files in the folder
			num_of_frames = len(os.listdir(f'assets/img/character/{self.soldier_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'assets/img/character/{self.soldier_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect() 
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1

	def move(self, moving_left, moving_right):
		#reset movement vars
		screen_scroll = 0
		dx = 0
		dy = 0

		# assign movement vars if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1

		#jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -15 #jump up
			self.jump = False
			self.in_air = True

		#apply gravity
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#check for collision
		for tile in world.obstacle_list:
			#check collision in the x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#if the ai  has hit a wall then make it turn aroound
				if self.soldier_type == ENEMY_NAME:
					self.direction *= -1
					self.move_counter = 0
			# check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# check if below the ground, i.e. jumping
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		#check for collision with water
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		#check for collision with exit
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		#check if fallen off the map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0

		#check if going off the edges of the screen
		if self.soldier_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0

		# update rectangle position
		self.rect.x += dx
		self.rect.y += dy

		#update scroll based on player position
		if self.soldier_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)) :
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll, level_complete

	def shooting(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1
			shoot_fx.play()

	def control_ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1, 150) == 1:
				self.update_action(0) #0: idle
				self.idling = True
				self.idling_counter = 50
			#check ai near player
			if self.vision.colliderect(player.rect):
				#stop run & face player
				self.update_action(0) #0: idle
				self.shooting()
			else:
				if not self.idling:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1) #1: run
					self.move_counter += 1
					#update ai vision as the enemy moves
					self.vision.center = (self.rect.centerx + 200 * self.direction, self.rect.centery)
					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1 
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False

		#scroll
		self.rect.x += screen_scroll
		

	def update_animation(self):
		#update animation
		ANIMATION_COOLDOWN = 100
		
		#update img depending on current ftrame
		self.image = self.animation_list[self.action][self.frame_index]
		
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#if the animation has run out the reset back to the start
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:
				self.frame_index = 0

	def update_action(self, new_action):
    	# check if the new action is different to the previous one
    		if new_action != self.action:
        		self.action = new_action
        		#update the animation settings
        		self.frame_index = 0
        		self.update_time = pygame.time.get_ticks()			
	
	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Special(pygame.sprite.Sprite):
    # this class is responsible for the animated entities such as Dogs , crows , chests
    def __init__(self, entity_type, x, y, scale):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.entity_type = entity_type
        self.frame_index = 0
        self.health = 10
        self.alive = True
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        # Loading all images for animations
        animation_types = ['Idle', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in folder
            frame_numbers = len(os.listdir(f'assets/img/live_entity/{entity_type}/{animation}'))
            for i in range(frame_numbers):
                img = pygame.image.load(f'assets/img/live_entity/{entity_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update(self):
        self.update_animation()
        self.check_being_alive()
        self.rect.x += screen_scroll

        if self.rect.colliderect(player):
            if self.alive:
                self.health -= 25
                damage_text = DamageText(self.rect.centerx,
                                         self.rect.centery, str(" speed has been increased "), SKYBLUE)
                damage_text_group.add(damage_text)
                if player.alive:
                    player.speed += 2

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # update imaged based on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation list ended, back to start of the list
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 1:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def check_being_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(1)  # Entity Death animation

    def draw(self):
        screen.blit(self.image, self.rect)

class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		# How long is the level
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)	
					elif tile == 15: #create player
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.9, 6, 20, 5) #scale,speed,ammo,grenades
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16: #create enemy
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 2, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17: #create ammo
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18: #create grenade
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19: #create health
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20: #create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
					elif tile == 21: #create enemy 2
						enemy = Soldier('enemy_two', x * TILE_SIZE, y * TILE_SIZE, 2, 3, 20, 0)
						enemy_group.add(enemy)
					elif tile == 27:  # create bird
						bird = Special('crow', x * TILE_SIZE + 20, y * TILE_SIZE + 13, 2)
						live_entity_group.add(bird)
					elif tile == 28:  # create dog
						dog = Special('dog', x * TILE_SIZE + 30, y * TILE_SIZE + 7, 1.5)
						live_entity_group.add(dog)
					elif tile == 29:  # create chest
						chest = Special('chest', x * TILE_SIZE + 30, y * TILE_SIZE + 12, 2)
						live_entity_group.add(chest)

		return player, health_bar

	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll	

class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll		

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img 
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll		

class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		#scroll
		self.rect.x += screen_scroll	
		#check if player pick up box
		if pygame.sprite.collide_rect(self, player):
			# check the box type
			if self.item_type == 'Health':
				player.health += 25
				damage_text = DamageText(self.rect.centerx, self.rect.centery, f"Health +25", WHITE)
				damage_text_group.add(damage_text)
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.ammo += 15
				damage_text = DamageText(self.rect.centerx,self.rect.centery, f"Ammo +15", WHITE)
				damage_text_group.add(damage_text)
			elif self.item_type == 'Grenade':
				damage_text = DamageText(self.rect.centerx,self.rect.centery, f"Grenade +3", WHITE)
				damage_text_group.add(damage_text)
				player.grenades += 3
			#delete boxes
			self.kill()


class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health

		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) + screen_scroll
		
		#check if bellet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()  # del bullet

		#check for collison with level
			# check collision with environment
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()
		#check collision with character
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					if enemy.health >= 0:
						damage_text = DamageText(enemy.rect.centerx, enemy.rect.centery, str(enemy.health), WHITE)
						damage_text_group.add(damage_text)
					self.kill()
		for live_entity in live_entity_group:
			if live_entity.entity_type != "chest":
				if pygame.sprite.spritecollide(live_entity, bullet_group, False):
					if live_entity.alive:
						live_entity.health = -25
						damage_text = DamageText(live_entity.rect.centerx,
						live_entity.rect.centery, str("Y U SHOOT BRO! HAHAHAHAH"), RED)
						damage_text_group.add(damage_text)
						if player.alive:
							player.health -= 50
							self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#check for the collisoin with level
		for tile in world.obstacle_list:
			#check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			# check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				# check if below the ground, i.e. throwing
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				# check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom

		#update grenade position
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			#do dmg to anyone that is nearby
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50
					if enemy.health >= 0:
						damage_text = DamageText(enemy.rect.centerx, enemy.rect.centery, str(enemy.health), WHITE)
						damage_text_group.add(damage_text)
			for live_entity in live_entity_group:
				if live_entity.entity_type != "chest":
					if abs(self.rect.centerx - live_entity.rect.centerx) < TILE_SIZE * 2 and \
						abs(self.rect.centery - live_entity.rect.centery) < TILE_SIZE * 2:
						if live_entity.alive:
							live_entity.health = -25
							damage_text = DamageText(live_entity.rect.centerx, live_entity.rect.centery, str("LOL NOOB"), RED)
							damage_text_group.add(damage_text)
							if player.alive:
								player.health -= 50
								self.kill()

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.explosion_images = []
		for num in range(1, 6):
			img = pygame.image.load(f'assets/img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.explosion_images.append(img)
		self.frame_index = 0
		self.image = self.explosion_images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0

	def update(self):
		#scroll
		self.rect.x += screen_scroll
		EXPLOSION_SPEED = 4
		#update explosion animation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			# if the animation has been completed then delete explosion
			if self.frame_index >= len(self.explosion_images):
				self.kill()
			else:
				self.image = self.explosion_images[self.frame_index]

class ScreenFade():
	def __init__(self, direction, color, speed):
		self.direction = direction
		self.color = color
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1: #whole screen fade
			pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2: #vertical screen fade down
			pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete


#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, YELLOW, 10)

#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 -130, SCREEN_HEIGHT // 2 - 120, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 -110, SCREEN_HEIGHT // 2 - 10, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 -100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#create sprite groups
damage_text_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
live_entity_group = pygame.sprite.Group()

#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#load in the level data & create world
with open(f'level{level}_data.csv', newline = '') as csvfile:
	reader = csv.reader(csvfile, delimiter = ',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)


run = True
while run:

	clock.tick(FPS)

	# menu
	if start_game == False:
		#main menu
		#screen.fill(BG)
		screen.blit(intro_bg,(0, 0)) 
		#add button
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			run = False
	else:
		total_time += 1
		#update bg
		draw_bg()
		#draw world map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		
		#show ammo
		draw_text(f'AMMO : {player.ammo}', font, BLACK, 10, 40)
		#show grenades
		draw_text(f'GRENADE : {player.grenades}', font, BLACK, 10, 60)
		draw_lvl_info_text(f'Mission {level}', font, WHITE, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2)
		draw_lvl_info_text(f'{MISSIONS[level]}', font, WHITE, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 30)
		
		player.update()
		player.draw()
		
		for enemy in enemy_group:
			enemy.control_ai()
			enemy.update()
			enemy.draw()

		#update & draw groups
		damage_text_group.update()
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		live_entity_group.update()

		# draw damage text
		damage_text_group.draw(screen)
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)
		live_entity_group.draw(screen)


		#show intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0

		#update player actions
		if player.alive:
			#shoot bullets
			if shoot:
				player.shooting()
			#throw grenade
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(grenade)
				#reduce grernades
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: ldle
			screen_scroll, level_complete = player.move(moving_left,moving_right)

			bg_scroll -= screen_scroll
			#check if player has completed the level
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					#load in the level data & create world
					with open(f'level{level}_data.csv', newline = '') as csvfile:
						reader = csv.reader(csvfile, delimiter = ',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)
				else:
					level = 1

		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					#load in the level data & create world
					with open(f'level{level}_data.csv', newline = '') as csvfile:
						reader = csv.reader(csvfile, delimiter = ',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		#quit
		if event.type == pygame.QUIT:
			run = False
		#keyboard press
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_g:
				grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False
		#keyboard released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_g:
				grenade = False
				grenade_thrown = False

	pygame.display.update()

pygame.quit()