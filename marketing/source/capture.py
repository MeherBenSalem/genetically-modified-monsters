#!/usr/bin/env python3
"""Takes the listing screenshots and GIFs in marketing/images/ from a running QA server and client.

Start them first (1.21.1, Fabric or NeoForge) on a FRESH QA world (seed `spore-and-stem`, so every chunk is generated
with the mod's worldgen):

    tools/qa/prepare_runs.sh 1.21.1 fabric tools/qa/options.txt
    Xvfb :1 -screen 0 1920x1080x24 &
    DISPLAY=:1 tools/qa/devrun.sh start-server 1.21.1 fabric
    DISPLAY=:1 tools/qa/devrun.sh start-client 1.21.1 fabric

then run `DISPLAY=:1 python3 marketing/source/capture.py [scene...]` (`studio` first: it builds the sets).
Staged scenes are built on two flat studio plateaus in the plains south of spawn (x 0..95, z 380..427, y 80) from the
mod's own worldgen features (`/place feature`) and blocks; natural scenes use generated terrain at the coordinates
below. Actors are summoned with NoAI so they hold still; natural spawning, weather and the daylight cycle are off.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage import PLAYER, WORK, cmd, contact, grab, place, record, s, setup, shot, still, surface, view  # noqa: E402

Y = 80                       # studio floor
GLADE = (0, 380)             # 48x48: glowcap glade (north half) and bouncecap meadow (south half)
YARD = (48, 380)             # 48x48: the fungal-wood cottage, displays, farm and creature line-ups


def plateau(x0, z0, size=48):
    """Flattens a size x size square at y=80: dirt below, grass on top, air above."""
    cmd(f'forceload add {x0} {z0} {x0 + size - 1} {z0 + size - 1}')
    for tx in range(x0, x0 + size, 16):
        for tz in range(z0, z0 + size, 16):
            cmd(f'fill {tx} 55 {tz} {tx + 15} {Y - 1} {tz + 15} minecraft:dirt',
                f'fill {tx} {Y} {tz} {tx + 15} {Y} {tz + 15} minecraft:grass_block',
                f'fill {tx} {Y + 1} {tz} {tx + 15} {Y + 60} {tz + 15} minecraft:air')


def scatter(block, n, x0, x1, z0, z1, seed, on='minecraft:air'):
    rng = random.Random(seed)
    for _ in range(n):
        x, z = rng.randint(x0, x1), rng.randint(z0, z1)
        cmd(f'execute if block {x} {Y + 1} {z} {on} run setblock {x} {Y + 1} {z} {block}')


# ---------------------------------------------------------------------------------------------------- sets

def grotto():
    """A cave set at the back of the yard: veils with bulbs, glowcap gills, glowcaps, emberstools by a lava seep,
    a shelf-fungus stump and a giant puffball. Open to the south for the camera."""
    rng = random.Random(21)
    cmd('fill 79 80 381 95 91 399 minecraft:stone', 'fill 80 81 382 94 88 399 minecraft:air',
        'fill 80 80 382 94 80 398 minecraft:moss_block', 'fill 80 81 399 94 91 399 minecraft:air')
    for _ in range(26):  # an uneven ceiling and walls
        x, z = rng.randint(80, 94), rng.randint(382, 396)
        cmd(f'fill {x} {rng.randint(86, 88)} {z} {x + rng.randint(0, 2)} 88 {z + rng.randint(0, 2)} minecraft:stone')
    for _ in range(18):  # rock bulging in from the sides and the back
        side = rng.choice(('w', 'e', 'n'))
        y0, y1 = rng.randint(81, 85), rng.randint(85, 88)
        if side == 'w':
            z = rng.randint(382, 398)
            cmd(f'fill 80 {y0} {z} {80 + rng.randint(0, 2)} {y1} {z + rng.randint(0, 2)} minecraft:stone')
        elif side == 'e':
            z = rng.randint(382, 398)
            cmd(f'fill {94 - rng.randint(0, 2)} {y0} {z} 94 {y1} {z + rng.randint(0, 2)} minecraft:stone')
        else:
            x = rng.randint(80, 92)
            cmd(f'fill {x} {y0} 382 {x + rng.randint(0, 2)} {y1} {382 + rng.randint(0, 2)} minecraft:stone')
    cmd('fill 79 85 399 95 91 399 minecraft:stone', 'fill 79 81 399 81 85 399 minecraft:stone', 'fill 93 81 399 95 85 399 minecraft:stone')
    for _ in range(10):
        x, z = rng.randint(80, 94), rng.randint(383, 397)
        cmd(f'setblock {x} 80 {z} minecraft:mycelium', f'setblock {x + 1} 80 {z} spore_and_stem:mycelial_soil')
    for (x, z, n) in ((83, 388, 4), (86, 385, 3), (90, 390, 5), (92, 386, 3), (88, 393, 2), (84, 395, 3)):
        top = 88
        for y in range(top, top - 8, -1):
            if 'passed' in cmd(f'execute if block {x} {y} {z} minecraft:air'):
                top = y
                break
        for k in range(n):
            y = top - k
            last = k == n - 1
            bulb = 'true' if rng.random() < 0.45 or last else 'false'
            block = 'mycelial_veil' if last else 'mycelial_veil_plant'
            cmd(f'setblock {x} {y} {z} spore_and_stem:{block}[bulb={bulb}]')
    for (x, z) in ((81, 384), (82, 384), (93, 392), (93, 393), (88, 383)):
        cmd(f'execute if block {x} 88 {z} minecraft:air run setblock {x} 88 {z} minecraft:stone')
        cmd(f'setblock {x} 87 {z} spore_and_stem:glowcap_gills')
    cmd('setblock 91 80 396 minecraft:lava', 'setblock 92 80 396 minecraft:lava', 'setblock 91 81 397 minecraft:air')
    for (x, z) in ((90, 395), (93, 395), (90, 397), (93, 397), (92, 398)):
        cmd(f'setblock {x} 81 {z} spore_and_stem:emberstool')
    scatter('spore_and_stem:glowcap', 9, 82, 92, 383, 394, 22)
    cmd('fill 82 81 391 82 82 391 minecraft:oak_log', 'setblock 83 81 391 spore_and_stem:shelf_fungus[facing=east,shelves=3]',
        'setblock 82 82 392 spore_and_stem:shelf_fungus[facing=south,shelves=2]', 'setblock 86 81 389 spore_and_stem:giant_puffball',
        'setblock 85 81 396 spore_and_stem:inkcap', 'setblock 84 81 397 spore_and_stem:deathcap', 'setblock 89 81 398 spore_and_stem:frostcap')


def grotto_shot():
    clear_actors()
    night(18000)
    for (x, y, z, yaw) in ((86.5, 84.6, 391.5, 30), (90.0, 85.2, 389.0, -40), (88.2, 83.6, 394.0, 160)):
        still('spore_and_stem:glowmoth', x, y, z, yaw)
    still('spore_and_stem:sporeling', 86.8, 81, 392.2, 200, ',Variant:"glowcap"')
    view(86.2, 81.8, 398.2, 88.5, 83.2, 388, wait=6)
    shot('glowcap-grotto')


def build_glade():
    gx, gz = GLADE
    plateau(gx, gz)
    cmd('fill 2 80 381 45 80 404 minecraft:mycelium')
    for (x, z, r, b) in ((8, 396, 3, 'minecraft:podzol'), (30, 390, 2, 'spore_and_stem:mycelial_soil'), (40, 400, 3, 'minecraft:moss_block'),
                         (18, 385, 2, 'minecraft:podzol'), (24, 402, 2, 'minecraft:moss_block')):
        cmd(f'fill {x - r} 80 {z - r} {x + r} 80 {z + r} {b} replace minecraft:mycelium')
    for x in range(1, 47, 5):
        cmd(f'place feature minecraft:spruce {x} 81 381')
    for z in range(386, 405, 6):
        cmd(f'place feature minecraft:spruce 1 81 {z}', f'place feature minecraft:spruce 46 81 {z}')
    for (x, z) in ((12, 392), (25, 387), (36, 395), (19, 399)):
        place('huge_glowcap', x, 81, z)
    scatter('spore_and_stem:glowcap', 40, 4, 43, 383, 404, 7)
    # The south half: a bouncecap meadow with puffballs, flowers and a fairy ring, inkcaps at the edges.
    for (x, z) in ((10, 414), (34, 418), (22, 424)):
        place('huge_bouncecap', x, 81, z)
    for (x, z) in ((44, 410), (3, 425)):
        place('huge_inkcap', x, 81, z)
    for b, n, seed in (('spore_and_stem:bouncecap', 18, 11), ('spore_and_stem:puffball', 8, 12), ('minecraft:poppy', 10, 13),
                       ('minecraft:oxeye_daisy', 10, 14), ('minecraft:cornflower', 8, 15), ('minecraft:short_grass', 40, 16)):
        scatter(b, n, 3, 44, 407, 426, seed)
    for (x, z) in ((7, 420), (8, 420), (7, 421)):
        cmd(f'setblock {x} 81 {z} spore_and_stem:giant_puffball')
    for i in range(12):  # a fairy ring of chanterelles
        import math
        a = i * math.tau / 12
        x, z = round(26 + math.cos(a) * 4), round(414 + math.sin(a) * 4)
        cmd(f'setblock {x} 81 {z} spore_and_stem:chanterelle')


def build_yard():
    yx, yz = YARD
    plateau(yx, yz)
    for x in range(yx, yx + 48, 6):
        cmd(f'place feature minecraft:spruce {x} 81 {yz}')
    cottage(60, 386)
    displays()
    farm()
    grotto()


def cottage(x0, z0):
    """A small cottage of the three fungal woods: glowcap frame, inkcap planks, bouncecap roof and trim."""
    w, d = 9, 7
    x1, z1 = x0 + w - 1, z0 + d - 1
    cmd(f'fill {x0} 81 {z0} {x1} 81 {z1} spore_and_stem:glowcap_planks',
        f'fill {x0} 82 {z0} {x1} 85 {z1} spore_and_stem:inkcap_planks hollow',
        f'fill {x0 + 1} 82 {z0 + 1} {x1 - 1} 85 {z1 - 1} minecraft:air')
    for x, z in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        cmd(f'fill {x} 81 {z} {x} 85 {z} spore_and_stem:glowcap_stem')
    cmd(f'fill {x0} 86 {z0} {x1} 86 {z1} spore_and_stem:stripped_glowcap_hyphae')
    # Roof: bouncecap stairs on both slopes, cap blocks on the ridge.
    for i in range(4):
        cmd(f'fill {x0 - 1} {87 + i} {z0 - 1 + i} {x1 + 1} {87 + i} {z0 - 1 + i} spore_and_stem:bouncecap_stairs[facing=south]',
            f'fill {x0 - 1} {87 + i} {z1 + 1 - i} {x1 + 1} {87 + i} {z1 + 1 - i} spore_and_stem:bouncecap_stairs[facing=north]')
    cmd(f'fill {x0 - 1} 91 {z0 + 3} {x1 + 1} 91 {z0 + 3} spore_and_stem:bouncecap_slab')
    for z in range(z0, z1 + 1):
        for y in range(87, 91):
            cmd(f'setblock {x0} {y} {z} spore_and_stem:inkcap_planks keep', f'setblock {x1} {y} {z} spore_and_stem:inkcap_planks keep')
    # Door, windows and a lantern porch.
    mid = x0 + w // 2
    cmd(f'setblock {mid} 82 {z1} spore_and_stem:glowcap_door[facing=south,half=lower]',
        f'setblock {mid} 83 {z1} spore_and_stem:glowcap_door[facing=south,half=upper]',
        f'setblock {mid - 2} 83 {z1} spore_and_stem:inkcap_trapdoor[facing=south,open=true,half=top]',
        f'setblock {mid + 2} 83 {z1} spore_and_stem:inkcap_trapdoor[facing=south,open=true,half=top]',
        f'setblock {mid - 1} 85 {z1 + 1} spore_and_stem:glowcap_lantern[hanging=true]',
        f'setblock {mid + 1} 85 {z1 + 1} spore_and_stem:glowcap_lantern[hanging=true]',
        f'fill {mid - 1} 85 {z1 + 1} {mid + 1} 85 {z1 + 1} spore_and_stem:bouncecap_slab[type=top] keep',
        f'fill {x0 - 1} 81 {z1 + 2} {x1 + 1} 81 {z1 + 2} spore_and_stem:bouncecap_fence',
        f'setblock {mid} 81 {z1 + 2} spore_and_stem:bouncecap_fence_gate[facing=south]',
        f'fill {x0} 81 {z1 + 1} {x1} 81 {z1 + 1} minecraft:air')
    for x in (x0 + 1, x0 + 3, x1 - 3, x1 - 1):
        cmd(f'setblock {x} 81 {z1 + 1} spore_and_stem:potted_{random.Random(x).choice(["glowcap", "bouncecap", "chanterelle", "frostcap"])}')


def displays():
    """The nine small fungi in a 3x3 bed of mycelial soil, and their potted forms on a moss shelf behind."""
    fungi = ['glowcap', 'bouncecap', 'inkcap', 'morel', 'chanterelle', 'deathcap', 'frostcap', 'emberstool', 'puffball']
    cmd('fill 54 80 403 60 80 409 minecraft:moss_block', 'fill 53 81 401 61 81 401 minecraft:moss_block')
    for i, f in enumerate(fungi):
        cmd(f'setblock {55 + (i % 3) * 2} 81 {404 + (i // 3) * 2} spore_and_stem:{f}',
            f'setblock {53 + i} 82 401 spore_and_stem:potted_{f}')


def farm():
    """A shady farm: cultivation logs at every stage on mycelial soil, shelf fungus on a stump, veils on a frame."""
    cmd('fill 74 80 404 92 80 418 spore_and_stem:mycelial_soil', 'fill 73 81 403 93 81 403 minecraft:spruce_fence',
        'fill 73 81 419 93 81 419 minecraft:spruce_fence')
    fungi = ['glowcap', 'bouncecap', 'inkcap', 'morel', 'chanterelle', 'frostcap', 'emberstool']
    for row, f in enumerate(fungi):
        for stage in range(4):
            cmd(f'setblock {76 + stage * 4} 81 {405 + row * 2} spore_and_stem:cultivation_log[axis=x,fungus={f},stage={stage}]')
    # A stump with shelf fungus and a gill canopy hung from a frame.
    cmd('fill 70 81 412 70 84 412 minecraft:oak_log',
        'setblock 71 82 412 spore_and_stem:shelf_fungus[facing=east,shelves=3]',
        'setblock 70 83 413 spore_and_stem:shelf_fungus[facing=south,shelves=2]',
        'setblock 69 82 412 spore_and_stem:shelf_fungus[facing=west,shelves=3]')


def studio():
    setup()
    build_glade()
    build_yard()
    cmd('kill @e[type=item]')


# ---------------------------------------------------------------------------------------------------- scenes

def night(t=18000):
    cmd(f'time set {t}')


def clear_actors():
    for kind in ('sporeling', 'glowmoth', 'truffler', 'bloatshroom', 'shambler', 'sporemaw', 'mimicap', 'myceliarch', 'root_spike'):
        cmd(f'kill @e[type=spore_and_stem:{kind}]')
    cmd('kill @e[type=item]', 'kill @e[type=minecraft:experience_orb]')


def grove():
    clear_actors()
    for (x, z, yaw, v) in ((21.5, 401.5, 160, 'glowcap'), (23.8, 402.6, 200, 'glowcap'), (26.2, 400.8, 150, 'bouncecap'),
                           (28.6, 403.6, 205, 'inkcap')):
        still('spore_and_stem:sporeling', x, 81, z, yaw, f',Variant:"{v}"')
    for (x, y, z, yaw) in ((17.5, 85.2, 396.5, 30), (29.5, 86.4, 393.0, -40), (24.0, 84.0, 399.0, 10), (33.0, 84.8, 399.5, 60)):
        still('spore_and_stem:glowmoth', x, y, z, yaw)
    night()
    view(20.5, 81.4, 406.5, 26, 86, 389, wait=6)
    shot('glowcap-grove')


def giants():
    clear_actors()
    cmd('time set 2500')
    for (x, z, yaw, v) in ((33.5, 421.5, 150, 'bouncecap'), (35.8, 422.4, 200, 'bouncecap'), (31.2, 423.6, 170, 'chanterelle')):
        still('spore_and_stem:sporeling', x, 81, z, yaw, f',Variant:"{v}"')
    view(44, 82.5, 427.2, 24, 86, 405, wait=6)
    shot('giants-day')


def cottage_shot():
    clear_actors()
    cmd('time set 12600')
    still('spore_and_stem:sporeling', 62.5, 81, 395.5, 200, ',Variant:"glowcap"')
    view(70.5, 81.7, 401.5, 64, 84.2, 391.5, wait=6)
    shot('fungal-cottage')


def farm_shot():
    clear_actors()
    cmd('time set 6000')
    still('spore_and_stem:sporeling', 74.5, 81, 421.5, 200, ',Variant:"chanterelle"')
    view(85.5, 83.0, 419.5, 83.5, 81.2, 411, wait=5)
    shot('cultivation')


def friends():
    clear_actors()
    cmd('time set 4000')
    for (x, z, yaw, v) in ((13.5, 418.5, 200, 'glowcap'), (15.5, 419.2, 170, 'bouncecap'), (17.6, 418.6, 160, 'inkcap'),
                           (19.4, 419.6, 190, 'chanterelle')):
        still('spore_and_stem:sporeling', x, 81, z, yaw, f',Variant:"{v}"')
    still('spore_and_stem:truffler', 22.5, 81, 417.5, 140)
    still('spore_and_stem:glowmoth', 11.0, 83.6, 417.0, 220)
    view(16.8, 81.7, 422.8, 17.2, 81.5, 418.4, wait=5)
    shot('friends')


def foes():
    clear_actors()
    cmd('time set 12950')
    still('spore_and_stem:shambler', 10.5, 81, 401.5, 190)
    still('spore_and_stem:bloatshroom', 13.0, 81, 403.6, 170)
    still('spore_and_stem:sporemaw', 15.5, 81, 401.0, 210, ',Burrow:0')
    still('spore_and_stem:mimicap', 7.6, 81, 403.6, 160, ',Disguised:0b,Variant:0')
    view(11.5, 81.9, 408.4, 11.5, 82.0, 401.5, wait=6)
    shot('foes')


def boss():
    clear_actors()
    cmd('time set 12300')
    still('spore_and_stem:myceliarch', 62.5, 81, 419.5, 205)
    view(65.8, 81.2, 426.4, 62.5, 85.4, 419.5, wait=6)
    shot('myceliarch')


def boss_fight():
    """An iron golem picks a fight with the Myceliarch; the camera watches the attacks as a spectator. Writes frames
    (fight_NN.png) to the work folder to choose the card art from."""
    clear_actors()
    cmd('time set 12350', 'kill @e[type=minecraft:iron_golem]')
    cmd('summon spore_and_stem:myceliarch 28.5 81 415.5 {PersistenceRequired:1b}')
    time.sleep(6)  # let it rise
    cmd('summon minecraft:iron_golem 24.5 81 418.5 {PersistenceRequired:1b}',
        'effect give @e[type=minecraft:iron_golem] resistance 120 3 true', 'effect give @e[type=minecraft:iron_golem] regeneration 120 2 true')
    view(21.5, 82.6, 424.5, 27.5, 83.6, 416.0, wait=1)
    for i in range(24):
        time.sleep(1.0)
        grab(f'fight_{i:02d}', hud=False)
    cmd('kill @e[type=minecraft:iron_golem]')


def boss_duel():
    """First person: the Myceliarch fights the player (survival, Resistance IV and Regeneration so the camera
    survives). Frames duel_NN.png go to the work folder with the HUD and boss bar visible."""
    clear_actors()
    cmd('time set 12350', 'kill @e[type=minecraft:iron_golem]', f'gamemode survival {PLAYER}', f'effect clear {PLAYER}',
        f'effect give {PLAYER} resistance 300 3 true', f'effect give {PLAYER} regeneration 300 3 true',
        f'effect give {PLAYER} saturation 300 1 true', f'clear {PLAYER}',
        f'item replace entity {PLAYER} weapon.mainhand with spore_and_stem:bloomreaver',
        f'item replace entity {PLAYER} armor.head with spore_and_stem:crown_of_the_bloom')
    s().tp(26.5, 81, 424.5, facing=(26.5, 84.0, 413.5))
    time.sleep(2)
    cmd('summon spore_and_stem:myceliarch 26.5 81 413.5 {PersistenceRequired:1b}')
    for i in range(48):
        time.sleep(0.5)
        grab(f'duel_{i:02d}', hud=True)
    cmd(f'gamemode spectator {PLAYER}', f'effect clear {PLAYER}', f'clear {PLAYER}')
    clear_actors()


def summon_gif():
    """The real summoning: a Fruiting Heart used on mycelium, recorded while the ritual runs and the Myceliarch rises."""
    clear_actors()
    cmd('time set 12400', f'gamemode creative {PLAYER}', f'clear {PLAYER}', 'setblock 23 80 417 minecraft:mycelium',
        f'item replace entity {PLAYER} hotbar.0 with spore_and_stem:fruiting_heart')
    s().key('1')
    s().tp(23.5, 81, 421.6, facing=(23.5, 80.95, 417.5))
    time.sleep(3)
    s().hud(False)

    def go():
        s().click(3)
        time.sleep(0.4)
        s().tp(23.5, 81, 427.0, facing=(23.5, 83.4, 418.0))
        time.sleep(1.6)
    record('myceliarch-rises', 9.5, (1280, 720, 320, 150), 720, 14, go, skip=1.8)
    shot('myceliarch-risen')
    s().hud(True)
    cmd(f'gamemode spectator {PLAYER}', f'clear {PLAYER}')


def fields():
    clear_actors()
    cmd('time set 12900')
    view(1384, 96, 3112, 1344, 70, 3066, wait=14)
    shot('mushroom-fields')


def inventory():
    clear_actors()
    cmd(f'gamemode survival {PLAYER}', f'clear {PLAYER}', f'effect give {PLAYER} resistance 120 4 true', 'time set 6000')
    items = ['glowcap 12', 'bouncecap 8', 'inkcap 6', 'morel 16', 'chanterelle 16', 'deathcap 4', 'frostcap 8', 'emberstool 8',
             'puffball 9', 'lumen_spores 32', 'mycelial_thread 24', 'mycoleather 12', 'bouncecap_gel 10', 'truffle 7', 'mycelial_core 2',
             'fruiting_heart', 'spore_heart', 'glowcap_soup', 'truffle_stew', 'bouncecap_jelly 4', 'frostcap_tea 3', 'antifungal_tonic 2',
             'ember_skewer 6', 'cultivation_log 4', 'glowcap_lantern 6', 'shelf_fungus 12', 'mycelial_soil 32']
    for i, item in enumerate(items):
        cmd(f'item replace entity {PLAYER} inventory.{i} with spore_and_stem:{item}')
    for i, item in enumerate(['bloomreaver', 'foraging_knife', 'spore_bomb 16', 'glowcap_planks 64', 'bouncecap_planks 64',
                              'inkcap_planks 64', 'glowcap_cap 32', 'roasted_morel 12', 'chanterelle_toast 8']):
        cmd(f'item replace entity {PLAYER} hotbar.{i} with spore_and_stem:{item}')
    for slot, item in (('armor.head', 'crown_of_the_bloom'), ('armor.chest', 'mycoleather_tunic'), ('armor.legs', 'mycoleather_leggings'),
                       ('armor.feet', 'mycoleather_boots')):
        cmd(f'item replace entity {PLAYER} {slot} with spore_and_stem:{item}')
    view(20.5, 81, 406.5, 26, 86, 389, wait=8)
    s().key('e')
    time.sleep(1.5)
    s().move(1100, 470)
    time.sleep(0.6)
    shot('inventory', hud=True)
    s().key('Escape')
    cmd(f'gamemode spectator {PLAYER}', f'clear {PLAYER}')


SCENES = {'studio': studio, 'grove': grove, 'giants': giants, 'cottage': cottage_shot, 'farm': farm_shot,
          'friends': friends, 'grotto': grotto_shot, 'foes': foes, 'boss': boss, 'fields': fields, 'inventory': inventory}
# Run on request only: they produce frames to choose from (boss_fight) or a GIF (summon_gif).
EXTRAS = {'boss_fight': boss_fight, 'boss_duel': boss_duel, 'summon_gif': summon_gif}

if __name__ == '__main__':
    wanted = sys.argv[1:] or list(SCENES)
    s()
    for name in wanted:
        {**SCENES, **EXTRAS}[name]()
