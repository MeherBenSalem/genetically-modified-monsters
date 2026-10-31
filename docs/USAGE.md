# Spore & Stem: usage guide

Everything in Spore & Stem 2.0, with every recipe and number (the same on Minecraft 1.21.1 and 1.20.1). The design reasoning is in [DESIGN.md](DESIGN.md).

## Getting started

1. Find mushrooms: Glowcaps in dark forests, the Mushroom Fields and caves; Bouncecaps in flower forests and meadows;
   Inkcaps in swamps and dark forests; Morels and Chanterelles in forests and taiga. Shelf fungus grows on old trunks,
   Mycelial Veils hang from cave ceilings.
2. Make **Mycelial Soil** (Dirt, Bone Meal and any 2 mushrooms → 2) so your mushrooms grow in daylight.
3. Bone meal a Glowcap, Bouncecap or Inkcap on soil to grow a giant, and chop it for wood and caps.
4. Turn caps into **Mycoleather** (3 caps + 1 Mycelial Thread → 2) for armor, and build **Cultivation Logs** to farm.

## Fungi

### The three giants

| | Glowcap | Bouncecap | Inkcap |
| --- | --- | --- | --- |
| Small mushroom | light 9; Night Vision 10 s when eaten | Jump Boost 10 s | not edible |
| Huge shape | slender stem, flat glowing parasol, hanging gills | stout stem, puffy dome | tall stem, shaggy bell |
| Cap block | light 10, lets glowing spores drift down | bouncy, no fall damage | drips ink |
| Cap drops | the cap; 20% Lumen Spores (50% with a Foraging Knife); 5% a Glowcap | the cap; 20% Bouncecap Gel (50%); 5% a Bouncecap | the cap; 20% Ink Sac (50%); 5% an Inkcap |
| Grows in | Mushroom Fields, cave floors deep down | flower forest, meadow, Mushroom Fields | dark forest, swamp, Mushroom Fields |

- **Bone meal** grows a small one into a giant (40% per use) on dirt-like blocks, moss, mycelium or Mycelial Soil, if
  the whole shape fits. Otherwise nothing happens.
- **Glowcap Gills** hang under the giant Glowcaps (light 14) and drop 1-2 Lumen Spores.

### Wood

Per species: stem, stripped stem, hyphae, stripped hyphae, planks, stairs, slab, fence, fence gate, door, trapdoor,
button, pressure plate. Recipes are the vanilla ones (1 stem → 4 planks, 4 stems → 3 hyphae, and so on). Stems are in
`#minecraft:logs` and planks in `#minecraft:planks`, so every recipe that takes any log or planks accepts them. Fungal
wood never catches fire but burns as furnace fuel. An axe strips stems and hyphae.

### Small mushrooms

| Mushroom | Eaten raw | Notes |
| --- | --- | --- |
| Morel | 2 hunger | Smelt, smoke or cook on a campfire for a Roasted Morel |
| Chanterelle | 2 hunger | Toast, stew, tonic |
| Deathcap | Poison II 10 s, Mycosis 20 s | Spore Bombs |
| Frostcap | Fire Resistance 10 s, Slowness 5 s | Tea, tonic |
| Emberstool | Haste 10 s | light 7; deep caves, crimson forest, basalt deltas |
| Puffball | 2 hunger | 9 → Giant Puffball |
| Inkcap | not edible | 1 → Black Dye |

All nine, plus the three giants' small mushrooms, are pottable. They survive on dirt-like blocks, moss, mycelium and
Mycelial Soil in any light, and on any solid block in the dark. Bone meal spreads a copy to a free spot within three
blocks; on their own they only spread in the dark or on mycelium.

### Other fungal blocks

- **Shelf Fungus:** placed on the side of any log or stem; 1-3 shelves, grows on random ticks, and placing another on
  it adds a shelf. The shelves are solid. Drops one per shelf.
- **Mycelial Veil:** grows down from ceilings like weeping vines. Some segments carry a glowing bulb (light 10): use
  it to pick Lumen Spores; bone meal grows a bulb. Shears drop the veil itself; a Foraging Knife drops 1-2 Mycelial
  Thread. Climbable.
- **Giant Puffball** (9 Puffballs): a soft block; landing on it puffs spores and halves fall damage. Drops 2-4
  Puffballs.
- **Truffle Soil:** under forests. Drops 1-2 Truffles (more with Fortune), itself with Silk Touch.
- **Mycelial Soil** (Dirt, Bone Meal and any 2 mushrooms → 2): mushrooms (vanilla too) live on it in any light, and
  on random ticks it spreads the mushroom on top or grows a giant.
- **Glowcap Lantern** (Mycelial Thread over 3 glowcap stems around Lumen Spores): light 15, standing or hanging.

## Cultivation

**Cultivation Log** (3 logs over Mycelial Thread, Mycelial Soil, Mycelial Thread → 2):

1. Place it (it lies along the direction you face).
2. Use a Glowcap, Bouncecap, Inkcap, Morel, Chanterelle, Frostcap or Emberstool on it to inoculate it.
3. It fruits through stages 0-3 on random ticks: 1 in 4 per tick, 1 in 2 on Mycelial Soil, 1 in 8 under an open sky
   by day.
4. Use the ripe log for 2-3 of that mushroom; it returns to stage 1. Ripe Glowcap and Emberstool logs glow.

**Foraging Knife** (iron ingot, Mycelial Thread and a stick, diagonal): 250 durability, 3 attack damage. Mines
fungal blocks fast and improves cap drops (see above).

## Food

| Food | Recipe | Food / saturation | Effect |
| --- | --- | --- | --- |
| Roasted Morel | cook a Morel | 6 / 0.6 | |
| Chanterelle Toast | Bread, 2 Chanterelles | 8 / 0.8 | |
| Glowcap Soup | Bowl, 2 Glowcaps, Lumen Spores | 6 / 0.6 | Night Vision 90 s |
| Bouncecap Jelly | Glass Bottle, Bouncecap Gel, Sugar | 4 / 0.4 | Jump Boost II 45 s, Slow Falling 15 s |
| Frostcap Tea | Glass Bottle, 2 Frostcaps, Sugar | 2 / 0.2 | Fire Resistance 90 s |
| Ember Skewer | Stick, Emberstool, Roasted Morel | 6 / 0.7 | Strength 30 s |
| Truffle | Truffle Soil, Trufflers | 3 / 0.6 | Regeneration 5 s |
| Truffle Stew | Bowl, Truffle, Morel, Chanterelle, Baked Potato | 10 / 1.2 | Regeneration II 8 s, Absorption 60 s |
| Forager's Stew | Bowl, any 3 `#spore_and_stem:edible_fungi` | 8 / 0.8 | Cures Mycosis |
| Antifungal Tonic | Glass Bottle, Frostcap, Chanterelle, Honey Bottle | 0 / 0 | Cures Mycosis, Spore Ward 3 min |

Bowls, bottles and the skewer's stick come back.

## Materials

| Item | Source | Use |
| --- | --- | --- |
| Lumen Spores | Glowcap caps and gills, veil bulbs, Glowmoths | Lantern, Glowcap Soup, Fruiting Heart, Bloomreaver |
| Mycelial Thread | Veils (Foraging Knife), Shamblers, Sporemaws, Mimicaps | 2 → String; Mycoleather, Spore Bombs, knife, logs |
| Mycoleather | 3 caps (any `#spore_and_stem:caps`) + 1 thread → 2 | Armor, Fruiting Heart, `#c:leathers` |
| Bouncecap Gel | Bouncecap caps | Bouncecap Jelly, `#c:slime_balls` |
| Mycelial Core | Shambler 5%, Mimicap 8%, Sporemaw 4% (+1% per Looting level) | Fruiting Heart |
| Truffle | Truffle Soil, Trufflers | Food, taming Sporelings, breeding |
| Spore Heart | the Myceliarch | Bloomreaver, Crown of the Bloom |

## Mycosis

- **Sources:** Shambler hits (8 s), Deathcaps, Spore Globs, Spore Bombs, Bloatshroom bursts, the Myceliarch.
- **Effect:** 1 damage every 80 ticks at level I (halved per level, never faster than every 10 ticks), never below 1
  health. Spore particles.
- **Rising:** a zombie, husk, drowned, villager, pillager, vindicator, witch or player that dies with Mycosis rises as
  a Shambler (`#spore_and_stem:mycosis_risers`).
- **Immune:** fungal creatures (`#spore_and_stem:fungal`) and anyone with **Spore Ward** (Antifungal Tonic, a full
  Mycoleather set, the Crown of the Bloom).
- **Cures:** milk, Forager's Stew, Antifungal Tonic.
- **Rooted** (Mimicap bites, Root Spikes): 60% slower, no jumping.
- **Spore Bomb** (Puffball, Deathcap, Mycelial Thread → 2; stacks to 16): thrown, bursts into a cloud (radius 3, 6 s)
  of Mycosis 15 s and Slowness II.

## Creatures

| Creature | Health | Spawns (weight) | Drops |
| --- | --- | --- | --- |
| Sporeling | 8 | Mushroom Fields, dark forest, flower forest, meadow, swamp, taiga, lush caves (10) | a mushroom of its cap |
| Truffler | 14 | Dark forest, old growth taiga, forest, Mushroom Fields (6) | porkchop, sometimes a Morel |
| Glowmoth | 4 | Caves, lush caves, dark forest, Mushroom Fields (8, ambient) | Lumen Spores |
| Bloatshroom | 16 | Overworld at night and in caves (25) | Puffballs |
| Shambler | 26 | Dark forest, swamps (20), all overworld caves (5) | Mycelial Thread, a mushroom, Mycelial Core 5% |
| Sporemaw | 20 | Dark forest, swamps, lush caves (10), all overworld caves (3) | Mycelial Thread, Deathcap, Mycelial Core 4% |
| Mimicap | 22 | Forests, dark forest, birch, taiga in any light (8), all overworld land (2) | Mycelial Thread, Mycelial Core 8% |

No monsters spawn in the Mushroom Fields or the Deep Dark.

- **Sporeling:** four caps by biome (Glowcap, Bouncecap, Inkcap, Chanterelle). Tends small fungi near it (spreads
  them; it never grows giants). Tame with Truffles (1 in 3); tamed, it follows, sits when used, and sheds a mushroom
  every 5-10 minutes (config). Breeds with Truffles. Doesn't flee from a player wearing the Crown of the Bloom.
- **Truffler:** sniffs and sometimes digs up a Truffle (`truffler_dig_chance`, 15% per sniff); walks to nearby Truffle
  Soil and roots it out (the soil turns to Coarse Dirt and drops 2 Truffles). Breeds with Truffles.
- **Glowmoth:** flies toward light and Glowcaps.
- **Bloatshroom:** swells over 1.5 s when close, then bursts into a cloud (radius 3.5) of Mycosis 20 s, Nausea 6 s and
  Blindness 2 s. Breaks no blocks. Fire or flint and steel sets it off.
- **Shambler:** hits for 4 and infects. Doesn't burn in daylight but moves 25% slower in direct sunlight.
- **Sporemaw:** waits burrowed (taking half damage) until a player is within 10 blocks, then lobs Spore Globs (3
  damage and a small Mycosis cloud) every 2 s. After 3 hits, or losing sight, it burrows and resurfaces up to 8 blocks
  away.
- **Mimicap:** disguised as a red or brown toadstool; within 5 blocks it unfolds, climbs walls and bites for 5 and
  Rooted 1.5 s. Settles back after 10 s without prey.

## The Myceliarch

**Fruiting Heart:** 4 Lumen Spores, 2 Truffles, 2 Mycoleather and a Mycelial Core:

```
L T L
M C M
L T L
```

Use it on Mycelium, Mycelial Soil, Podzol or Moss (`#spore_and_stem:myceliarch_summon_blocks`). It needs a 3×5×3
space and no other Myceliarch within 96 blocks. A 3 s ritual, then the boss climbs out (invulnerable while rising).

| | |
| --- | --- |
| Health | 300 (config `myceliarch_health`) |
| Armor | 10, knockback resistance 1, follow range 48 |
| Slam (within ~4.4 blocks) | 14 damage in a 2.8 radius in front, knockback, then 8 Root Spikes (6 damage, Rooted 1.5 s) |
| Root Eruption (5.5-20 blocks, line of sight) | 12 Root Spikes in a line, 8 damage and Rooted 2 s each |
| Spore Nova (every 15 s, within 9 blocks) | Mycosis II 10 s within 7 blocks, and a shove |
| Brood Call (every 25 s, at most 6 minions) | 2 Bloatshrooms and a Shambler |
| Second bloom (at 50%) | 2 s roar (invulnerable), brighter gills, +30% speed, cooldowns ×0.6, Spore Rain (5 s of globs, 3 damage) |
| Drops | Spore Heart, 4-8 Mycoleather, 8-16 Lumen Spores (Looting adds), 250 XP |

Damage is multiplied by `myceliarch_damage_multiplier`. It never despawns, can't be pushed, breaks no blocks, stays
within 40 blocks of where it rose, and ignores Mycosis, Rooted, poison, wither and damage from fungal creatures.

## Gear

| Item | Recipe | Stats |
| --- | --- | --- |
| Mycoleather Hood / Tunic / Leggings / Boots | Mycoleather in the armor shapes | 2 / 5 / 4 / 2 armor, durability ×14, enchantability 18. Full set: Spore Ward |
| Bloomreaver | Spore Heart, Diamond Sword, 2 Lumen Spores, 2 Mycoleather | 8 attack, -2.4 speed, 1800 durability; hits give Mycosis II 6 s. Use: Spore Burst, radius 4, Mycosis II, Slowness II and a shove; 10 s cooldown, 3 durability |
| Crown of the Bloom | Spore Heart, Golden Helmet, 2 Glowcap Caps | 3 armor, 2 toughness, 600 durability; Night Vision and Spore Ward while worn |

## Configuration

`config/spore_and_stem.json` (server side; each key has a `_comment_` beside it):

| Key | Default | |
| --- | --- | --- |
| `mycosis_enabled` | true | false makes everyone shrug Mycosis off |
| `mycosis_rising` | true | the infected dead rise as Shamblers |
| `mycosis_damage_interval` | 80 | ticks between Mycosis damage at level I (min 10) |
| `myceliarch_health` | 300.0 | |
| `myceliarch_damage_multiplier` | 1.0 | |
| `sporeling_shed_min` / `sporeling_shed_max` | 5 / 10 | minutes between a tamed Sporeling's mushrooms |
| `truffler_dig_chance` | 0.15 | chance per sniff |

## Datapacks

- Features and spawns: biome tags under `data/spore_and_stem/tags/worldgen/biome/` (`has_feature/*`, `spawns/*`),
  read by NeoForge biome modifiers and by the Fabric biome API alike.
- `#spore_and_stem:fungi`, `edible_fungi`, `caps`, `fungus_soil`, `shelf_fungus_hosts`, `myceliarch_summon_blocks`,
  `mineable/knife`, `foraging_tools`, entity tags `fungal` and `mycosis_risers`.
- Convention tags: `c:mushrooms`, `c:leathers`, `c:slime_balls`, `c:strings`, `c:foods/*`, `c:drinks`.
- Compostables: Fabric registers them in code, NeoForge reads the `neoforge:compostables` data map.
