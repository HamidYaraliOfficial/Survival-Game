import sys
import math
import random
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ─── THEMES ────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "bg": "#1a1a2e", "panel": "#16213e", "accent": "#e94560",
        "btn": "#0f3460", "btn_hover": "#e94560", "text": "#eaeaea",
        "sub": "#a0a0b0", "bar_bg": "#0a0a1a", "hp": "#e94560",
        "mp": "#4cc9f0", "xp": "#f8961e", "ammo": "#90e0ef",
        "sky1": "#0d0d1a", "sky2": "#1a1a3e", "ground": "#2d1b69",
        "platform": "#4a3080", "platform2": "#6a4090",
    },
    "light": {
        "bg": "#f0f4ff", "panel": "#dce8ff", "accent": "#e94560",
        "btn": "#4361ee", "btn_hover": "#e94560", "text": "#1a1a2e",
        "sub": "#555577", "bar_bg": "#c0ccee", "hp": "#e63946",
        "mp": "#4895ef", "xp": "#f4a261", "ammo": "#48cae4",
        "sky1": "#89c2d9", "sky2": "#a9d6e5", "ground": "#5c4033",
        "platform": "#6d4c41", "platform2": "#8d6e63",
    }
}

# ─── TRANSLATIONS ───────────────────────────────────────────────────────────
TR = {
    "en": {
        "title": "SURVIVOR", "start": "START GAME", "resume": "RESUME",
        "restart": "RESTART", "settings": "SETTINGS", "quit": "QUIT",
        "paused": "PAUSED", "game_over": "GAME OVER", "victory": "VICTORY!",
        "level": "LEVEL", "score": "SCORE", "kills": "KILLS",
        "hp": "HP", "mp": "MP", "xp": "XP", "ammo": "AMMO",
        "grenades": "GRN", "combo": "COMBO",
        "lang": "Language", "theme": "Theme",
        "dark": "Dark", "light": "Light",
        "move": "A/D: Move  W/Space: Jump  S: Duck",
        "action": "J: Shoot  K: Grenade  L: Special  P: Pause",
        "lvlup": "LEVEL UP!", "wave": "WAVE",
        "enemy_soldier": "Soldier", "enemy_heavy": "Heavy",
        "enemy_scout": "Scout", "enemy_drone": "Drone", "enemy_boss": "BOSS",
    },
    "zh": {
        "title": "幸存者", "start": "开始游戏", "resume": "继续",
        "restart": "重新开始", "settings": "设置", "quit": "退出",
        "paused": "暂停", "game_over": "游戏结束", "victory": "胜利!",
        "level": "关卡", "score": "分数", "kills": "击杀",
        "hp": "血量", "mp": "能量", "xp": "经验", "ammo": "弹药",
        "grenades": "手雷", "combo": "连击",
        "lang": "语言", "theme": "主题",
        "dark": "暗色", "light": "亮色",
        "move": "A/D:移动  W/空格:跳跃  S:蹲下",
        "action": "J:射击  K:手雷  L:特殊  P:暂停",
        "lvlup": "升级!", "wave": "波次",
        "enemy_soldier": "士兵", "enemy_heavy": "重甲",
        "enemy_scout": "侦察", "enemy_drone": "无人机", "enemy_boss": "首领",
    },
    "fa": {
        "title": "بازمانده", "start": "شروع بازی", "resume": "ادامه",
        "restart": "شروع مجدد", "settings": "تنظیمات", "quit": "خروج",
        "paused": "توقف", "game_over": "پایان بازی", "victory": "پیروزی!",
        "level": "مرحله", "score": "امتیاز", "kills": "کشته",
        "hp": "جان", "mp": "انرژی", "xp": "تجربه", "ammo": "تیر",
        "grenades": "نارنجک", "combo": "کمبو",
        "lang": "زبان", "theme": "پوسته",
        "dark": "تاریک", "light": "روشن",
        "move": "A/D:حرکت  W/فاصله:پرش  S:خم شدن",
        "action": "J:شلیک  K:نارنجک  L:ویژه  P:توقف",
        "lvlup": "ارتقا سطح!", "wave": "موج",
        "enemy_soldier": "سرباز", "enemy_heavy": "سنگین",
        "enemy_scout": "پیشرو", "enemy_drone": "پهپاد", "enemy_boss": "رئیس",
    }
}

GRAVITY = 0.55
PLAYER_SPEED = 4.5
JUMP_FORCE = -13
MAX_LEVELS = 5

# ─── PARTICLE ──────────────────────────────────────────────────────────────
class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','color','size','kind']
    def __init__(self, x, y, vx, vy, life, color, size=3, kind='circle'):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = self.max_life = life
        self.color = color
        self.size = size
        self.kind = kind

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.vx *= 0.97
        self.life -= 1
        return self.life > 0

    def draw(self, p: QPainter, ox):
        alpha = int(255 * self.life / self.max_life)
        c = QColor(self.color)
        c.setAlpha(alpha)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        sx = self.x - ox
        if self.kind == 'circle':
            r = max(1, int(self.size * self.life / self.max_life))
            p.drawEllipse(int(sx - r), int(self.y - r), r*2, r*2)
        else:
            r = max(1, int(self.size * self.life / self.max_life))
            p.drawRect(int(sx - r), int(self.y - r), r*2, r*2)

# ─── FLOAT TEXT ─────────────────────────────────────────────────────────────
class FloatText:
    def __init__(self, x, y, text, color="#ffffff", size=16):
        self.x, self.y = x, y
        self.text = text
        self.color = color
        self.size = size
        self.life = 60
        self.max_life = 60

    def update(self):
        self.y -= 1.2
        self.life -= 1
        return self.life > 0

    def draw(self, p: QPainter, ox):
        alpha = int(255 * self.life / self.max_life)
        c = QColor(self.color)
        c.setAlpha(alpha)
        p.setPen(c)
        font = QFont("Arial", self.size, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(int(self.x - ox), int(self.y), self.text)

# ─── BULLET ─────────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, vx, vy, owner='player', damage=10, color='#ffff00'):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.owner = owner
        self.damage = damage
        self.color = color
        self.alive = True
        self.trail = []

    def update(self, platforms):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        if self.y > 2000 or self.y < -500 or self.x < -500 or self.x > 20000:
            self.alive = False
        for pl in platforms:
            if pl.kind == 'solid' and pl.rect.contains(int(self.x), int(self.y)):
                self.alive = False
                break

    def draw(self, p: QPainter, ox):
        if not self.alive:
            return
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(120 * i / max(1, len(self.trail)))
            c = QColor(self.color)
            c.setAlpha(alpha)
            p.setPen(QPen(c, 2))
            p.drawPoint(int(tx - ox), int(ty))
        c = QColor(self.color)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawEllipse(int(self.x - ox - 4), int(self.y - 4), 8, 8)

# ─── GRENADE ────────────────────────────────────────────────────────────────
class Grenade:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.alive = True
        self.timer = 120
        self.bounces = 0

    def update(self, platforms):
        self.vy += GRAVITY * 0.7
        self.x += self.vx
        self.y += self.vy
        self.timer -= 1
        for pl in platforms:
            if pl.kind == 'solid':
                r = pl.rect
                if r.contains(int(self.x), int(self.y)):
                    if self.vy > 0:
                        self.y = r.top() - 1
                        self.vy *= -0.5
                        self.vx *= 0.8
                        self.bounces += 1
        if self.timer <= 0:
            self.alive = False

    def draw(self, p: QPainter, ox):
        if not self.alive:
            return
        blink = self.timer < 40 and (self.timer // 5) % 2 == 0
        c = QColor("#ff6600") if blink else QColor("#88aa00")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawEllipse(int(self.x - ox - 6), int(self.y - 6), 12, 12)
        p.setPen(QPen(QColor("#ffff00"), 2))
        p.drawLine(int(self.x - ox), int(self.y - 6), int(self.x - ox), int(self.y - 12))

# ─── PLATFORM ───────────────────────────────────────────────────────────────
class Platform:
    def __init__(self, x, y, w, h, kind='solid', color=None):
        self.rect = QRect(x, y, w, h)
        self.kind = kind
        self.color = color

    def draw(self, p: QPainter, ox, theme):
        r = self.rect
        rx = r.x() - int(ox)
        if rx > 1920 or rx + r.width() < -100:
            return
        draw_r = QRect(rx, r.y(), r.width(), r.height())
        if self.kind == 'solid':
            col1 = QColor(self.color or theme.get("platform", "#4a3080"))
            col2 = col1.darker(130)
            grad = QLinearGradient(rx, r.y(), rx, r.y() + r.height())
            grad.setColorAt(0, col1)
            grad.setColorAt(1, col2)
            p.setBrush(grad)
            p.setPen(QPen(col1.lighter(150), 1))
            p.drawRect(draw_r)
            # top shine
            p.setPen(QPen(QColor(255,255,255,60), 2))
            p.drawLine(rx, r.y()+1, rx+r.width(), r.y()+1)
        elif self.kind == 'water':
            c = QColor("#1a6eb5" if not self.color else self.color)
            c.setAlpha(160)
            p.setBrush(c)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(draw_r)
        elif self.kind == 'lava':
            c = QColor("#cc3300" if not self.color else self.color)
            c.setAlpha(200)
            p.setBrush(c)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(draw_r)
            p.setPen(QPen(QColor("#ff6600"), 2))
            p.drawLine(rx, r.y(), rx+r.width(), r.y())

# ─── PLAYER ─────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 32, 48
        self.facing = 1
        self.on_ground = False
        self.ducking = False
        self.running = False
        self.shooting = False
        self.hurt_timer = 0
        self.shoot_cooldown = 0
        self.special_cooldown = 0
        self.grenade_cooldown = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.jump_count = 0
        # stats
        self.hp = 150
        self.max_hp = 150
        self.mp = 100
        self.max_mp = 100
        self.xp = 0
        self.xp_next = 100
        self.level = 1
        self.ammo = 60
        self.max_ammo = 60
        self.grenades = 5
        self.score = 0
        self.kills = 0
        self.combo = 0
        self.combo_timer = 0
        self.alive = True
        self.invincible = 0

    def rect(self):
        h = self.h // 2 if self.ducking else self.h
        return QRect(int(self.x - self.w//2), int(self.y - h), self.w, h)

    def take_damage(self, dmg):
        if self.invincible > 0:
            return
        self.hp -= dmg
        self.hurt_timer = 20
        self.invincible = 30
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, keys, platforms, bullets_out, grenades_out, particles):
        # movement
        moving = False
        speed = PLAYER_SPEED * (1.5 if self.running and not self.ducking else 1.0)
        if keys.get(Qt.Key.Key_A) or keys.get(Qt.Key.Key_Left):
            self.vx = -speed
            self.facing = -1
            moving = True
        elif keys.get(Qt.Key.Key_D) or keys.get(Qt.Key.Key_Right):
            self.vx = speed
            self.facing = 1
            moving = True
        else:
            self.vx *= 0.75

        self.ducking = bool(keys.get(Qt.Key.Key_S) or keys.get(Qt.Key.Key_Down))
        self.running = bool(keys.get(Qt.Key.Key_Shift))

        if (keys.get(Qt.Key.Key_W) or keys.get(Qt.Key.Key_Space)) and self.jump_count < 2:
            if self.on_ground or self.jump_count == 0:
                self.vy = JUMP_FORCE
                self.jump_count += 1
                self.on_ground = False

        # gravity
        self.vy += GRAVITY
        self.vy = min(self.vy, 18)

        # move x
        self.x += self.vx
        self._collide_x(platforms)
        # move y
        self.y += self.vy
        self._collide_y(platforms)

        # hazards
        for pl in platforms:
            if pl.kind in ('lava', 'water') and pl.rect.contains(int(self.x), int(self.y)):
                self.take_damage(2 if pl.kind == 'lava' else 0.5)

        # bounds
        self.x = max(self.w//2, self.x)

        # animation
        self.anim_timer += 1
        if self.anim_timer >= (6 if moving else 12):
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

        # timers
        if self.hurt_timer > 0: self.hurt_timer -= 1
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.special_cooldown > 0: self.special_cooldown -= 1
        if self.grenade_cooldown > 0: self.grenade_cooldown -= 1
        if self.invincible > 0: self.invincible -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # mp regen
        if self.mp < self.max_mp:
            self.mp = min(self.max_mp, self.mp + 0.15)

    def _collide_x(self, platforms):
        r = self.rect()
        for pl in platforms:
            if pl.kind != 'solid': continue
            if r.intersects(pl.rect):
                if self.vx > 0:
                    self.x = pl.rect.left() - self.w//2
                elif self.vx < 0:
                    self.x = pl.rect.right() + self.w//2
                self.vx = 0

    def _collide_y(self, platforms):
        r = self.rect()
        self.on_ground = False
        for pl in platforms:
            if pl.kind != 'solid': continue
            if r.intersects(pl.rect):
                if self.vy > 0:
                    h = self.h // 2 if self.ducking else self.h
                    self.y = pl.rect.top() - 1
                    self.vy = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif self.vy < 0:
                    self.y = pl.rect.bottom() + (self.h // 2 if self.ducking else self.h)
                    self.vy = 0

    def shoot(self, bullets_out, spread=False):
        if self.shoot_cooldown > 0 or self.ammo <= 0:
            return
        self.ammo -= 1
        self.shoot_cooldown = 8
        cy = self.y - (self.h * 0.4)
        speed = 14
        if not spread:
            b = Bullet(self.x, cy, speed * self.facing, 0, 'player', 15, '#ffee00')
            bullets_out.append(b)
        else:
            for ang in [-0.15, 0, 0.15]:
                vx = speed * self.facing * math.cos(ang)
                vy = speed * math.sin(ang)
                b = Bullet(self.x, cy, vx, vy, 'player', 10, '#ff9900')
                bullets_out.append(b)

    def throw_grenade(self, grenades_out):
        if self.grenade_cooldown > 0 or self.grenades <= 0:
            return
        self.grenades -= 1
        self.grenade_cooldown = 40
        vx = 7 * self.facing
        vy = -10
        grenades_out.append(Grenade(self.x, self.y - self.h//2, vx, vy))

    def special(self, bullets_out, particles):
        if self.special_cooldown > 0 or self.mp < 40:
            return
        self.mp -= 40
        self.special_cooldown = 90
        cy = self.y - self.h * 0.4
        for i in range(8):
            ang = i * math.pi / 4
            vx = 10 * math.cos(ang)
            vy = 10 * math.sin(ang)
            b = Bullet(self.x, cy, vx, vy, 'player', 25, '#cc00ff')
            bullets_out.append(b)
        for _ in range(20):
            particles.append(Particle(self.x, cy,
                random.uniform(-6,6), random.uniform(-6,6),
                40, '#cc00ff', 5))

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.4)
            self.max_hp += 20
            self.hp = min(self.hp + 40, self.max_hp)
            self.max_mp += 10
            self.max_ammo += 10
            self.ammo = self.max_ammo
            return True
        return False

    def draw(self, p: QPainter, ox, theme):
        sx = int(self.x - ox)
        sy = int(self.y)
        is_dark = theme.get("bg","#") < "#8"

        # hurt flash
        if self.hurt_timer > 0 and (self.hurt_timer // 3) % 2 == 1:
            return
        if self.invincible > 0 and (self.invincible // 4) % 2 == 1:
            p.setOpacity(0.5)

        h = self.h // 2 if self.ducking else self.h
        bw = self.w

        # shadow
        shadow = QColor(0,0,0,60)
        p.setBrush(shadow)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(sx - bw//2, sy - 4, bw, 8)

        # body
        body_col = QColor("#3a7fd5") if is_dark else QColor("#1a5fb4")
        p.setBrush(body_col)
        p.setPen(QPen(QColor("#ffffff" if is_dark else "#1a1a2e"), 2))
        if self.ducking:
            p.drawRoundedRect(sx - bw//2, sy - h, bw, h, 6, 6)
        else:
            p.drawRoundedRect(sx - bw//2 + 4, sy - int(h*0.55), bw-8, int(h*0.55), 5, 5)
            # legs
            leg_off = int(math.sin(self.anim_frame * math.pi / 2) * 5)
            leg_col = QColor("#2255aa" if is_dark else "#0d3b8e")
            p.setBrush(leg_col)
            p.drawRoundedRect(sx - bw//2 + 2, sy - int(h*0.45), 10, int(h*0.45) - leg_off, 4, 4)
            p.drawRoundedRect(sx + bw//2 - 12, sy - int(h*0.45), 10, int(h*0.45) + leg_off, 4, 4)

        # head
        head_col = QColor("#f5c78e")
        p.setBrush(head_col)
        p.setPen(QPen(QColor("#c8964a"), 2))
        p.drawEllipse(sx - 10, sy - h - 2, 20, 22)

        # helmet
        helmet_col = QColor("#1a3a6e" if is_dark else "#1a3a6e")
        p.setBrush(helmet_col)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(sx - 11, sy - h - 4, 22, 14, 6, 6)

        # eyes
        eye_x = sx + (4 if self.facing > 0 else -8)
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(eye_x, sy - h + 4, 6, 5)
        p.setBrush(QColor("#1a1a2e"))
        p.drawEllipse(eye_x + (1 if self.facing > 0 else 1), sy - h + 5, 3, 3)

        # gun arm
        arm_y = sy - int(h*0.7)
        gun_col = QColor("#888888")
        p.setBrush(gun_col)
        p.setPen(Qt.PenStyle.NoPen)
        gun_x = sx + (bw//2 - 4) * self.facing
        p.drawRoundedRect(gun_x - 3, arm_y - 4, 18 * self.facing if self.facing > 0 else -18, 8, 3, 3)

        p.setOpacity(1.0)

# ─── ENEMY ──────────────────────────────────────────────────────────────────
class Enemy:
    TYPES = {
        'soldier': {'hp':60,'speed':2.0,'damage':8,'shoot_cd':80,'score':100,'xp':30,'w':28,'h':44,'color_idx':0},
        'heavy':   {'hp':180,'speed':1.2,'damage':18,'shoot_cd':120,'score':250,'xp':80,'w':36,'h':52,'color_idx':1},
        'scout':   {'hp':35,'speed':3.5,'damage':5,'shoot_cd':50,'score':150,'xp':50,'w':22,'h':38,'color_idx':2},
        'drone':   {'hp':45,'speed':2.8,'damage':6,'shoot_cd':60,'score':120,'xp':40,'w':30,'h':20,'color_idx':3},
        'boss':    {'hp':600,'speed':1.8,'damage':25,'shoot_cd':40,'score':1000,'xp':400,'w':52,'h':68,'color_idx':4},
    }
    COLORS = ['#cc3333','#aa5500','#00aa88','#5555cc','#990099']

    def __init__(self, x, y, kind='soldier'):
        t = self.TYPES[kind]
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = t['w'], t['h']
        self.kind = kind
        self.hp = t['hp']
        self.max_hp = t['hp']
        self.speed = t['speed']
        self.damage = t['damage']
        self.shoot_cd = t['shoot_cd']
        self.shoot_timer = random.randint(0, t['shoot_cd'])
        self.score_val = t['score']
        self.xp_val = t['xp']
        self.color = self.COLORS[t['color_idx']]
        self.facing = -1
        self.on_ground = False
        self.alive = True
        self.patrol_dir = random.choice([-1, 1])
        self.patrol_timer = random.randint(60, 180)
        self.aggro = False
        self.aggro_range = 400
        self.hurt_timer = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.fly_offset = random.uniform(0, math.pi * 2)

    def rect(self):
        return QRect(int(self.x - self.w//2), int(self.y - self.h), self.w, self.h)

    def take_damage(self, dmg):
        self.hp -= dmg
        self.hurt_timer = 12
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, platforms, player, bullets_out, particles, tick):
        if not self.alive:
            return
        dx = player.x - self.x
        dist = abs(dx)
        if dist < self.aggro_range:
            self.aggro = True
        if dist > self.aggro_range * 1.5:
            self.aggro = False

        is_flying = self.kind == 'drone'
        if is_flying:
            # fly toward player
            target_y = player.y - 80
            self.fly_offset += 0.05
            self.y += (target_y - self.y) * 0.03 + math.sin(self.fly_offset) * 1.5
            if self.aggro:
                self.x += self.speed * (1 if dx > 0 else -1)
                self.facing = 1 if dx > 0 else -1
        else:
            if self.aggro:
                self.vx = self.speed * (1 if dx > 0 else -1)
                self.facing = 1 if dx > 0 else -1
            else:
                self.patrol_timer -= 1
                if self.patrol_timer <= 0:
                    self.patrol_dir *= -1
                    self.patrol_timer = random.randint(60, 180)
                self.vx = self.speed * 0.5 * self.patrol_dir
                self.facing = self.patrol_dir

            self.vy += GRAVITY
            self.vy = min(self.vy, 18)
            self.x += self.vx
            self.y += self.vy
            self._collide_y(platforms)

        self.x = max(self.w//2, self.x)

        # shooting
        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and dist < 500:
            self.shoot_timer = self.shoot_cd + random.randint(-10, 20)
            cy = self.y - self.h * 0.5
            spd = 8
            if self.kind == 'boss':
                for ang in [-0.2, 0, 0.2]:
                    vx = spd * self.facing * math.cos(ang)
                    vy = spd * math.sin(ang)
                    bullets_out.append(Bullet(self.x, cy, vx, vy, 'enemy', self.damage, '#ff4444'))
            elif self.kind == 'drone':
                dy = player.y - cy
                length = math.sqrt(dx*dx + dy*dy) or 1
                bullets_out.append(Bullet(self.x, cy, spd*dx/length, spd*dy/length, 'enemy', self.damage, '#ff8800'))
            else:
                bullets_out.append(Bullet(self.x, cy, spd * self.facing, 0, 'enemy', self.damage, '#ff4444'))

        # anim
        self.anim_timer += 1
        if self.anim_timer >= 8:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

    def _collide_y(self, platforms):
        r = self.rect()
        self.on_ground = False
        for pl in platforms:
            if pl.kind != 'solid': continue
            if r.intersects(pl.rect):
                if self.vy > 0:
                    self.y = pl.rect.top() - 1
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = pl.rect.bottom() + self.h
                    self.vy = 0

    def draw(self, p: QPainter, ox, theme):
        if not self.alive:
            return
        sx = int(self.x - ox)
        sy = int(self.y)
        is_dark = theme.get("bg","#") < "#8"

        if self.hurt_timer > 0 and (self.hurt_timer // 3) % 2 == 1:
            p.setOpacity(0.4)

        ec = QColor(self.color)
        dark_ec = ec.darker(150)
        p.setBrush(ec)
        p.setPen(QPen(dark_ec, 2))

        if self.kind == 'drone':
            # drone body
            p.drawRoundedRect(sx - self.w//2, sy - self.h//2, self.w, self.h, 8, 8)
            # rotors
            p.setPen(QPen(QColor("#aaaaaa"), 2))
            p.drawLine(sx - self.w//2 - 10, sy - self.h//2 - 4, sx + self.w//2 + 10, sy - self.h//2 - 4)
            for ex in [sx - self.w//2 - 8, sx + self.w//2 + 8]:
                p.setBrush(QColor("#cccccc"))
                p.drawEllipse(ex - 6, sy - self.h//2 - 10, 12, 7)
            # camera eye
            p.setBrush(QColor("#ff0000"))
            p.drawEllipse(sx + (5 if self.facing > 0 else -10), sy - self.h//2 + 4, 8, 8)
        elif self.kind == 'boss':
            # boss - big and menacing
            p.drawRoundedRect(sx - self.w//2, sy - self.h, self.w, self.h, 8, 8)
            # shoulder pads
            p.setBrush(ec.lighter(120))
            p.drawRoundedRect(sx - self.w//2 - 10, sy - self.h + 10, 14, 24, 4, 4)
            p.drawRoundedRect(sx + self.w//2 - 4, sy - self.h + 10, 14, 24, 4, 4)
            # head
            p.setBrush(QColor("#f5c78e"))
            p.drawEllipse(sx - 14, sy - self.h - 2, 28, 28)
            # horns
            p.setBrush(ec.darker(110))
            horn = QPolygon([QPoint(sx - 10, sy - self.h - 2), QPoint(sx - 16, sy - self.h - 18), QPoint(sx - 4, sy - self.h - 2)])
            p.drawPolygon(horn)
            horn2 = QPolygon([QPoint(sx + 4, sy - self.h - 2), QPoint(sx + 16, sy - self.h - 18), QPoint(sx + 10, sy - self.h - 2)])
            p.drawPolygon(horn2)
            # eyes glow
            p.setBrush(QColor("#ff0000"))
            p.drawEllipse(sx - 8, sy - self.h + 8, 6, 6)
            p.drawEllipse(sx + 2, sy - self.h + 8, 6, 6)
        else:
            # standard enemy
            p.drawRoundedRect(sx - self.w//2 + 3, sy - int(self.h*0.55), self.w-6, int(self.h*0.55), 5, 5)
            # legs
            leg_off = int(math.sin(self.anim_frame * math.pi / 2) * 4)
            p.setBrush(dark_ec)
            p.drawRoundedRect(sx - self.w//2 + 2, sy - int(self.h*0.45), 8, int(self.h*0.45) - leg_off, 3, 3)
            p.drawRoundedRect(sx + self.w//2 - 10, sy - int(self.h*0.45), 8, int(self.h*0.45) + leg_off, 3, 3)
            # head
            p.setBrush(QColor("#f5c78e"))
            p.setPen(QPen(QColor("#c8964a"), 1))
            p.drawEllipse(sx - 9, sy - self.h - 2, 18, 20)
            # helmet
            p.setBrush(dark_ec)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(sx - 10, sy - self.h - 4, 20, 12, 5, 5)
            # gun
            p.setBrush(QColor("#666666"))
            gx = sx + (self.w//2 - 3) * self.facing
            p.drawRoundedRect(gx - 2 if self.facing < 0 else gx - 2,
                              sy - int(self.h*0.7) - 4, 16 * self.facing if self.facing > 0 else -16, 7, 2, 2)

        # HP bar
        bar_w = self.w + 10
        bar_x = sx - bar_w//2
        bar_y = sy - self.h - 12
        p.setBrush(QColor("#330000"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(bar_x, bar_y, bar_w, 5)
        hp_ratio = self.hp / self.max_hp
        hp_color = QColor("#00cc44") if hp_ratio > 0.5 else QColor("#ffaa00") if hp_ratio > 0.25 else QColor("#ff2200")
        p.setBrush(hp_color)
        p.drawRect(bar_x, bar_y, int(bar_w * hp_ratio), 5)

        p.setOpacity(1.0)

# ─── LEVEL ──────────────────────────────────────────────────────────────────
class Level:
    def __init__(self, idx):
        self.idx = idx
        self.platforms = []
        self.enemies = []
        self.width = 3200 + idx * 800
        self._build()

    def _build(self):
        idx = self.idx
        ground_y = 520
        self.platforms.append(Platform(0, ground_y, self.width, 80, 'solid'))

        # floating platforms
        positions = [
            (200, 400), (500, 340), (800, 280), (1100, 360), (1400, 300),
            (1700, 380), (2000, 260), (2300, 320), (2600, 400), (2900, 280),
        ]
        widths = [160, 140, 180, 120, 160, 140, 200, 150, 130, 170]
        for i, ((px, py), pw) in enumerate(zip(positions, widths)):
            if px < self.width:
                self.platforms.append(Platform(px, py + idx*10, pw, 18, 'solid'))

        # hazards
        if idx >= 2:
            self.platforms.append(Platform(1200, ground_y, 200, 80, 'lava', '#cc3300'))
        if idx >= 3:
            self.platforms.append(Platform(2400, ground_y, 150, 80, 'water', '#1a6eb5'))
        if idx >= 4:
            self.platforms.append(Platform(600, ground_y, 100, 80, 'lava'))
            self.platforms.append(Platform(1800, ground_y, 120, 80, 'lava'))

        # enemies
        enemy_count = 4 + idx * 3
        kinds = ['soldier']
        if idx >= 1: kinds.append('scout')
        if idx >= 2: kinds.append('heavy')
        if idx >= 3: kinds.append('drone')

        for i in range(enemy_count):
            ex = random.randint(400, self.width - 200)
            ek = random.choice(kinds)
            ey = ground_y - 2
            if ek == 'drone':
                ey = ground_y - 200
            self.enemies.append(Enemy(ex, ey, ek))

        # boss on last level
        if idx == MAX_LEVELS - 1:
            self.enemies.append(Enemy(self.width - 400, ground_y - 2, 'boss'))

# ─── BACKGROUND ─────────────────────────────────────────────────────────────
class Background:
    def __init__(self, level_width):
        self.stars = [(random.randint(0, level_width), random.randint(0, 400), random.random()) for _ in range(120)]
        self.clouds = [(random.randint(0, level_width), random.randint(30, 180), random.randint(80, 200), random.randint(40, 80)) for _ in range(20)]
        self.mountains = [(random.randint(0, level_width), random.randint(200, 420), random.randint(80, 200)) for _ in range(18)]

    def draw(self, p: QPainter, ox, w, h, theme):
        is_dark = theme.get("bg","#") < "#8"
        # sky gradient
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(theme['sky1']))
        grad.setColorAt(1, QColor(theme['sky2']))
        p.fillRect(0, 0, w, h, grad)

        if is_dark:
            # stars
            for sx, sy, size in self.stars:
                sx_s = (sx - ox * 0.1) % w
                blink = 0.5 + 0.5 * math.sin(sx * 0.3 + sy * 0.2)
                alpha = int(150 + 100 * blink)
                c = QColor(255, 255, 255, alpha)
                p.setPen(c)
                r = max(1, int(size * 2))
                p.drawEllipse(int(sx_s), int(sy), r, r)
        else:
            # sun
            sun_x = int((800 - ox * 0.05) % (w * 2))
            sun_grad = QRadialGradient(sun_x, 80, 50)
            sun_grad.setColorAt(0, QColor(255, 230, 100, 220))
            sun_grad.setColorAt(1, QColor(255, 200, 50, 0))
            p.setBrush(sun_grad)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(sun_x - 50, 30, 100, 100)

        # mountains (parallax 0.3)
        mountain_col = QColor(theme['ground']).darker(110)
        mountain_col.setAlpha(180)
        p.setBrush(mountain_col)
        p.setPen(Qt.PenStyle.NoPen)
        for mx, my, mh in self.mountains:
            mx_s = int((mx - ox * 0.3) % (w + 300)) - 150
            pts = [QPoint(mx_s - 80, h), QPoint(mx_s, my), QPoint(mx_s + 80, h)]
            p.drawPolygon(QPolygon(pts))

        # clouds (parallax 0.5)
        for cx, cy, cw, ch in self.clouds:
            cx_s = int((cx - ox * 0.5) % (w + 300)) - 150
            cloud_col = QColor(255,255,255, 60 if is_dark else 200)
            p.setBrush(cloud_col)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(cx_s - cw//2, cy - ch//2, cw, ch)
            p.drawEllipse(cx_s - cw//3, cy - int(ch*0.7), int(cw*0.7), int(ch*0.7))
            p.drawEllipse(cx_s + cw//6, cy - int(ch*0.6), int(cw*0.6), int(ch*0.6))

# ─── GAME CANVAS ────────────────────────────────────────────────────────────
class GameCanvas(QWidget):
    score_updated = pyqtSignal(int)
    state_changed = pyqtSignal(str)
    levelup_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.theme = THEMES['dark']
        self.lang = 'en'
        self.state = 'idle'
        self.keys = {}
        self.tick = 0
        self.offset_x = 0.0
        self.player = None
        self.level = None
        self.bullets = []
        self.grenades = []
        self.particles = []
        self.float_texts = []
        self.bg = None
        self.current_level_idx = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)
        self._font_cache = {}
        self.setMouseTracking(True)

    def t(self, key):
        return TR[self.lang].get(key, key)

    def set_theme(self, name):
        self.theme = THEMES.get(name, THEMES['dark'])
        self.update()

    def set_lang(self, lang):
        self.lang = lang
        self.update()

    def start_game(self):
        self.current_level_idx = 0
        self._load_level(0)
        self.state = 'playing'
        self.state_changed.emit('playing')
        self.setFocus()

    def _load_level(self, idx):
        self.level = Level(idx)
        self.bg = Background(self.level.width)
        self.player = Player(100, 400)
        self.bullets = []
        self.grenades = []
        self.particles = []
        self.float_texts = []
        self.offset_x = 0.0
        self.tick = 0

    def _next_level(self):
        self.current_level_idx += 1
        if self.current_level_idx >= MAX_LEVELS:
            self.state = 'victory'
            self.state_changed.emit('victory')
        else:
            old_player = self.player
            self._load_level(self.current_level_idx)
            # carry over player stats
            self.player.hp = old_player.hp
            self.player.max_hp = old_player.max_hp
            self.player.mp = old_player.mp
            self.player.max_mp = old_player.max_mp
            self.player.level = old_player.level
            self.player.xp = old_player.xp
            self.player.xp_next = old_player.xp_next
            self.player.score = old_player.score
            self.player.kills = old_player.kills
            self.player.ammo = old_player.max_ammo
            self.player.grenades = old_player.grenades

    def _tick(self):
        if self.state != 'playing':
            self.update()
            return
        self.tick += 1
        pl = self.player
        lv = self.level

        # player actions
        if self.keys.get(Qt.Key.Key_J):
            pl.shoot(self.bullets, spread=self.keys.get(Qt.Key.Key_Shift, False))
        if self.keys.get(Qt.Key.Key_K):
            pl.throw_grenade(self.grenades)
        if self.keys.get(Qt.Key.Key_L):
            leveled = pl.special(self.bullets, self.particles)

        pl.update(self.keys, lv.platforms, self.bullets, self.grenades, self.particles)

        # camera follow
        target_ox = pl.x - self.width() * 0.4
        target_ox = max(0, min(target_ox, lv.width - self.width()))
        self.offset_x += (target_ox - self.offset_x) * 0.1

        # bullets
        for b in self.bullets:
            b.update(lv.platforms)
        # grenade
        for g in self.grenades:
            g.update(lv.platforms)
            if not g.alive:
                self._explode(g.x, g.y, 80, 30)
        self.grenades = [g for g in self.grenades if g.alive]

        # enemy update
        for en in lv.enemies:
            if not en.alive: continue
            en.update(lv.platforms, pl, self.bullets, self.particles, self.tick)

        # collision: player bullets vs enemies
        for b in self.bullets:
            if not b.alive or b.owner != 'player': continue
            for en in lv.enemies:
                if not en.alive: continue
                if en.rect().contains(int(b.x), int(b.y)):
                    en.take_damage(b.damage)
                    b.alive = False
                    mult = max(1, pl.combo)
                    actual_dmg = b.damage * mult
                    self.float_texts.append(FloatText(en.x, en.y - en.h - 10,
                        f"-{actual_dmg}", "#ff4444", 14))
                    if not en.alive:
                        self._on_enemy_killed(en)
                    # blood
                    for _ in range(6):
                        self.particles.append(Particle(b.x, b.y,
                            random.uniform(-3,3), random.uniform(-4,0),
                            20, '#cc0000', 4))
                    break

        # enemy bullets vs player
        for b in self.bullets:
            if not b.alive or b.owner != 'enemy': continue
            if pl.alive and pl.rect().contains(int(b.x), int(b.y)):
                pl.take_damage(b.damage)
                b.alive = False
                self.float_texts.append(FloatText(pl.x, pl.y - pl.h - 10,
                    f"-{b.damage}", "#ff8800", 14))
                for _ in range(5):
                    self.particles.append(Particle(b.x, b.y,
                        random.uniform(-2,2), random.uniform(-3,0),
                        15, '#ffaa00', 3))

        # grenade explosion vs enemies (handled above, also check timing)
        self.bullets = [b for b in self.bullets if b.alive]

        # particles & float texts
        self.particles = [pt for pt in self.particles if pt.update()]
        self.float_texts = [ft for ft in self.float_texts if ft.update()]

        # player death
        if not pl.alive:
            self.state = 'gameover'
            self.state_changed.emit('gameover')

        # level complete
        alive_enemies = [e for e in lv.enemies if e.alive]
        if len(alive_enemies) == 0:
            self._next_level()

        self.score_updated.emit(pl.score)
        self.update()

    def _on_enemy_killed(self, en):
        pl = self.player
        pl.kills += 1
        pl.combo += 1
        pl.combo_timer = 90
        mult = max(1, pl.combo)
        gained_score = en.score_val * mult
        pl.score += gained_score
        # XP
        leveled = pl.add_xp(en.xp_val)
        if leveled:
            self.float_texts.append(FloatText(pl.x, pl.y - pl.h - 30,
                self.t('lvlup'), '#ffff00', 20))
            self.levelup_signal.emit(pl.level)
        # explosion particles
        self._explode(en.x, en.y - en.h//2, 50, 20)

    def _explode(self, x, y, radius, count):
        colors = ['#ff6600','#ff9900','#ffcc00','#ff3300','#ffffff']
        for _ in range(count):
            ang = random.uniform(0, math.pi * 2)
            spd = random.uniform(1, radius/10)
            self.particles.append(Particle(x, y,
                math.cos(ang)*spd, math.sin(ang)*spd,
                random.randint(20, 50), random.choice(colors),
                random.randint(3,8)))
        # shockwave float text
        self.float_texts.append(FloatText(x, y - 20, "BOOM!", '#ff6600', 18))

    def keyPressEvent(self, e):
        self.keys[e.key()] = True
        if e.key() == Qt.Key.Key_P and self.state == 'playing':
            self.state = 'paused'
            self.state_changed.emit('paused')
        elif e.key() == Qt.Key.Key_P and self.state == 'paused':
            self.state = 'playing'
            self.state_changed.emit('playing')
            self.setFocus()

    def keyReleaseEvent(self, e):
        self.keys[e.key()] = False

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if self.state == 'idle':
            self._draw_idle(p, w, h)
        elif self.state in ('playing', 'paused'):
            self._draw_game(p, w, h)
            if self.state == 'paused':
                self._draw_overlay(p, w, h, self.t('paused'), '#4cc9f0')
        elif self.state == 'gameover':
            if self.player:
                self._draw_game(p, w, h)
            self._draw_overlay(p, w, h, self.t('game_over'), '#e94560')
        elif self.state == 'victory':
            if self.player:
                self._draw_game(p, w, h)
            self._draw_overlay(p, w, h, self.t('victory'), '#f8961e')

        p.end()

    def _draw_idle(self, p, w, h):
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(self.theme['sky1']))
        grad.setColorAt(1, QColor(self.theme['sky2']))
        p.fillRect(0, 0, w, h, grad)
        # animated particles
        for i in range(30):
            x = int((i * 137 + self.tick * 0.5) % w)
            y = int((i * 83 + math.sin(i + self.tick * 0.02) * 50) % h)
            alpha = int(80 + 80 * math.sin(self.tick * 0.05 + i))
            c = QColor(self.theme['accent'])
            c.setAlpha(alpha)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(c)
            p.drawEllipse(x, y, 3, 3)
        # title
        title_size = max(28, min(60, w // 12))
        font = QFont("Arial", title_size, QFont.Weight.Black)
        p.setFont(font)
        # glow
        for offset in range(3, 0, -1):
            glow = QColor(self.theme['accent'])
            glow.setAlpha(30 * offset)
            p.setPen(glow)
            p.drawText(QRect(0, h//3 - title_size - offset*4, w, title_size + 20),
                       Qt.AlignmentFlag.AlignHCenter, self.t('title'))
        p.setPen(QColor(self.theme['text']))
        p.drawText(QRect(0, h//3 - title_size, w, title_size + 20),
                   Qt.AlignmentFlag.AlignHCenter, self.t('title'))
        # subtitle
        sub_size = max(10, min(16, w // 50))
        font2 = QFont("Arial", sub_size)
        p.setFont(font2)
        p.setPen(QColor(self.theme['sub']))
        p.drawText(QRect(0, h//3 + title_size + 10, w, 30),
                   Qt.AlignmentFlag.AlignHCenter,
                   self.t('move') + "  |  " + self.t('action'))

    def _draw_game(self, p, w, h):
        if not self.level or not self.player:
            return
        ox = int(self.offset_x)
        # background
        self.bg.draw(p, ox, w, h, self.theme)
        # platforms
        for pl_obj in self.level.platforms:
            pl_obj.draw(p, ox, self.theme)
        # bullets
        for b in self.bullets:
            b.draw(p, ox)
        # grenades
        for g in self.grenades:
            g.draw(p, ox)
        # enemies
        for en in self.level.enemies:
            if en.alive:
                en.draw(p, ox, self.theme)
        # particles
        for pt in self.particles:
            pt.draw(p, ox)
        # float texts
        for ft in self.float_texts:
            ft.draw(p, ox)
        # player
        self.player.draw(p, ox, self.theme)
        # HUD
        self._draw_hud(p, w, h)

    def _draw_hud(self, p, w, h):
        pl = self.player
        hud_y = 10
        bar_h = max(12, h // 45)
        bar_w = max(80, w // 6)
        pad = 10
        hud_bg = QColor(self.theme['bar_bg'])
        hud_bg.setAlpha(180)
        # panel bg
        p.setBrush(hud_bg)
        p.setPen(Qt.PenStyle.NoPen)
        panel_w = bar_w + 80
        p.drawRoundedRect(pad, hud_y, panel_w, 110, 8, 8)

        def draw_bar(label, val, mx, color, y_off):
            font = QFont("Arial", max(8, bar_h - 2), QFont.Weight.Bold)
            p.setFont(font)
            p.setPen(QColor(self.theme['sub']))
            p.drawText(pad + 8, hud_y + y_off + bar_h - 2, label)
            bx = pad + 48
            p.setBrush(QColor("#000000"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(bx, hud_y + y_off, bar_w, bar_h, 3, 3)
            fill_w = int(bar_w * max(0, val) / max(1, mx))
            grad = QLinearGradient(bx, 0, bx + fill_w, 0)
            c = QColor(color)
            grad.setColorAt(0, c.darker(120))
            grad.setColorAt(1, c.lighter(130))
            p.setBrush(grad)
            p.drawRoundedRect(bx, hud_y + y_off, fill_w, bar_h, 3, 3)
            p.setPen(QColor(self.theme['text']))
            p.drawText(bx + bar_w + 4, hud_y + y_off + bar_h - 2, f"{int(val)}/{int(mx)}")

        draw_bar(self.t('hp'), pl.hp, pl.max_hp, self.theme['hp'], 8)
        draw_bar(self.t('mp'), pl.mp, pl.max_mp, self.theme['mp'], 8 + bar_h + 6)
        draw_bar(self.t('xp'), pl.xp, pl.xp_next, self.theme['xp'], 8 + (bar_h + 6) * 2)

        # ammo & grenades
        font_s = QFont("Arial", max(8, bar_h - 1), QFont.Weight.Bold)
        p.setFont(font_s)
        p.setPen(QColor(self.theme['ammo']))
        p.drawText(pad + 8, hud_y + 8 + (bar_h + 6) * 3 + bar_h, f"{self.t('ammo')}: {pl.ammo}/{pl.max_ammo}  {self.t('grenades')}: {pl.grenades}")

        # score / kills / level / combo — top right
        info_font = QFont("Arial", max(9, w // 80), QFont.Weight.Bold)
        p.setFont(info_font)
        right_x = w - max(160, w // 5)
        info_bg = QColor(self.theme['bar_bg'])
        info_bg.setAlpha(170)
        p.setBrush(info_bg)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(right_x - 8, hud_y, max(160, w // 5), 90, 8, 8)

        p.setPen(QColor(self.theme['text']))
        line_h = max(18, h // 30)
        p.drawText(right_x, hud_y + line_h,     f"{self.t('level')}: {self.current_level_idx + 1}/{MAX_LEVELS}  Lv.{pl.level}")
        p.drawText(right_x, hud_y + line_h * 2, f"{self.t('score')}: {pl.score}")
        p.drawText(right_x, hud_y + line_h * 3, f"{self.t('kills')}: {pl.kills}")
        if pl.combo > 1:
            c = QColor(self.theme['xp'])
            p.setPen(c)
            p.drawText(right_x, hud_y + line_h * 4, f"{self.t('combo')} x{pl.combo}!")

        # special cooldown indicator (bottom left)
        sc_ratio = 1.0 - pl.special_cooldown / 90.0
        sc_col = QColor(self.theme['mp']) if sc_ratio >= 1.0 else QColor(self.theme['sub'])
        p.setPen(QPen(sc_col, 3))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(pad, h - 50, 36, 36, 90 * 16, int(-360 * 16 * sc_ratio))
        p.setPen(QColor(self.theme['text']))
        font_tiny = QFont("Arial", 7)
        p.setFont(font_tiny)
        p.drawText(pad + 6, h - 27, "SP")

        # controls hint (bottom center) — only show briefly at start
        if self.tick < 300:
            alpha = int(255 * min(1.0, (300 - self.tick) / 60.0))
            hint_col = QColor(self.theme['sub'])
            hint_col.setAlpha(alpha)
            p.setPen(hint_col)
            hint_font = QFont("Arial", max(8, w // 90))
            p.setFont(hint_font)
            p.drawText(QRect(0, h - 36, w, 20),
                       Qt.AlignmentFlag.AlignHCenter, self.t('move'))
            p.drawText(QRect(0, h - 18, w, 18),
                       Qt.AlignmentFlag.AlignHCenter, self.t('action'))

    def _draw_overlay(self, p, w, h, title_text, color_hex):
        # dim background
        overlay = QColor(0, 0, 0, 160)
        p.fillRect(0, 0, w, h, overlay)

        # glowing panel
        cx, cy = w // 2, h // 2
        panel_w = max(300, w // 2)
        panel_h = max(180, h // 3)
        panel_col = QColor(self.theme['panel'])
        panel_col.setAlpha(230)
        p.setBrush(panel_col)
        border_col = QColor(color_hex)
        p.setPen(QPen(border_col, 3))
        p.drawRoundedRect(cx - panel_w // 2, cy - panel_h // 2, panel_w, panel_h, 14, 14)

        # title text glow
        title_size = max(22, min(48, w // 15))
        font = QFont("Arial", title_size, QFont.Weight.Black)
        p.setFont(font)
        for offset in range(3, 0, -1):
            glow = QColor(color_hex)
            glow.setAlpha(25 * offset)
            p.setPen(glow)
            p.drawText(QRect(cx - panel_w // 2, cy - panel_h // 2 - offset * 3,
                             panel_w, title_size + 20),
                       Qt.AlignmentFlag.AlignHCenter, title_text)
        p.setPen(QColor(color_hex))
        p.drawText(QRect(cx - panel_w // 2, cy - panel_h // 2,
                         panel_w, title_size + 20),
                   Qt.AlignmentFlag.AlignHCenter, title_text)

        if self.player:
            info_size = max(10, min(16, w // 55))
            font2 = QFont("Arial", info_size)
            p.setFont(font2)
            p.setPen(QColor(self.theme['text']))
            info_y = cy - panel_h // 2 + title_size + 28
            line_gap = info_size + 10
            p.drawText(QRect(cx - panel_w // 2, info_y, panel_w, line_gap),
                       Qt.AlignmentFlag.AlignHCenter,
                       f"{self.t('score')}: {self.player.score}   {self.t('kills')}: {self.player.kills}")
            p.drawText(QRect(cx - panel_w // 2, info_y + line_gap, panel_w, line_gap),
                       Qt.AlignmentFlag.AlignHCenter,
                       f"Lv.{self.player.level}   {self.t('level')}: {self.current_level_idx + 1}/{MAX_LEVELS}")

        hint_size = max(9, min(13, w // 65))
        hint_font = QFont("Arial", hint_size)
        p.setFont(hint_font)
        p.setPen(QColor(self.theme['sub']))
        p.drawText(QRect(cx - panel_w // 2, cy + panel_h // 2 - 30, panel_w, 26),
                   Qt.AlignmentFlag.AlignHCenter,
                   "Press buttons below  |  P = Resume" if self.state == 'paused' else "Press buttons below to continue")


# ─── MAIN WINDOW ────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = 'dark'
        self.current_lang = 'en'
        self.setWindowTitle("SURVIVOR")
        self.setMinimumSize(640, 480)
        self.resize(1100, 680)
        self._build_ui()
        self._apply_theme()

    def t(self, key):
        return TR[self.current_lang].get(key, key)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── top bar ──
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(46)
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(10, 4, 10, 4)
        top_layout.setSpacing(8)

        self.title_label = QLabel("SURVIVOR")
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Black))
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()

        # lang combo
        self.lang_label = QLabel(self.t('lang') + ":")
        top_layout.addWidget(self.lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "中文", "فارسی"])
        self.lang_combo.setFixedWidth(90)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        top_layout.addWidget(self.lang_combo)

        # theme combo
        self.theme_label = QLabel(self.t('theme') + ":")
        top_layout.addWidget(self.theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([self.t('dark'), self.t('light')])
        self.theme_combo.setFixedWidth(80)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        top_layout.addWidget(self.theme_combo)

        main_layout.addWidget(self.top_bar)

        # ── canvas ──
        self.canvas = GameCanvas()
        self.canvas.state_changed.connect(self._on_state_changed)
        self.canvas.score_updated.connect(self._on_score_updated)
        self.canvas.levelup_signal.connect(self._on_levelup)
        main_layout.addWidget(self.canvas, stretch=1)

        # ── bottom bar ──
        self.bottom_bar = QWidget()
        self.bottom_bar.setFixedHeight(52)
        bot_layout = QHBoxLayout(self.bottom_bar)
        bot_layout.setContentsMargins(10, 6, 10, 6)
        bot_layout.setSpacing(8)

        self.btn_start   = self._make_btn(self.t('start'),   self._on_start)
        self.btn_resume  = self._make_btn(self.t('resume'),  self._on_resume)
        self.btn_restart = self._make_btn(self.t('restart'), self._on_restart)
        self.btn_quit    = self._make_btn(self.t('quit'),    self.close)

        for btn in [self.btn_start, self.btn_resume, self.btn_restart, self.btn_quit]:
            bot_layout.addWidget(btn)

        bot_layout.addStretch()

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        bot_layout.addWidget(self.status_label)

        main_layout.addWidget(self.bottom_bar)

        self._refresh_buttons('idle')

    def _make_btn(self, text, slot):
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setMinimumWidth(90)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def _refresh_buttons(self, state):
        self.btn_start.setVisible(state == 'idle')
        self.btn_resume.setVisible(state == 'paused')
        self.btn_restart.setVisible(state in ('paused', 'gameover', 'victory'))
        self.btn_quit.setVisible(True)

    def _on_start(self):
        self.canvas.start_game()

    def _on_resume(self):
        if self.canvas.state == 'paused':
            self.canvas.state = 'playing'
            self.canvas.state_changed.emit('playing')
            self.canvas.setFocus()

    def _on_restart(self):
        self.canvas.start_game()

    def _on_state_changed(self, state):
        self._refresh_buttons(state)
        messages = {
            'playing': '',
            'paused':  self.t('paused'),
            'gameover':self.t('game_over'),
            'victory': self.t('victory'),
            'idle':    '',
        }
        self.status_label.setText(messages.get(state, ''))

    def _on_score_updated(self, score):
        if self.canvas.player:
            self.status_label.setText(f"{self.t('score')}: {score}   {self.t('kills')}: {self.canvas.player.kills}")

    def _on_levelup(self, lv):
        self.status_label.setText(f"✦ {self.t('lvlup')} Lv.{lv} ✦")

    def _on_lang_changed(self, idx):
        langs = ['en', 'zh', 'fa']
        self.current_lang = langs[idx]
        self.canvas.set_lang(self.current_lang)
        self._update_texts()
        self._apply_theme()

    def _on_theme_changed(self, idx):
        self.current_theme = 'dark' if idx == 0 else 'light'
        self.canvas.set_theme(self.current_theme)
        self._apply_theme()

    def _update_texts(self):
        self.title_label.setText(self.t('title'))
        self.lang_label.setText(self.t('lang') + ":")
        self.theme_label.setText(self.t('theme') + ":")
        self.btn_start.setText(self.t('start'))
        self.btn_resume.setText(self.t('resume'))
        self.btn_restart.setText(self.t('restart'))
        self.btn_quit.setText(self.t('quit'))
        # refresh theme combo items with new language
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItems([self.t('dark'), self.t('light')])
        self.theme_combo.setCurrentIndex(0 if self.current_theme == 'dark' else 1)
        self.theme_combo.blockSignals(False)

    def _apply_theme(self):
        th = THEMES[self.current_theme]
        is_dark = self.current_theme == 'dark'

        accent  = th['accent']
        bg      = th['bg']
        panel   = th['panel']
        text    = th['text']
        sub     = th['sub']
        btn_col = th['btn']
        btn_h   = th['btn_hover']

        qss = f"""
        QMainWindow, QWidget {{
            background-color: {bg};
            color: {text};
            font-family: Arial;
        }}
        QLabel {{
            color: {text};
            background: transparent;
        }}
        QPushButton {{
            background-color: {btn_col};
            color: {text};
            border: 1px solid {accent};
            border-radius: 6px;
            padding: 4px 12px;
            font-weight: bold;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: {btn_h};
            color: #ffffff;
            border: 1px solid {btn_h};
        }}
        QPushButton:pressed {{
            background-color: {accent};
        }}
        QComboBox {{
            background-color: {panel};
            color: {text};
            border: 1px solid {sub};
            border-radius: 5px;
            padding: 2px 6px;
            font-size: 11px;
        }}
        QComboBox:hover {{
            border: 1px solid {accent};
        }}
        QComboBox QAbstractItemView {{
            background-color: {panel};
            color: {text};
            selection-background-color: {btn_col};
            border: 1px solid {accent};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 18px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {text};
            margin-right: 4px;
        }}
        """
        self.setStyleSheet(qss)

        # top/bottom bar special bg
        bar_style = f"background-color: {panel}; border-bottom: 1px solid {sub};"
        bot_style = f"background-color: {panel}; border-top: 1px solid {sub};"
        self.top_bar.setStyleSheet(bar_style)
        self.bottom_bar.setStyleSheet(bot_style)
        self.title_label.setStyleSheet(f"color: {accent}; font-size: 16px; font-weight: 900; background: transparent;")
        self.status_label.setStyleSheet(f"color: {sub}; background: transparent;")


# ─── ENTRY POINT ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
