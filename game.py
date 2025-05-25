import pgzrun
from random import randint
from pygame import Rect

WIDTH = 800
HEIGHT = 480
TITLE = "Super Popó"
GRAVITY = 0.5

game_state = 'menu'
sound_on = True
menu_music_playing = False
camera_offset = 0

invincible_timer = 0

hero = Actor('hero_idle1')
hero.hp = 6
hero.midbottom = (100, 400)
hero.vy = 0
hero.on_ground = False
hero.direction = 'right'
hero.anim_index = 0
hero.world_x = hero.x

enemies = []
animation_timer = 0
music.set_volume(0.3)

tile_parts = ['tile_0000', 'tile_0001', 'tile_0002', 'tile_0003']
platforms = []

for i in range(0, WIDTH * 5, 64):
    if i == 512 or i == 1280:
        continue
    elif 896 <= i <= 1152:
        platforms.append(Rect(i, 300, 64, 64))
    elif 1792 <= i <= 1984:
        platforms.append(Rect(i, 350, 64, 64))
    else:
        platforms.append(Rect(i, 400, 64, 64))

def draw_tile(x, y):
    for i, part in enumerate(tile_parts):
        screen.blit(part, (x + i * 16, y))

def draw():
    screen.clear()
    if game_state == 'menu':
        draw_menu()
    elif game_state == 'game':
        draw_game()
    elif game_state == 'gameover':
        draw_gameover()
    elif game_state == 'victory':
        draw_victory()

def draw_menu():
    screen.draw.text("Super Popó World", center=(WIDTH // 2, 100), fontsize=50)
    screen.draw.textbox("Começar o jogo", Rect(300, 200, 200, 50))
    sound_text = "Música e sons ligados" if sound_on else "Música e sons desligados"
    screen.draw.textbox(sound_text, Rect(300, 270, 200, 50))
    screen.draw.textbox("Saída", Rect(300, 340, 200, 50))

def draw_game():
    screen.fill((100, 200, 255))
    for plat in platforms:
        draw_tile(plat.x - camera_offset, plat.y)
    for enemy in enemies:
        screen.blit(enemy.image, (enemy.x - camera_offset, enemy.y))
    screen.blit(hero.image, (hero.x, hero.y))
    draw_hearts()
    enemy_count = len(enemies)
    screen.draw.text(f"Inimigos restantes: {enemy_count}", topright=(WIDTH - 10, 10), fontsize=30, color="black")

def draw_hearts():
    for i in range(3):
        heart_x = 10 + i * 40
        if hero.hp >= (i + 1) * 2:
            screen.blit('full_heart', (heart_x, 10))
        elif hero.hp == (i * 2 + 1):
            screen.blit('midheart', (heart_x, 10))
        else:
            screen.blit('without_heart', (heart_x, 10))

def draw_victory():
    screen.draw.text("Você venceu!", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="green")
    screen.draw.text("Pressione Enter para voltar ao menu", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30)

def draw_gameover():
    screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
    screen.draw.text("Pressione Enter para voltar ao menu", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30)

def update(dt):
    global animation_timer, invincible_timer, menu_music_playing, game_state
    if game_state == 'menu':
        if not menu_music_playing:
            music.stop()
            if sound_on:
                music.play('menu')
            menu_music_playing = True
    if game_state == 'game':
        update_hero()
        update_enemies()
        animation_timer += dt
        if animation_timer > 0.2:
            animate_hero()
            animate_enemies()
            animation_timer = 0
        if invincible_timer > 0:
            invincible_timer -= 1
    if game_state == 'game' and not enemies:
        game_state = 'victory'
        music.stop()
        if sound_on:
            sounds.victory.play()

def find_safe_spawn():
    for plat in platforms:
        if plat.left <= 100 <= plat.right and plat.top == 400:
            return plat
    return Rect(100, 400, 64, 64)

def update_hero():
    global camera_offset, gameover_played
    hero.vy += 1
    hero.y += hero.vy
    hero.on_ground = False

    for plat in platforms:
        hero_rect = Rect(hero.world_x - hero.width / 2, hero.y - hero.height / 2, hero.width, hero.height)
        if hero_rect.colliderect(plat) and hero.vy >= 0:
            if hero_rect.bottom - hero.vy <= plat.top:
                hero.y = plat.top - hero.height / 2
                hero.vy = 0
                hero.on_ground = True
    if keyboard.left:
        hero.world_x -= 3
        hero.direction = 'left'
    elif keyboard.right:
        hero.world_x += 3
        hero.direction = 'right'
    hero_rect = Rect(hero.world_x - hero.width / 2, hero.y - hero.height / 2, hero.width, hero.height)
    for enemy in enemies[:]:
        enemy_rect = Rect(enemy.x - enemy.width / 2, enemy.y - enemy.height / 2, enemy.width, enemy.height)
        if hero_rect.colliderect(enemy_rect):
            if hero.vy > 0 and hero_rect.bottom <= enemy_rect.top + 10:
                enemies.remove(enemy)
                hero.vy = -10
                if sound_on:
                    sounds.hit.play()
            else:
                take_damage()
    if hero.world_x > camera_offset + WIDTH // 2:
        camera_offset = hero.world_x - WIDTH // 2
    elif hero.world_x < camera_offset + WIDTH // 2 and camera_offset > 0:
        camera_offset = max(0, hero.world_x - WIDTH // 2)
    max_camera_offset = WIDTH * 5 - WIDTH
    camera_offset = min(camera_offset, max_camera_offset)
    hero.x = hero.world_x - camera_offset
    if camera_offset == 0 and hero.world_x < 32:
        hero.world_x = 32
        hero.x = hero.world_x - camera_offset
    max_world_x = WIDTH * 5 - 32
    if hero.world_x > max_world_x:
        hero.world_x = max_world_x
        hero.x = hero.world_x - camera_offset
    if hero.y > HEIGHT:
        hero.hp = 1
        take_damage()

def animate_hero():
    hero.anim_index = (hero.anim_index + 1) % 4
    if not hero.on_ground:
        hero.image = 'hero_jump'
    elif keyboard.left or keyboard.right:
        hero.image = f'hero_run{hero.anim_index + 1}'
    else:
        hero.image = f'hero_idle{hero.anim_index + 1}'

def update_enemies():
    for enemy in enemies:
        enemy.y += GRAVITY
        on_platform = False
        for plat in platforms:
            if enemy.colliderect(plat) and enemy.y + enemy.height // 2 <= plat.top + 10:
                enemy.bottom = plat.top
                on_platform = True
                break
        if not on_platform:
            continue
        enemy_bottom = enemy.y + enemy.height // 2
        next_x = enemy.x + enemy.vx
        has_floor = any(p.collidepoint(next_x, enemy_bottom + 1) for p in platforms)
        if not has_floor or next_x < enemy.left_bound or next_x > enemy.right_bound:
            enemy.vx *= -1
        else:
            enemy.x = next_x

def animate_enemies():
    for enemy in enemies:
        enemy.image = f'enemy_idle{randint(1, 2)}'

def on_mouse_down(pos):
    global game_state, sound_on, menu_music_playing
    if game_state == 'menu':
        if Rect(300, 200, 200, 50).collidepoint(pos):
            game_state = 'game'
            menu_music_playing = False
            music.stop()
            if sound_on:
                music.play('intro')
            spawn_enemies()
        elif Rect(300, 270, 200, 50).collidepoint(pos):
            sound_on = not sound_on
            if not sound_on:
                music.stop()
            else:
                if game_state == 'menu':
                    if sound_on:
                        music.play('menu')
        elif Rect(300, 340, 200, 50).collidepoint(pos):
            exit()

def on_key_down(key):
    global game_state, menu_music_playing
    if game_state == 'game' and key == keys.SPACE and hero.on_ground:
        hero.vy = -15
        if sound_on:
            sounds.jump.play()
    elif game_state in ['gameover', 'victory'] and key == keys.RETURN:
        game_state = 'menu'
        menu_music_playing = False
        reset_game()

def spawn_enemies():
    enemies.clear()
    valid_platforms = [plat for plat in platforms if plat.width >= 64]
    for _ in range(10):
        plat = valid_platforms[randint(0, len(valid_platforms) - 1)]
        e = Actor('enemy_idle1')
        e.midbottom = (plat.centerx, plat.top)
        e.left_bound = plat.left + 16
        e.right_bound = plat.right - 16
        e.vx = randint(1, 2) * (1 if randint(0, 1) == 0 else -1)
        enemies.append(e)

def take_damage():
    global invincible_timer, game_state
    if invincible_timer <= 0:
        hero.hp -= 1
        invincible_timer = 60
        if sound_on:
            sounds.damage.play()
        if hero.direction == 'right':
            hero.world_x -= 15
        else:
            hero.world_x += 15
        hero.vy = -5
        if hero.hp <= 0:
            music.stop()
            if sound_on:
                sounds.gameover.play()
            game_state = 'gameover'

def reset_game():
    global game_state, camera_offset
    music.stop()
    safe_plat = find_safe_spawn()
    hero.world_x = safe_plat.centerx
    hero.y = safe_plat.top - hero.height / 2
    hero.vy = 0
    hero.hp = 6
    hero.on_ground = True
    camera_offset = 0

    spawn_enemies()
    game_state = 'menu'

pgzrun.go()
