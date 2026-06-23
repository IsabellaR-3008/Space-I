import math
import random
import pygame

pygame.init()
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Dodge: Ultimate Arcade Upgrade")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)
title_font = pygame.font.SysFont(None, 64)
large_font = pygame.font.SysFont(None, 48)

INTRO, PLAYING, GAMEOVER = 0, 1, 2

starfield = [
    {
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "size": random.uniform(1, 3),
        "speed": random.uniform(0.3, 1.4),
    }
    for _ in range(160)
]

intro_particles = [
    {
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "size": random.uniform(2, 5),
        "speed": random.uniform(0.8, 2.6),
        "angle": random.uniform(0, math.tau),
    }
    for _ in range(120)
]


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def hsv_to_rgb(h, s, v):
    return tuple(round(i * 255) for i in pygame.Color(0).hsva_to_rgba(h, s, v, 100)[:3])


class Player:
    def __init__(self):
        self.x = WIDTH * 0.5
        self.y = HEIGHT * 0.8
        self.radius = 18
        self.base_speed = 5.4
        self.speed = self.base_speed
        self.trail = []
        self.color = (255, 255, 255)

    def update(self, keys, level):
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 or dy != 0:
            self.trail.insert(0, (self.x, self.y))
        self.trail = self.trail[:20]

        factor = 1 + (level - 1) * 0.085
        step = self.base_speed * factor
        self.x += dx * step
        self.y += dy * step
        self.x = clamp(self.x, self.radius, WIDTH - self.radius)
        self.y = clamp(self.y, self.radius, HEIGHT - self.radius)

    def draw(self, surface):
        trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for index, (tx, ty) in enumerate(self.trail):
            alpha = max(16, 180 - index * 8)
            radius = self.radius + (len(self.trail) - index) * 0.75
            pygame.draw.circle(trail_surface, (100, 200, 255, alpha), (int(tx), int(ty)), int(radius))
        surface.blit(trail_surface, (0, 0))

        points = [
            (self.x, self.y - self.radius),
            (self.x - self.radius * 0.7, self.y + self.radius * 0.9),
            (self.x + self.radius * 0.7, self.y + self.radius * 0.9),
        ]
        pygame.draw.polygon(surface, (255, 255, 255), points)
        pygame.draw.circle(surface, (50, 180, 255), (int(self.x), int(self.y)), self.radius // 2)


class Enemy:
    def __init__(self, level, tick):
        self.radius = random.randint(18, 45)
        self.x = random.uniform(self.radius, WIDTH - self.radius)
        self.y = -self.radius * 2
        self.speed = random.uniform(2.4, 4.2) + level * 0.4
        self.hue = random.uniform(0, 360)
        self.offset = random.uniform(0, math.tau)
        self.oscillation = random.uniform(0.5, 1.6)
        self.spawn_tick = tick

    def update(self, tick):
        self.y += self.speed
        self.x += math.sin(tick * 0.018 + self.offset) * self.oscillation
        self.color = pygame.Color(0)
        self.color.hsva = ((self.hue + tick * 0.12) % 360, 100, 100, 100)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)

    def off_screen(self):
        return self.y - self.radius > HEIGHT + 20

    def collides_with(self, player):
        distance = math.hypot(self.x - player.x, self.y - player.y)
        return distance < self.radius + player.radius * 0.8


def draw_starfield(surface, tick, ambient=True):
    for star in starfield:
        star["y"] += star["speed"] * 0.35
        star["x"] += math.sin(tick * 0.01 + star["y"] * 0.02) * 0.1
        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.uniform(0, WIDTH)
        shade = int(200 - star["size"] * 50)
        pygame.draw.circle(surface, (shade, shade, shade), (int(star["x"]), int(star["y"])), int(star["size"]))

    if not ambient:
        for particle in intro_particles:
            particle["x"] += math.cos(particle["angle"]) * particle["speed"] * 0.2
            particle["y"] += math.sin(particle["angle"]) * particle["speed"] * 0.2
            particle["angle"] += 0.005
            if particle["x"] < 0 or particle["x"] > WIDTH or particle["y"] < 0 or particle["y"] > HEIGHT:
                particle["x"] = random.uniform(0, WIDTH)
                particle["y"] = random.uniform(0, HEIGHT)
            color = (120, 180, 255)
            pygame.draw.circle(surface, color, (int(particle["x"]), int(particle["y"])), int(particle["size"]))


def draw_text(surface, text, size, x, y, color=(255, 255, 255), center=False):
    label = pygame.font.SysFont(None, size).render(text, True, color)
    rect = label.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(label, rect)


def draw_intro_screen(tick):
    WIN.fill((6, 6, 18))
    draw_starfield(WIN, tick, ambient=False)
    pygame.draw.rect(WIN, (10, 10, 30), (60, 80, WIDTH - 120, HEIGHT - 160), border_radius=18)

    title = title_font.render("Space Dodge: Ultimate Upgrade", True, (255, 255, 255))
    WIN.blit(title, ((WIDTH - title.get_width()) // 2, 120))

    draw_text(WIN, "Press SPACE to launch into the particle field.", 32, WIDTH // 2, 240, center=True)
    draw_text(WIN, "Dynamic levels. Rainbow enemies. Speed progression. Motion blur aura.", 28, WIDTH // 2, 300, color=(180, 220, 255), center=True)
    draw_text(WIN, "Use arrow keys or WASD to dodge. Survive as long as possible.", 28, WIDTH // 2, 340, color=(180, 220, 255), center=True)
    draw_text(WIN, "Ready for deep space?", 28, WIDTH // 2, 420, color=(255, 190, 80), center=True)

    prompt = large_font.render("SPACE - Launch", True, (255, 255, 255))
    WIN.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT - 140))


def draw_game_over(surface, score, level):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))
    draw_text(surface, "MISSION FAILED", 60, WIDTH // 2, HEIGHT // 2 - 90, center=True)
    draw_text(surface, f"Max Level: {level}", 38, WIDTH // 2, HEIGHT // 2 - 10, center=True)
    draw_text(surface, f"Survival Time: {score:.1f}s", 34, WIDTH // 2, HEIGHT // 2 + 40, center=True)
    draw_text(surface, "Press R to retry or Q to quit.", 30, WIDTH // 2, HEIGHT // 2 + 100, center=True)


def main():
    running = True
    state = INTRO
    player = Player()
    enemies = []
    score = 0.0
    tick = 0
    spawn_timer = 0
    level = 1

    while running:
        delta = clock.tick(60) / 1000.0
        tick += 1
        if state == PLAYING:
            score += delta
            level = 1 + min(int(score // 15), 8)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == INTRO and event.key == pygame.K_SPACE:
                    state = PLAYING
                    player = Player()
                    enemies.clear()
                    score = 0.0
                    tick = 0
                    spawn_timer = 0
                    level = 1
                elif state == GAMEOVER:
                    if event.key == pygame.K_r:
                        state = PLAYING
                        player = Player()
                        enemies.clear()
                        score = 0.0
                        tick = 0
                        spawn_timer = 0
                        level = 1
                    elif event.key == pygame.K_q:
                        running = False

        keys = pygame.key.get_pressed()

        WIN.fill((5, 5, 18))
        draw_starfield(WIN, tick, ambient=True)

        if state == INTRO:
            draw_intro_screen(tick)
        elif state == PLAYING:
            player.update(keys, level)

            spawn_interval = max(26, 90 - level * 8)
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                enemies.append(Enemy(level, tick))

            enemies = [enemy for enemy in enemies if not enemy.off_screen()]
            for enemy in enemies:
                enemy.update(tick)
                enemy.draw(WIN)
                if enemy.collides_with(player):
                    state = GAMEOVER

            player.draw(WIN)

            draw_text(WIN, f"Time: {score:.1f}s", 26, 18, 16)
            draw_text(WIN, f"Level: {level}", 26, WIDTH - 150, 16)
            draw_text(WIN, f"Enemies: {len(enemies)}", 26, WIDTH - 150, 46)

            if score > 0:
                progress = min(1.0, (score % 15) / 15)
                bar_width = int((WIDTH - 60) * progress)
                pygame.draw.rect(WIN, (40, 40, 80), (30, HEIGHT - 40, WIDTH - 60, 18), border_radius=9)
                pygame.draw.rect(WIN, (100, 230, 255), (30, HEIGHT - 40, bar_width, 18), border_radius=9)
                draw_text(WIN, "Level surge", 22, WIDTH // 2, HEIGHT - 36, color=(220, 255, 255), center=True)
        elif state == GAMEOVER:
            draw_game_over(WIN, score, level)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()


if __name__ == '__main__':
    main()