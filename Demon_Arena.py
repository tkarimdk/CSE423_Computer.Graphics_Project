# Imports
import math
import time
import random
import os
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Display Settings
WINDOW_W = 1000
WINDOW_H = 800
HUD_W = 1000
HUD_H = 800


MINIMAP_W = 240
MINIMAP_MARGIN = 20
MINIMAP_BG_ALPHA = 0.78

# Game State
player_pos = [150.0, 150.0, 50.0]
player_angle = 45.0
aim_pitch = 0.0
camera_mode = 1
player_health = 100.0
invincible_until = 0.0
last_player_hit_time = 0.0
cheat_mode = False
game_state = 'menu'
player_walk_cycle = 0.0
player_is_moving = False

keys = {'w': False, 'a': False, 's': False, 'd': False}
special_keys = {'left': False, 'right': False, 'up': False, 'down': False}

# Weapon Settings
guns = ['Pistol', 'Rifle', 'Rocket Launcher']
current_gun = 0
last_shot_time = 0.0


ammo = [7, 2, 1]
max_ammo = [7, 2, 1]
reload_time = [1.2, 1.5, 2.0]
is_reloading = False
reload_start_time = 0.0
no_reload_until = 0.0

# Object Lists
enemies = []
projectiles = []
powerups = []
explosions = []

# Enemy Difficulty
kill_count = 0
enemy_level = 1
MAX_ENEMIES = 5

LEVEL_DATA = {
    1: {'speed': 90.0, 'health': 80},
    2: {'speed': 150.0, 'health': 110},
    3: {'speed': 290.0, 'health': 140}
}

# Demon Types
DEMON_TYPES = {
    'normal': {
        'label': 'Normal Demon',
        'speed_mult': 1.0,
        'health_mult': 1.0,
        'touch_damage': 20.0,
        'hit_radius': 28.0,
        'contact_radius': 30.0,
        'spawn_weight': 0.55
    },
    'flying': {
        'label': 'Flying Demon',
        'speed_mult': 1.18,
        'health_mult': 0.75,
        'touch_damage': 14.0,
        'hit_radius': 30.0,
        'contact_radius': 34.0,
        'spawn_weight': 0.28
    },
    'bulky': {
        'label': 'Bulky Demon',
        'speed_mult': 0.58,
        'health_mult': 1.85,
        'touch_damage': 32.0,
        'hit_radius': 40.0,
        'contact_radius': 44.0,
        'spawn_weight': 0.17
    }
}

# Damage Settings
GUN_DAMAGE = {
    'Pistol': {'body': 40, 'head': 80},
    'Rifle': {'body': 80, 'head': 130},
    'Rocket Launcher': {'body': 250, 'head': 250}
}

ROCKET_RADIUS = 150.0

# Map Layout
game_map = [
    "WWWWWWWWWWWWWWWWWWWWWWWW",
    "W......................W",
    "W..WWWW..WWWW..WWWW....W",
    "W..W.........W.........W",
    "W..W..WWWW...W..WWWW...W",
    "W.....W......W......W..W",
    "WWW...W..WWWWW..WW..W..W",
    "W......................W",
    "W..WW..WWWWW..W...WWW..W",
    "W..W......W......W.....W",
    "W..W..WW..W..WWWWW..W..W",
    "W.....WW.....W......W..W",
    "W..WWWWWW..WWW..WW.....W",
    "W......................W",
    "WWWWWWWWWWWWWWWWWWWWWWWW"
]
BLOCK_SIZE = 100
walls = []
for row in range(len(game_map)):
    for col in range(len(game_map[0])):
        if game_map[row][col] == 'W':
            walls.append((col * BLOCK_SIZE, row * BLOCK_SIZE))

# Utility Functions
def check_collision(x, y, radius):
    for wx, wy in walls:
        if abs(x - wx) < BLOCK_SIZE/2 + radius and abs(y - wy) < BLOCK_SIZE/2 + radius:
            return True
    return False

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, HUD_W, 0, HUD_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def get_text_width(text, font=GLUT_BITMAP_HELVETICA_18):
    width = 0
    for ch in text:
        width += glutBitmapWidth(font, ord(ch))
    return width


def draw_text_color(x, y, text, r=1.0, g=1.0, b=1.0, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(r, g, b)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, HUD_W, 0, HUD_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_text_centered(cx, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1.0, 1.0, 1.0)):
    width = get_text_width(text, font)
    draw_text_color(cx - width / 2.0, y, text, color[0], color[1], color[2], font)

# Map Rendering
def draw_map():

    world_w = len(game_map[0]) * BLOCK_SIZE
    world_h = len(game_map) * BLOCK_SIZE
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.1, 0.15)
    glVertex3f(-BLOCK_SIZE, -BLOCK_SIZE, 0)
    glVertex3f(world_w, -BLOCK_SIZE, 0)
    glVertex3f(world_w, world_h, 0)
    glVertex3f(-BLOCK_SIZE, world_h, 0)
    glEnd()


    for wx, wy in walls:
        glPushMatrix()
        glTranslatef(wx, wy, BLOCK_SIZE / 2)
        glColor3f(0.5, 0.2, 0.2)
        glutSolidCube(BLOCK_SIZE)
        glPopMatrix()

# Enemy Rendering
def draw_enemy_health_bar(enemy):
    ex, ey, ez = enemy['pos']
    hp = enemy.get('health', 1)
    max_hp = enemy.get('max_health', hp)
    ratio = max(0.0, min(1.0, hp / max_hp))

    dtype = enemy.get('type', 'normal')
    scale = 1.35 if dtype == 'bulky' else 0.92 if dtype == 'flying' else 1.0
    bar_z = ez + (64 * scale if dtype == 'bulky' else 55 if dtype == 'flying' else 38)


    px, py, _ = player_pos
    face_angle = math.degrees(math.atan2(py - ey, px - ex))

    glPushMatrix()
    glTranslatef(ex, ey, bar_z)
    glRotatef(face_angle - 90, 0, 0, 1)


    glColor3f(0.05, 0.05, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(-24, 0, -4)
    glVertex3f(24, 0, -4)
    glVertex3f(24, 0, 4)
    glVertex3f(-24, 0, 4)
    glEnd()

    if ratio > 0.5:
        glColor3f(0.0, 0.9, 0.1)
    elif ratio > 0.25:
        glColor3f(1.0, 0.6, 0.0)
    else:
        glColor3f(1.0, 0.0, 0.0)

    fill = 48 * ratio
    glBegin(GL_QUADS)
    glVertex3f(-24, 0.5, -3)
    glVertex3f(-24 + fill, 0.5, -3)
    glVertex3f(-24 + fill, 0.5, 3)
    glVertex3f(-24, 0.5, 3)
    glEnd()

    glPopMatrix()


def draw_demon_wings(is_hit):

    if is_hit:
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3f(0.18, 0.02, 0.22)

    glBegin(GL_TRIANGLES)

    glVertex3f(-9, -2, 35)
    glVertex3f(-48, -8, 58)
    glVertex3f(-35, -5, 15)

    glVertex3f(9, -2, 35)
    glVertex3f(48, -8, 58)
    glVertex3f(35, -5, 15)
    glEnd()


    glColor3f(0.03, 0.03, 0.03)
    glBegin(GL_LINES)
    glVertex3f(-10, -1, 35); glVertex3f(-48, -8, 58)
    glVertex3f(-10, -1, 35); glVertex3f(-35, -5, 15)
    glVertex3f(10, -1, 35); glVertex3f(48, -8, 58)
    glVertex3f(10, -1, 35); glVertex3f(35, -5, 15)
    glEnd()


def draw_enemies():
    px, py, _ = player_pos
    for enemy in enemies:
        ex, ey, ez = enemy['pos']
        level = enemy.get('level', 1)
        dtype = enemy.get('type', 'normal')


        angle = math.degrees(math.atan2(py - ey, px - ex))
        is_hit = (time.time() - enemy.get('last_hit_time', 0.0)) < 0.1

        def set_color(r, g, b):
            if is_hit:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(r, g, b)


        if dtype == 'bulky':
            body_scale = 1.52
            z_offset = -22
            torso_color = (0.34, 0.03, 0.03)
            head_color = (0.58, 0.05, 0.05)
            limb_color = (0.24, 0.02, 0.02)
            armor_color = (0.22, 0.22, 0.24)
            eye_color = (1.0, 0.28, 0.02)
        elif dtype == 'flying':
            body_scale = 0.88
            z_offset = -8
            torso_color = (0.36, 0.0, 0.55)
            head_color = (0.55, 0.0, 0.75)
            limb_color = (0.25, 0.0, 0.42)
            eye_color = (0.1, 0.95, 1.0)
            armor_color = (0.18, 0.10, 0.25)
        else:
            body_scale = 1.0
            z_offset = -25
            if level == 1:
                torso_color = (0.65, 0.0, 0.0)
                head_color = (0.85, 0.0, 0.0)
                eye_color = (1.0, 1.0, 0.0)
            elif level == 2:
                torso_color = (0.85, 0.12, 0.0)
                head_color = (1.0, 0.18, 0.0)
                eye_color = (1.0, 0.45, 0.0)
            else:
                torso_color = (0.18, 0.0, 0.24)
                head_color = (0.08, 0.0, 0.12)
                eye_color = (0.0, 0.0, 0.0)
            limb_color = (0.45, 0.0, 0.0)
            armor_color = (0.18, 0.02, 0.02)

        glPushMatrix()
        glTranslatef(ex, ey, ez + z_offset)
        glRotatef(angle - 90, 0, 0, 1)
        glScalef(body_scale, body_scale, body_scale)

        if dtype == 'flying':
            draw_demon_wings(is_hit)


        set_color(*torso_color)
        glPushMatrix()
        glTranslatef(0, 0, 20)
        if dtype == 'bulky':
            glScalef(1.46, 0.92, 1.95)
        elif dtype == 'flying':
            glScalef(0.9, 0.48, 1.35)
        else:
            glScalef(1.05, 0.55, 1.6)
        glutSolidCube(20)
        glPopMatrix()


        if dtype == 'bulky':

            glColor3f(*armor_color)
            glPushMatrix()
            glTranslatef(0, 10, 24)
            glScalef(0.95, 0.26, 0.95)
            glutSolidCube(22)
            glPopMatrix()


            for sx in (-19, 19):
                glPushMatrix()
                glTranslatef(sx, 4, 34)
                glRotatef(-18 if sx < 0 else 18, 0, 0, 1)
                glScalef(0.48, 0.58, 0.48)
                glutSolidCube(20)
                glPopMatrix()


            set_color(0.95, 0.18, 0.02)
            glPushMatrix()
            glTranslatef(0, 12, 24)
            glutSolidSphere(4.8, 12, 12)
            glPopMatrix()


            glColor3f(0.04, 0.04, 0.04)
            for sx, sz in ((-10, 38), (0, 42), (10, 38)):
                glPushMatrix()
                glTranslatef(sx, -10, sz)
                glRotatef(180, 1, 0, 0)
                glutSolidCone(3.0, 12.0, 10, 10)
                glPopMatrix()


        set_color(*head_color)
        glPushMatrix()
        glTranslatef(0, 0, 42)
        head_size = 12 if dtype == 'bulky' else 9 if dtype == 'flying' else 10
        glutSolidSphere(head_size, 10, 10)
        glPopMatrix()

        if dtype == 'bulky':

            glColor3f(*armor_color)
            glPushMatrix()
            glTranslatef(0, 9, 37)
            glScalef(0.72, 0.28, 0.34)
            glutSolidCube(18)
            glPopMatrix()


        if is_hit:
            glColor3f(1.0, 0.0, 0.0)
        else:
            glColor3f(*eye_color)
        eye_y = 9 if dtype == 'bulky' else 8
        eye_size = 2.9 if dtype == 'bulky' else 2.4
        eye_x = 5 if dtype == 'bulky' else 4
        glPushMatrix()
        glTranslatef(eye_x, eye_y, 44)
        glutSolidSphere(eye_size, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-eye_x, eye_y, 44)
        glutSolidSphere(eye_size, 10, 10)
        glPopMatrix()


        set_color(0.03, 0.03, 0.03)
        horn_h = 26 if dtype == 'bulky' else 17 if dtype == 'flying' else 15
        horn_r = 4.0 if dtype == 'bulky' else 2.5
        horn_x = 7 if dtype == 'bulky' else 5
        horn_z = 52 if dtype == 'bulky' else 49
        glPushMatrix()
        glTranslatef(horn_x, 0, horn_z)
        glRotatef(-28 if dtype == 'bulky' else -35, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(horn_r, horn_h, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-horn_x, 0, horn_z)
        glRotatef(28 if dtype == 'bulky' else 35, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(horn_r, horn_h, 10, 10)
        glPopMatrix()


        set_color(*limb_color)
        arm_x = 17 if dtype == 'bulky' else 12
        arm_scale = 1.72 if dtype == 'bulky' else 1.25
        arm_w = 0.44 if dtype == 'bulky' else 0.32
        glPushMatrix()
        glTranslatef(-arm_x, 3, 27)
        glRotatef(-18, 1, 0, 0)
        glScalef(arm_w, arm_w, arm_scale)
        glutSolidCube(15)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(arm_x, 3, 27)
        glRotatef(-18, 1, 0, 0)
        glScalef(arm_w, arm_w, arm_scale)
        glutSolidCube(15)
        glPopMatrix()

        if dtype == 'bulky':
            glColor3f(*armor_color)

            for sx in (-17, 17):
                glPushMatrix()
                glTranslatef(sx, 6, 14)
                glScalef(0.42, 0.42, 0.52)
                glutSolidCube(16)
                glPopMatrix()

            glColor3f(0.06, 0.06, 0.06)
            for sx in (-17, 17):
                for sy in (4, 8):
                    glPushMatrix()
                    glTranslatef(sx, sy, 14)
                    glRotatef(-90, 1, 0, 0)
                    glutSolidCone(1.8, 6.0, 8, 8)
                    glPopMatrix()


        set_color(*limb_color)
        leg_scale_z = 2.2 if dtype == 'bulky' else 1.15 if dtype == 'flying' else 1.8
        leg_width = 0.60 if dtype == 'bulky' else 0.34 if dtype == 'flying' else 0.42
        leg_z = -10 if dtype == 'bulky' else 0 if dtype == 'flying' else -5
        leg_x = 7 if dtype == 'bulky' else 6

        glPushMatrix()
        glTranslatef(-leg_x, 0, leg_z)
        glScalef(leg_width, leg_width, leg_scale_z)
        glutSolidCube(15)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(leg_x, 0, leg_z)
        glScalef(leg_width, leg_width, leg_scale_z)
        glutSolidCube(15)
        glPopMatrix()

        if dtype == 'bulky':
            glColor3f(*armor_color)
            for sx in (-7, 7):
                glPushMatrix()
                glTranslatef(sx, 6, -23)
                glScalef(0.60, 0.82, 0.22)
                glutSolidCube(16)
                glPopMatrix()
        glPopMatrix()
        draw_enemy_health_bar(enemy)

# Projectile and Powerup Rendering
def draw_projectiles():
    for proj in projectiles:
        px, py, pz = proj['pos']
        glPushMatrix()
        glTranslatef(px, py, pz)
        if proj['type'] == 'Rocket Launcher':
            glColor3f(1, 0.5, 0)
            gluSphere(gluNewQuadric(), 8, 10, 10)
        else:
            glColor3f(1, 1, 0)
            gluSphere(gluNewQuadric(), 3, 10, 10)
        glPopMatrix()

def draw_powerups():
    for pup in powerups:
        px, py, pz = pup['pos']
        glPushMatrix()
        glTranslatef(px, py, pz)
        glRotatef(pup.get('angle', 0.0), 0, 0, 1)
        scale = pup.get('scale', 1.0)
        glScalef(scale, scale, scale)


        if pup.get('type') == 'invincibility':
            glColor3f(0, 1, 1)
        elif pup.get('type') == 'noreload':
            glColor3f(1, 0, 0)
        else:
            glColor3f(0, 1, 0)

        gluSphere(gluNewQuadric(), 18, 16, 16)
        glPopMatrix()

def draw_pixel_rect(x, y, w, h, r, g, b):
    glColor3f(r, g, b)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)

# Weapon Rendering
def draw_3d_gun():
    recoil_offset = 0
    now = time.time()
    time_since_shot = now - last_shot_time
    if time_since_shot < 0.1:
        recoil_offset = -3.0

    reload_offset = 0.0
    if is_reloading:
        reload_offset = math.sin(time.time() * 12.0) * 5.0

    if current_gun == 0:
        glColor3f(0.4, 0.4, 0.4)
        glPushMatrix()
        glTranslatef(0, recoil_offset + reload_offset, 0)

        glPushMatrix()
        glTranslatef(0, 5, 2)
        glScalef(0.2, 1.0, 0.3)
        glutSolidCube(10)
        glPopMatrix()

        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(0, 1, -2)
        glRotatef(20, 1, 0, 0)
        glScalef(0.2, 0.4, 0.6)
        glutSolidCube(10)
        glPopMatrix()

        if time_since_shot < 0.05:
            glColor3f(1.0, 0.8, 0.0)
            glPushMatrix()
            glTranslatef(0, 11, 2)
            glutSolidSphere(2, 10, 10)
            glPopMatrix()

        glPopMatrix()

    elif current_gun == 1:
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0, recoil_offset + reload_offset, 0)

        glPushMatrix()
        glTranslatef(0, 8, 2)
        glScalef(0.2, 2.0, 0.3)
        glutSolidCube(10)
        glPopMatrix()

        glColor3f(0.4, 0.2, 0.1)
        glPushMatrix()
        glTranslatef(0, -2, 2)
        glScalef(0.2, 0.8, 0.4)
        glutSolidCube(10)
        glPopMatrix()

        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 3, 0)
        glScalef(0.2, 0.4, 0.5)
        glutSolidCube(10)
        glPopMatrix()

        if time_since_shot < 0.05:
            glColor3f(1.0, 0.8, 0.0)
            glPushMatrix()
            glTranslatef(0, 19, 2)
            glutSolidSphere(2.5, 10, 10)
            glPopMatrix()

        glPopMatrix()

    elif current_gun == 2:
        glColor3f(0.3, 0.4, 0.2)
        glPushMatrix()
        glTranslatef(0, recoil_offset + reload_offset, 0)

        glPushMatrix()
        glTranslatef(0, 6, 2)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 3, 16, 10, 10)
        glPopMatrix()

        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, -2, 2)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 4, 8, 10, 10)
        glPopMatrix()

        if time_since_shot < 0.1:
            glColor3f(1.0, 0.5, 0.0)
            glPushMatrix()
            glTranslatef(0, 16, 2)
            glutSolidSphere(4, 10, 10)
            glPopMatrix()

        glPopMatrix()

def draw_circle_2d(cx, cy, radius, segments=64):
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        glVertex2f(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
    glEnd()


def draw_line_2d(x1, y1, x2, y2):
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

# HUD Rendering
def draw_hud_crosshair():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, HUD_W, 0, HUD_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    cx, cy = HUD_W // 2, HUD_H // 2


    if current_gun == 0:
        glBegin(GL_QUADS)
        draw_pixel_rect(cx - 5, cy + 12, 10, 28, 0, 1, 0)
        draw_pixel_rect(cx - 5, cy - 40, 10, 28, 0, 1, 0)
        draw_pixel_rect(cx - 40, cy - 5, 28, 10, 0, 1, 0)
        draw_pixel_rect(cx + 12, cy - 5, 28, 10, 0, 1, 0)
        glEnd()


    elif current_gun == 1:
        r = 260
        glColor3f(0, 0, 0)


        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(cx - r, 0); glVertex2f(cx - r, HUD_H); glVertex2f(0, HUD_H)
        glVertex2f(cx + r, 0); glVertex2f(HUD_W, 0); glVertex2f(HUD_W, HUD_H); glVertex2f(cx + r, HUD_H)
        glVertex2f(cx - r, cy + r); glVertex2f(cx + r, cy + r); glVertex2f(cx + r, HUD_H); glVertex2f(cx - r, HUD_H)
        glVertex2f(cx - r, 0); glVertex2f(cx + r, 0); glVertex2f(cx + r, cy - r); glVertex2f(cx - r, cy - r)
        glEnd()


        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        lastx = None
        lasty = None
        for i in range(121):
            t = 2 * math.pi * i / 120.0
            x = cx + r * math.cos(t)
            y = cy + r * math.sin(t)
            if lastx is not None:
                glVertex2f(lastx, lasty)
                glVertex2f(x, y)
            lastx, lasty = x, y
        glEnd()


        glBegin(GL_LINES)
        glVertex2f(cx - r, cy); glVertex2f(cx + r, cy)
        glVertex2f(cx, cy - r); glVertex2f(cx, cy + r)
        glEnd()


        glColor3f(1, 0, 0)
        glBegin(GL_QUADS)
        draw_pixel_rect(cx - 3, cy - 3, 6, 6, 1, 0, 0)
        glEnd()


    else:
        glColor3f(1, 0.5, 0)
        draw_circle_2d(cx, cy, 95)
        draw_circle_2d(cx, cy, 45)
        draw_line_2d(cx - 130, cy, cx - 100, cy)
        draw_line_2d(cx + 100, cy, cx + 130, cy)
        draw_line_2d(cx, cy - 130, cx, cy - 100)
        draw_line_2d(cx, cy + 100, cx, cy + 130)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# Player Rendering
def draw_player_and_weapon():
    px, py, pz = player_pos
    walk_swing = math.sin(player_walk_cycle) if player_is_moving else 0.0
    walk_swing_opposite = math.sin(player_walk_cycle + math.pi) if player_is_moving else 0.0
    body_bob = abs(math.sin(player_walk_cycle * 0.5)) * 1.8 if player_is_moving else 0.0

    glPushMatrix()
    glTranslatef(px, py, pz - 25 + body_bob)
    glRotatef(player_angle - 90, 0, 0, 1)

    if camera_mode == 3:

        glColor3f(0.0, 0.5, 0.2)
        glPushMatrix()
        glTranslatef(0, 0, 20)
        glScalef(1.0, 0.5, 1.5)
        glutSolidCube(20)
        glPopMatrix()


        glColor3f(0.9, 0.7, 0.6)
        glPushMatrix()
        glTranslatef(0, 0, 42)
        glutSolidSphere(8, 10, 10)
        glPopMatrix()


        glColor3f(0.0, 0.8, 1.0)
        glPushMatrix()
        glTranslatef(0, 4, 42)
        glScalef(1.0, 0.5, 0.3)
        glutSolidCube(10)
        glPopMatrix()


        glColor3f(0.0, 0.4, 0.1)
        glPushMatrix()
        glTranslatef(11, 5, 31)
        glRotatef(-18 + walk_swing * 20.0, 1, 0, 0)
        glTranslatef(0, 0, -4)
        glScalef(0.32, 0.32, 1.25)
        glutSolidCube(15)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-11, 5, 31)
        glRotatef(-18 + walk_swing_opposite * 20.0, 1, 0, 0)
        glTranslatef(0, 0, -4)
        glScalef(0.32, 0.32, 1.25)
        glutSolidCube(15)
        glPopMatrix()


        glColor3f(0.2, 0.2, 0.2)
        glPushMatrix()
        glTranslatef(-6, 0, 13)
        glRotatef(walk_swing * 28.0, 1, 0, 0)
        glTranslatef(0, 0, -8)
        glScalef(0.4, 0.4, 1.22)
        glutSolidCube(15)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(6, 0, 13)
        glRotatef(walk_swing_opposite * 28.0, 1, 0, 0)
        glTranslatef(0, 0, -8)
        glScalef(0.4, 0.4, 1.22)
        glutSolidCube(15)
        glPopMatrix()


        glTranslatef(10, 18, 25)
        glRotatef(aim_pitch, 1, 0, 0)
        if current_gun == 1:
            glScalef(1.25, 1.25, 1.25)
        elif current_gun == 2:
            glScalef(1.45, 1.45, 1.45)
    else:
        glClear(GL_DEPTH_BUFFER_BIT)
        weapon_bob_y = abs(math.sin(player_walk_cycle * 0.5)) * 1.6 if player_is_moving else 0.0
        weapon_bob_x = math.sin(player_walk_cycle) * 0.9 if player_is_moving else 0.0
        glTranslatef(5 + weapon_bob_x, 7 + weapon_bob_y, 32)
        glRotatef(aim_pitch, 1, 0, 0)
        if current_gun == 1:
            glTranslatef(0, 1, 0)
        elif current_gun == 2:
            glTranslatef(0, 2, -1)
            glScalef(1.25, 1.25, 1.25)


    if not (camera_mode == 1 and current_gun == 1):
        draw_3d_gun()

    glPopMatrix()

# Effects and Minimap Rendering
def draw_explosions():
    now = time.time()
    for exp in explosions:
        age = now - exp['time_created']
        progress = age / exp['duration']
        if progress < 1.0:
            glPushMatrix()
            glTranslatef(*exp['pos'])

            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            alpha = 1.0 - progress
            radius = exp['max_radius'] * progress

            if progress < 0.2:
                glColor4f(1.0, 1.0, 1.0, alpha)
            elif progress < 0.5:
                glColor4f(1.0, 1.0, 0.0, alpha)
            elif progress < 0.8:
                glColor4f(1.0, 0.5, 0.0, alpha)
            else:
                glColor4f(1.0, 0.0, 0.0, alpha)

            glutSolidSphere(radius, 20, 20)

            glDisable(GL_BLEND)
            glPopMatrix()

def draw_player_health_bar():
    hp = max(0.0, min(100.0, player_health))
    width = 300.0 * (hp / 100.0)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, HUD_W, 0, HUD_H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(10, 650)
    glVertex2f(310, 650)
    glVertex2f(310, 670)
    glVertex2f(10, 670)
    glEnd()

    if hp > 50:
        glColor3f(0.0, 0.8, 0.1)
    elif hp > 25:
        glColor3f(1.0, 0.6, 0.0)
    else:
        glColor3f(1.0, 0.0, 0.0)

    glBegin(GL_QUADS)
    glVertex2f(10, 650)
    glVertex2f(10 + width, 650)
    glVertex2f(10 + width, 670)
    glVertex2f(10, 670)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_filled_rect_2d(x, y, w, h, r, g, b, a=1.0):

    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def draw_small_square_2d(cx, cy, size, r, g, b, a=1.0):

    half = size / 2.0
    draw_filled_rect_2d(cx - half, cy - half, size, size, r, g, b, a)


def world_to_minimap(wx, wy, map_x, map_y, map_w, map_h):


    world_w = len(game_map[0]) * BLOCK_SIZE
    world_h = len(game_map) * BLOCK_SIZE

    mx = map_x + ((wx + BLOCK_SIZE / 2) / world_w) * map_w
    my = map_y + ((wy + BLOCK_SIZE / 2) / world_h) * map_h


    mx = max(map_x, min(map_x + map_w, mx))
    my = max(map_y, min(map_y + map_h, my))
    return mx, my


def draw_minimap():

    world_cols = len(game_map[0])
    world_rows = len(game_map)

    map_w = MINIMAP_W
    map_h = MINIMAP_W * (world_rows / world_cols)
    map_x = HUD_W - MINIMAP_MARGIN - map_w
    map_y = HUD_H - MINIMAP_MARGIN - map_h

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, HUD_W, 0, HUD_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    draw_filled_rect_2d(
        map_x - 8,
        map_y - 8,
        map_w + 16,
        map_h + 16,
        0.02,
        0.04,
        0.08,
        MINIMAP_BG_ALPHA,
    )


    draw_filled_rect_2d(map_x, map_y, map_w, map_h, 0.07, 0.08, 0.12, 0.95)

    cell_w = map_w / world_cols
    cell_h = map_h / world_rows


    for row in range(world_rows):
        for col in range(world_cols):
            if game_map[row][col] == 'W':
                x = map_x + col * cell_w
                y = map_y + row * cell_h
                draw_filled_rect_2d(x, y, cell_w, cell_h, 0.45, 0.14, 0.14, 1.0)


    glColor3f(0.2, 0.85, 1.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(map_x, map_y)
    glVertex2f(map_x + map_w, map_y)
    glVertex2f(map_x + map_w, map_y + map_h)
    glVertex2f(map_x, map_y + map_h)
    glEnd()


    for pup in powerups:
        px, py, _ = pup['pos']
        mx, my = world_to_minimap(px, py, map_x, map_y, map_w, map_h)
        if pup.get('type') == 'invincibility':
            draw_small_square_2d(mx, my, 6, 0.0, 1.0, 1.0, 1.0)
        elif pup.get('type') == 'noreload':
            draw_small_square_2d(mx, my, 6, 1.0, 0.0, 0.0, 1.0)
        else:
            draw_small_square_2d(mx, my, 6, 0.0, 1.0, 0.0, 1.0)


    for enemy in enemies:
        ex, ey, _ = enemy['pos']
        mx, my = world_to_minimap(ex, ey, map_x, map_y, map_w, map_h)
        if enemy.get('type') == 'flying':
            draw_small_square_2d(mx, my, 7, 0.75, 0.1, 1.0, 1.0)
        elif enemy.get('type') == 'bulky':
            draw_small_square_2d(mx, my, 9, 1.0, 0.45, 0.05, 1.0)
        else:
            draw_small_square_2d(mx, my, 7, 1.0, 0.05, 0.05, 1.0)


    px, py, _ = player_pos
    mx, my = world_to_minimap(px, py, map_x, map_y, map_w, map_h)
    draw_small_square_2d(mx, my, 8, 0.0, 0.95, 1.0, 1.0)


    rad = math.radians(player_angle)
    direction_len = 18
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINES)
    glVertex2f(mx, my)
    glVertex2f(mx + math.cos(rad) * direction_len, my + math.sin(rad) * direction_len)
    glEnd()

    glDisable(GL_BLEND)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# Menu and HUD
def draw_start_screen():

    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, HUD_W, 0, HUD_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    draw_filled_rect_2d(0, 0, HUD_W, HUD_H, 0.01, 0.01, 0.03, 1.0)
    draw_filled_rect_2d(0, 0, HUD_W, 250, 0.18, 0.02, 0.02, 0.40)
    draw_filled_rect_2d(0, 520, HUD_W, 280, 0.08, 0.02, 0.12, 0.50)
    draw_filled_rect_2d(180, 110, 640, 575, 0.02, 0.03, 0.05, 0.90)
    draw_filled_rect_2d(190, 120, 620, 555, 0.05, 0.01, 0.01, 0.28)


    glColor3f(0.90, 0.16, 0.05)
    glBegin(GL_LINE_LOOP)
    glVertex2f(180, 110); glVertex2f(820, 110); glVertex2f(820, 685); glVertex2f(180, 685)
    glEnd()

    glColor3f(0.35, 0.35, 0.40)
    glBegin(GL_LINE_LOOP)
    glVertex2f(196, 126); glVertex2f(804, 126); glVertex2f(804, 669); glVertex2f(196, 669)
    glEnd()


    draw_filled_rect_2d(240, 575, 520, 68, 0.15, 0.02, 0.02, 0.95)
    glColor3f(1.0, 0.26, 0.08)
    glBegin(GL_LINE_LOOP)
    glVertex2f(240, 575); glVertex2f(760, 575); glVertex2f(760, 643); glVertex2f(240, 643)
    glEnd()


    glColor3f(0.95, 0.20, 0.04)
    glBegin(GL_TRIANGLES)
    glVertex2f(400, 648); glVertex2f(422, 682); glVertex2f(442, 648)
    glVertex2f(558, 648); glVertex2f(578, 682); glVertex2f(600, 648)
    glEnd()


    draw_filled_rect_2d(340, 390, 320, 72, 0.34, 0.03, 0.03, 0.97)
    draw_filled_rect_2d(340, 292, 320, 72, 0.09, 0.10, 0.12, 0.97)

    glColor3f(1.0, 0.30, 0.08)
    glBegin(GL_LINE_LOOP)
    glVertex2f(340, 390); glVertex2f(660, 390); glVertex2f(660, 462); glVertex2f(340, 462)
    glEnd()

    glColor3f(0.85, 0.85, 0.88)
    glBegin(GL_LINE_LOOP)
    glVertex2f(340, 292); glVertex2f(660, 292); glVertex2f(660, 364); glVertex2f(340, 364)
    glEnd()


    draw_filled_rect_2d(250, 215, 500, 44, 0.04, 0.05, 0.08, 0.88)

    glDisable(GL_BLEND)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_text_centered(500, 603, "DEMON ARENA", GLUT_BITMAP_TIMES_ROMAN_24, (1.0, 0.95, 0.95))
    draw_text_centered(500, 420, "START GAME", GLUT_BITMAP_HELVETICA_18, (1.0, 1.0, 1.0))
    draw_text_centered(500, 322, "EXIT GAME", GLUT_BITMAP_HELVETICA_18, (0.94, 0.94, 0.94))
    draw_text_centered(500, 236, "ENTER or S = Start   |   E or ESC = Exit", GLUT_BITMAP_HELVETICA_18, (0.92, 0.94, 0.98))

def draw_hud():
    if time.time() - last_player_hit_time < 0.2:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, HUD_W, 0, HUD_H)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor4f(1.0, 0.0, 0.0, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(HUD_W, 0)
        glVertex2f(HUD_W, HUD_H)
        glVertex2f(0, HUD_H)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_BLEND)

    if player_health > 0:
        draw_player_health_bar()
        draw_text(10, 770, f"Health: {int(player_health)}")
        draw_text(10, 740, f"Weapon: {guns[current_gun]}")
        draw_text(10, 710, f"Kills: {kill_count} | Enemy Level: {enemy_level}")
        draw_text(10, 680, f"Ammo: {ammo[current_gun]}/{max_ammo[current_gun]}  |  1: Pistol | 2: Rifle | 3: Rocket")
        draw_text(10, 620, "WASD: Move | Arrows: Aim | C: Camera | SPACE: Shoot | B: Reload | J: Cheat | M: Menu")
        draw_text(10, 590, "Demons: Normal = balanced | Flying = fast wings | Bulky = tank")
        if cheat_mode:
            draw_text(10, 560, "CHEAT ON: Wall Vision + One Shot + Bullets Ignore Walls")
        if is_reloading:
            draw_text(10, 530, "RELOADING...")
        if time.time() < invincible_until:
            draw_text(10, 500, "CYAN ORB: INVINCIBLE")
        if time.time() < no_reload_until:
            draw_text(10, 470, "RED ORB: NO RELOAD")
    else:
        draw_text(350, 430, "GAME OVER!")
        draw_text(315, 395, "Press R to restart or M for main menu.")

# Enemy and Combat Logic
def update_enemy_level():
    global enemy_level
    if kill_count >= 10:
        enemy_level = 3
    elif kill_count >= 5:
        enemy_level = 2
    else:
        enemy_level = 1


def choose_demon_type():
    roll = random.random()
    running = 0.0
    for dtype, data in DEMON_TYPES.items():
        running += data['spawn_weight']
        if roll <= running:
            return dtype
    return 'normal'


def create_enemy(x, y):
    dtype = choose_demon_type()
    data = LEVEL_DATA[enemy_level]
    type_data = DEMON_TYPES[dtype]
    max_hp = int(data['health'] * type_data['health_mult'])


    start_z = 86 if dtype == 'flying' else 50

    return {
        'pos': [x, y, start_z],
        'type': dtype,
        'level': enemy_level,
        'health': max_hp,
        'max_health': max_hp,
        'speed_mult': type_data['speed_mult'],
        'touch_damage': type_data['touch_damage'],
        'hit_radius': type_data['hit_radius'],
        'contact_radius': type_data['contact_radius'],
        'spawn_time': time.time(),
        'last_hit_time': 0.0
    }


def create_powerup(x, y):


    roll = random.random()
    if roll < 0.40:
        ptype = 'invincibility'
    elif roll < 0.70:
        ptype = 'noreload'
    else:
        ptype = 'heal'

    powerups.append({
        'pos': [x, y, 25],
        'type': ptype,
        'scale': 1.0,
        'scale_dir': 1,
        'angle': 0.0
    })

def get_enemy_hit_type(proj, enemy):
    px, py, pz = proj['pos']
    ex, ey, ez = enemy['pos']
    dist = math.sqrt((px - ex) ** 2 + (py - ey) ** 2)

    dtype = enemy.get('type', 'normal')
    hit_radius = enemy.get('hit_radius', 28.0)
    head_radius = 18 if dtype == 'bulky' else 13 if dtype == 'flying' else 14
    head_height = ez + (28 if dtype == 'flying' else 10)


    if dist <= head_radius and pz >= head_height:
        return 'head'
    elif dist <= hit_radius:
        return 'body'
    return None


def damage_enemy(enemy, hit_type, weapon_type):
    global kill_count

    enemy['last_hit_time'] = time.time()

    if cheat_mode:
        damage = enemy.get('health', 9999)
    elif weapon_type == 'Rocket Launcher':
        damage = GUN_DAMAGE['Rocket Launcher']['body']
    else:
        damage = GUN_DAMAGE[weapon_type][hit_type]

    enemy['health'] -= damage

    if enemy['health'] <= 0:
        ex, ey, ez = enemy['pos']
        if enemy in enemies:
            enemies.remove(enemy)

        kill_count += 1
        update_enemy_level()

        if random.random() < 0.15:
            create_powerup(ex, ey)
        return True

    return False


def apply_rocket_aoe(pos):
    global player_health, last_player_hit_time

    for enemy in enemies[:]:
        ex, ey, ez = enemy['pos']
        dist = math.sqrt((pos[0] - ex)**2 + (pos[1] - ey)**2)
        if dist <= ROCKET_RADIUS:
            damage_enemy(enemy, 'body', 'Rocket Launcher')


    px, py, pz = player_pos
    player_dist = math.sqrt((pos[0] - px)**2 + (pos[1] - py)**2)
    if player_dist <= ROCKET_RADIUS and time.time() > invincible_until:

        ratio = 1.0 - (player_dist / ROCKET_RADIUS)
        player_health -= 60.0 * ratio
        last_player_hit_time = time.time()


def update_powerup_animation(dt):
    for pup in powerups:
        pup['angle'] = pup.get('angle', 0.0) + 120.0 * dt
        pup['scale'] = pup.get('scale', 1.0) + 0.8 * dt * pup.get('scale_dir', 1)

        if pup['scale'] > 1.25:
            pup['scale'] = 1.25
            pup['scale_dir'] = -1
        elif pup['scale'] < 0.75:
            pup['scale'] = 0.75
            pup['scale_dir'] = 1


def shoot():
    global last_shot_time, ammo

    if player_health <= 0:
        return


    now = time.time()
    no_reload_active = now < no_reload_until
    if is_reloading and not no_reload_active:
        return


    if ammo[current_gun] <= 0 and not no_reload_active:
        return

    delay = [0.5, 0.1, 1.0][current_gun]
    if (not no_reload_active) and now - last_shot_time < delay:
        return

    last_shot_time = now

    if not no_reload_active:
        ammo[current_gun] -= 1

    px, py, pz = player_pos
    yaw = math.radians(player_angle)
    pitch = math.radians(aim_pitch)

    horizontal_power = math.cos(pitch)
    dx = math.cos(yaw) * horizontal_power
    dy = math.sin(yaw) * horizontal_power
    dz = math.sin(pitch)

    speed = [30.0, 38.0, 22.0][current_gun]
    gun_name = guns[current_gun]

    projectiles.append({
        'pos': [px + dx * 15, py + dy * 15, pz + 5],
        'dir': [dx * speed, dy * speed, dz * speed],
        'type': gun_name
    })

# Game State Control
def restart_game():
    global player_pos, player_angle, player_health, enemies, projectiles, powerups, current_gun, explosions, last_player_hit_time
    global kill_count, enemy_level, enemy_spawn_timer, invincible_until, no_reload_until, last_shot_time, aim_pitch, cheat_mode
    global ammo, is_reloading, reload_start_time, player_walk_cycle, player_is_moving

    player_pos = [150.0, 150.0, 50.0]
    player_angle = 45.0
    aim_pitch = 0.0
    player_health = 100.0
    current_gun = 0
    enemies = []
    projectiles = []
    powerups = []
    explosions = []
    last_player_hit_time = 0.0
    invincible_until = 0.0
    no_reload_until = 0.0
    last_shot_time = 0.0
    ammo = max_ammo[:]
    is_reloading = False
    reload_start_time = 0.0
    kill_count = 0
    enemy_level = 1
    enemy_spawn_timer = 0.0
    cheat_mode = False
    player_walk_cycle = 0.0
    player_is_moving = False

    for k in keys:
        keys[k] = False
    for k in special_keys:
        special_keys[k] = False


def start_game():
    global game_state
    restart_game()
    game_state = 'playing'

# Input Handling
def keyboardListener(key, x, y):
    global current_gun, camera_mode, cheat_mode, is_reloading, reload_start_time, game_state
    key = key.lower()


    if game_state == 'menu':
        if key in (b'\r', b'\n', b' ', b's'):
            start_game()
        elif key in (b'e', b'\x1b'):
            os._exit(0)
        glutPostRedisplay()
        return

    if key == b'\x1b':
        os._exit(0)

    if key == b'm':
        game_state = 'menu'
        glutPostRedisplay()
        return

    if player_health > 0:
        try:
            k = key.decode('utf-8')
            if k in keys:
                keys[k] = True
        except:
            pass

        if key == b'1':
            current_gun = 0
        elif key == b'2':
            current_gun = 1
        elif key == b'3':
            current_gun = 2
        elif key == b'c':
            camera_mode = 3 if camera_mode == 1 else 1
        elif key == b' ':
            shoot()
        elif key == b'j':
            cheat_mode = not cheat_mode
        elif key == b'b':
            if ammo[current_gun] < max_ammo[current_gun] and time.time() >= no_reload_until:
                is_reloading = True
                reload_start_time = time.time()

    if key == b'r':
        restart_game()

def keyboardUpListener(key, x, y):
    try:
        k = key.lower().decode('utf-8')
        if k in keys:
            keys[k] = False
    except:
        pass

def specialKeyListener(key, x, y):
    if game_state == 'playing' and player_health > 0:
        if key == GLUT_KEY_LEFT:
            special_keys['left'] = True
        elif key == GLUT_KEY_RIGHT:
            special_keys['right'] = True
        elif key == GLUT_KEY_UP:
            special_keys['up'] = True
        elif key == GLUT_KEY_DOWN:
            special_keys['down'] = True

def specialKeyUpListener(key, x, y):
    if key == GLUT_KEY_LEFT:
        special_keys['left'] = False
    elif key == GLUT_KEY_RIGHT:
        special_keys['right'] = False
    elif key == GLUT_KEY_UP:
        special_keys['up'] = False
    elif key == GLUT_KEY_DOWN:
        special_keys['down'] = False

# Camera and Update Loop
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1.25, 0.1, 3500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    px, py, pz = player_pos
    rad = math.radians(player_angle)
    pitch = math.radians(aim_pitch)
    dx = math.cos(rad) * math.cos(pitch)
    dy = math.sin(rad) * math.cos(pitch)
    dz = math.sin(pitch)

    if camera_mode == 1:
        gluLookAt(px, py, pz + 10,
                  px + dx * 200, py + dy * 200, pz + 10 + dz * 200,
                  0, 0, 1)
    else:
        gluLookAt(px - dx*150, py - dy*150, pz + 100,
                  px, py, pz,
                  0, 0, 1)

last_time = time.time()
enemy_spawn_timer = 0.0

def idle():
    global last_time, player_health, enemy_spawn_timer, invincible_until, player_angle, aim_pitch
    global is_reloading, reload_start_time, ammo, no_reload_until, last_player_hit_time, player_walk_cycle, player_is_moving

    now = time.time()
    dt = now - last_time
    last_time = now

    if game_state != 'playing':
        glutPostRedisplay()
        return

    if player_health <= 0:
        glutPostRedisplay()
        return


    if is_reloading:
        if time.time() - reload_start_time >= reload_time[current_gun]:
            ammo[current_gun] = max_ammo[current_gun]
            is_reloading = False


    px, py, pz = player_pos
    rad = math.radians(player_angle)
    speed = 250.0 * dt
    dx = math.cos(rad) * speed
    dy = math.sin(rad) * speed

    nx, ny = px, py
    if keys['w']:
        nx += dx
        ny += dy
    if keys['s']:
        nx -= dx
        ny -= dy
    if keys['a']:
        nx -= dy
        ny += dx
    if keys['d']:
        nx += dy
        ny -= dx

    moved = False
    if nx != px or ny != py:
        if not check_collision(nx, py, 15):
            if abs(player_pos[0] - nx) > 0.0001:
                moved = True
            player_pos[0] = nx
        if not check_collision(player_pos[0], ny, 15):
            if abs(player_pos[1] - ny) > 0.0001:
                moved = True
            player_pos[1] = ny

    player_is_moving = moved
    if player_is_moving:
        player_walk_cycle += dt * 13.0
    else:
        player_walk_cycle *= 0.84

    turn_speed = 150.0 * dt
    pitch_speed = 90.0 * dt
    if special_keys['left']:
        player_angle += turn_speed
    if special_keys['right']:
        player_angle -= turn_speed
    if special_keys['up']:
        aim_pitch = min(35.0, aim_pitch + pitch_speed)
    if special_keys['down']:
        aim_pitch = max(-30.0, aim_pitch - pitch_speed)


    for proj in projectiles[:]:
        proj['pos'][0] += proj['dir'][0]
        proj['pos'][1] += proj['dir'][1]
        proj['pos'][2] += proj['dir'][2]

        hit_wall = False if cheat_mode else check_collision(proj['pos'][0], proj['pos'][1], 5)
        hit_target = None
        hit_type = None

        if not hit_wall:
            for enemy in enemies[:]:
                hit_type = get_enemy_hit_type(proj, enemy)
                if hit_type is not None:
                    hit_target = enemy
                    break

        if hit_wall or hit_target:
            if proj in projectiles:
                projectiles.remove(proj)

            if proj['type'] == 'Rocket Launcher':
                explosions.append({
                    'pos': proj['pos'][:],
                    'time_created': time.time(),
                    'max_radius': ROCKET_RADIUS,
                    'duration': 0.5
                })
                apply_rocket_aoe(proj['pos'])
            elif hit_target:
                damage_enemy(hit_target, hit_type, proj['type'])


    now = time.time()
    for exp in explosions[:]:
        if now - exp['time_created'] > exp['duration']:
            explosions.remove(exp)


    px, py, pz = player_pos
    for enemy in enemies:
        ex, ey, ez = enemy['pos']


        if enemy.get('type') == 'flying':
            enemy['pos'][2] = 86 + math.sin((time.time() - enemy.get('spawn_time', time.time())) * 4.0) * 9.0
            ez = enemy['pos'][2]

        dist = math.sqrt((px - ex)**2 + (py - ey)**2)
        if dist < enemy.get('contact_radius', 30.0):
            if time.time() > invincible_until:
                player_health -= enemy.get('touch_damage', 20.0) * dt
                last_player_hit_time = time.time()
        else:
            rad = math.atan2(py - ey, px - ex)
            level = enemy.get('level', enemy_level)
            enemy_speed = LEVEL_DATA[level]['speed'] * enemy.get('speed_mult', 1.0) * dt
            nx = ex + math.cos(rad) * enemy_speed
            ny = ey + math.sin(rad) * enemy_speed


            collision_radius = 22 if enemy.get('type') == 'bulky' else 15
            if not check_collision(nx, ny, collision_radius):
                enemy['pos'][0] = nx
                enemy['pos'][1] = ny


    update_powerup_animation(dt)
    for pup in powerups[:]:
        dist = math.sqrt((px - pup['pos'][0])**2 + (py - pup['pos'][1])**2)
        if dist < 30:
            powerups.remove(pup)
            if pup['type'] == 'invincibility':
                invincible_until = time.time() + 5.0
            elif pup['type'] == 'noreload':
                no_reload_until = time.time() + 5.0
            elif pup['type'] == 'heal':
                player_health = min(100.0, player_health + 30.0)


    enemy_spawn_timer -= dt
    if enemy_spawn_timer <= 0 and len(enemies) < MAX_ENEMIES:
        enemy_spawn_timer = 2.0
        for _ in range(10):
            sx = random.uniform(100, len(game_map[0])*BLOCK_SIZE - 100)
            sy = random.uniform(100, len(game_map)*BLOCK_SIZE - 100)
            if not check_collision(sx, sy, 15) and math.sqrt((px - sx)**2 + (py - sy)**2) > 300:
                enemies.append(create_enemy(sx, sy))
                break

    glutPostRedisplay()

# Rendering Pipeline
def showScreen():
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_W, WINDOW_H)

    if game_state == 'menu':
        draw_start_screen()
        glutSwapBuffers()
        return

    setupCamera()

    draw_map()
    draw_powerups()

    if cheat_mode:
        glDisable(GL_DEPTH_TEST)
        draw_enemies()
        glEnable(GL_DEPTH_TEST)
    else:
        draw_enemies()

    draw_projectiles()
    draw_explosions()
    draw_player_and_weapon()

    glDisable(GL_DEPTH_TEST)
    if camera_mode == 1 and player_health > 0:
        draw_hud_crosshair()

    draw_hud()
    draw_minimap()

    glutSwapBuffers()

# Application Entry Point
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Demon Arena")
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutSpecialUpFunc(specialKeyUpListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
