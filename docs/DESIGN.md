# Spore & Stem: design

The authoritative content spec for Spore & Stem 1.0 ("First Bloom"). Every id, number and behaviour in code, data,
art and listing copy comes from here. When the game changes, change this file in the same commit.

- **Mod id** `spore_and_stem` · **package** `com.nightbeam.sporeandstem` · **author** NightBeam Studio · Apache-2.0
- **Formerly** Genetically Modified Monsters (a 1.0 rewrite: nothing from it is kept).
- **Look:** clean, readable fungus. Natural cap colours with one bioluminescent accent (teal), soft spore particles,
  real 3D shapes for every placed mushroom. No gore, no body horror: eerie, not gross.

## 1. Fungi

### 1.1 Huge fungi with wood sets

Three species grow into huge mushrooms and give a full building set. Their small mushrooms grow huge with bone meal
on any dirt-like block, mycelium, moss or Mycelial Soil, given the room.

| Species | Cap | Stem / planks | Huge shape | Special |
| --- | --- | --- | --- | --- |
| **Glowcap** `glowcap` | Bioluminescent teal, pale rim, light 10 | Pale blue-grey with teal veins | Slender stem 6-10, flat parasol cap r 3-4, **Glowcap Gills** hang under the rim | Small: light 9. Gills: light 14, drop Lumen Spores |
| **Bouncecap** `bouncecap` | Rosy pink with cream spots | Soft rosy tan | Stout stem 3-5, round puffy dome r 3-4 | Cap is bouncy like slime, no fall damage. Drops Bouncecap Gel |
| **Inkcap** `inkcap` | Shaggy grey-white bell, ink-black fringe | Deep charcoal-violet | Tall stem 7-12, tall bell cap r 2 flaring to 3 | Cap drips ink particles, drops Ink Sacs |

Blocks per species `s` (16 each):
`s` (small mushroom, 3D model, pottable), `potted_s`, `s_cap` (six-face huge mushroom block), `s_stem`,
`stripped_s_stem`, `s_hyphae`, `stripped_s_hyphae`, `s_planks`, `s_stairs`, `s_slab`, `s_fence`, `s_fence_gate`,
`s_door`, `s_trapdoor`, `s_button`, `s_pressure_plate`. Glowcap also has `glowcap_gills`.

Stems strip with an axe. Mushroom wood is fuel and is not flammable (like nether stems). Stems are in
`#minecraft:logs`, planks in `#minecraft:planks`, so every vanilla wood recipe works.

### 1.2 Small fungi

All are placeable 3D mushrooms (random rotation and offset), pottable, and edible raw unless noted. Bone meal spreads
a copy to a nearby spot. They survive in any light on dirt-like blocks, moss, mycelium and Mycelial Soil, and on any
solid block in the dark.

| Fungus | id | Look | Raw | Where |
| --- | --- | --- | --- | --- |
| Morel | `morel` | Honeycomb cone, tan-brown | 2 food | Forests, birch forests |
| Chanterelle | `chanterelle` | Golden trumpet | 2 food | Taiga, old growth taiga, birch forests |
| Deathcap | `deathcap` | Pale olive cap, white skirt | Poison II 10 s, Mycosis 20 s | Dark forest |
| Frostcap | `frostcap` | Icy blue, frosted rim | Fire Resistance 10 s, Slowness 5 s | Snowy biomes, frozen peaks |
| Emberstool | `emberstool` | Red-orange with glowing ember tips, light 7 | Haste 10 s | Deep caves near lava, crimson forest, basalt deltas |
| Puffball | `puffball` | Round white ball | 2 food | Plains, meadows, savanna |
| Glowcap | `glowcap` | see 1.1 | Night Vision 10 s | Caves, mushroom fields, dark forest |
| Bouncecap | `bouncecap` | see 1.1 | Jump Boost 10 s | Flower forest, meadow, birch, mushroom fields |
| Inkcap | `inkcap` | see 1.1 | not edible | Swamp, dark forest, old growth taiga |

`#spore_and_stem:fungi` holds all nine plus the vanilla red and brown mushroom. `#spore_and_stem:edible_fungi`
holds the edible ones.

### 1.3 Other fungal blocks

| Block | id | Behaviour |
| --- | --- | --- |
| **Shelf Fungus** | `shelf_fungus` | Turkey-tail brackets on the side of any log or stem. 1-3 shelves (grows on random ticks). Solid plates you can stand on. Drops one per shelf |
| **Mycelial Veil** | `mycelial_veil`, `mycelial_veil_plant` | Hanging white threads from cave ceilings, grows down like weeping vines. Some segments carry glowing bulbs (light 10); use to pick 1 Lumen Spores. Shears or a Foraging Knife drop Mycelial Thread |
| **Giant Puffball** | `giant_puffball` | Soft round block. Landing on it puffs a spore cloud (cosmetic), halves fall damage. Drops 2-4 Puffballs |
| **Truffle Soil** | `truffle_soil` | Dirt laced with truffles, generated under forests. Drops 1-2 Truffles (Fortune), itself with Silk Touch |
| **Mycelial Soil** | `mycelial_soil` | Dark loam threaded with white. Mushrooms (vanilla too) survive on it in any light and grow on random ticks |
| **Glowcap Lantern** | `glowcap_lantern` | Lantern of glowcap gills in a stem frame. Light 15, stands or hangs |
| **Cultivation Log** | `cultivation_log` | A felled log lying on its side. Use any fungus from the table below to inoculate it; it fruits through 4 stages on random ticks (faster on Mycelial Soil, slower in bright light). Use a ripe log to harvest 2-3 of that fungus |

Cultivation Log fungi: `glowcap`, `bouncecap`, `inkcap`, `morel`, `chanterelle`, `frostcap`, `emberstool`.

## 2. Items

### 2.1 Materials

| Item | id | Source | Use |
| --- | --- | --- | --- |
| Lumen Spores | `lumen_spores` | Glowcap caps/gills, veil bulbs, Glowmoths | Lantern, Glowcap Soup, Fruiting Heart |
| Mycelial Thread | `mycelial_thread` | Veils (shears/knife), Shamblers, Sporemaws, Mimicaps | 2 → 1 String, Mycoleather, Spore Bombs |
| Mycoleather | `mycoleather` | 3 any cap + 1 Mycelial Thread → 2 | Armor, Fruiting Heart, `#c:leathers` |
| Bouncecap Gel | `bouncecap_gel` | Bouncecap caps | `#c:slime_balls`, Bouncecap Jelly |
| Mycelial Core | `mycelial_core` | Shambler 5%, Mimicap 8%, Sporemaw 4% (+1% per Looting) | Fruiting Heart |
| Truffle | `truffle` | Truffle Soil, Trufflers | Food, taming Sporelings, breeding Trufflers |
| Fruiting Heart | `fruiting_heart` | Lumen Spores ×4, Truffle ×2, Mycoleather ×2, Mycelial Core | Summons the Myceliarch |
| Spore Heart | `spore_heart` | The Myceliarch | Bloomreaver, Crown of the Bloom |
| Spore Glob | `spore_glob` | (projectile only, not obtainable) | Sporemaw and Myceliarch shots |

### 2.2 Food

| Food | id | Recipe | Food / sat. mod | Effect |
| --- | --- | --- | --- | --- |
| Roasted Morel | `roasted_morel` | Smelt/smoke/campfire Morel | 6 / 0.6 | |
| Chanterelle Toast | `chanterelle_toast` | Bread + 2 Chanterelle | 8 / 0.8 | |
| Glowcap Soup | `glowcap_soup` | Bowl + 2 Glowcap + Lumen Spores | 6 / 0.6 | Night Vision 90 s |
| Bouncecap Jelly | `bouncecap_jelly` | Glass Bottle + Bouncecap Gel + Sugar | 4 / 0.4 | Jump Boost II 45 s, Slow Falling 15 s |
| Frostcap Tea | `frostcap_tea` | Glass Bottle + 2 Frostcap + Sugar | 2 / 0.2 | Fire Resistance 90 s |
| Ember Skewer | `ember_skewer` | Stick + Emberstool + Roasted Morel | 6 / 0.7 | Strength 30 s |
| Truffle | `truffle` | | 3 / 0.6 | Regeneration 5 s |
| Truffle Stew | `truffle_stew` | Bowl + Truffle + Morel + Chanterelle + Baked Potato | 10 / 1.2 | Regeneration II 8 s, Absorption 60 s |
| Forager's Stew | `foragers_stew` | Bowl + 3 `#edible_fungi` | 8 / 0.8 | Cures Mycosis |
| Antifungal Tonic | `antifungal_tonic` | Glass Bottle + Frostcap + Chanterelle + Honey Bottle | 0 / 0 (always edible) | Cures Mycosis, Spore Ward 3 min |

Bowls and bottles come back.

### 2.3 Tools, weapons and armor

- **Foraging Knife** `foraging_knife`: 250 durability, 3 attack. Mines fungal blocks fast; small fungi and caps mined
  with it drop one extra; it harvests Mycelial Thread from veils. Recipe: iron ingot over stick (diagonal) + thread.
- **Spore Bomb** `spore_bomb` (stack 16): thrown, bursts into a spore cloud (radius 3, 6 s): Mycosis 15 s and
  Slowness II 6 s. Recipe: Puffball + Deathcap + Mycelial Thread → 2.
- **Mycoleather armor** `mycoleather_hood`, `mycoleather_tunic`, `mycoleather_leggings`, `mycoleather_boots`:
  2/5/4/2 defense, durability multiplier 14, enchantability 18, repaired with Mycoleather. Wearing all four gives
  **Spore Ward**.
- **Bloomreaver** `bloomreaver` (boss tier sword): 8 attack, -2.4 speed, 1800 durability, hits inflict Mycosis II
  6 s. **Use:** Spore Burst, radius 4: Mycosis II, Slowness II and a knockback push on every other living thing;
  10 s cooldown, 3 durability. Recipe: Spore Heart + Diamond Sword + 2 Lumen Spores + 2 Mycoleather.
- **Crown of the Bloom** `crown_of_the_bloom` (helmet): 3 defense, 2 toughness, 600 durability. While worn: Night
  Vision and Spore Ward, and Sporelings never flee from you. Recipe: Spore Heart + Golden Helmet + 2 Glowcap Caps.
- Spawn eggs for all eight creatures.

## 3. Effects

| Effect | id | Kind | Colour | Behaviour |
| --- | --- | --- | --- | --- |
| **Mycosis** | `mycosis` | harmful | `#7FB069` | 1 damage every 80 ticks ÷ (amplifier+1), never below 1 health. Spore particles. Fungal creatures and anyone with Spore Ward shrug it off. A zombie, husk, drowned, villager, pillager, vindicator, witch or player that dies with Mycosis **rises as a Shambler** (config) |
| **Spore Ward** | `spore_ward` | beneficial | `#D9C9A3` | Immune to Mycosis and spore clouds |
| **Rooted** | `rooted` | harmful | `#6B4F2A` | Movement −60%, no jumping |

Milk cures all three.

## 4. Creatures

All models are hierarchical with keyframed animations (Catmull-Rom). Each has idle, walk/fly and every special move
animated. `#spore_and_stem:fungal` (entity type tag) marks the fungal creatures: they ignore Mycosis and spore clouds.

| Creature | id | Kind | Size (w×h) | Health | Notes |
| --- | --- | --- | --- | --- | --- |
| **Sporeling** | `sporeling` | passive, tameable | 0.5×0.6 | 8 | Four cap variants (glowcap, bouncecap, inkcap, chanterelle) by biome. Tends small fungi near it (bone meal effect, slow). Tame with Truffles (1 in 3), sits on use. Tamed ones shed a mushroom of their variant every 5-10 min. Breeds with Truffles |
| **Bloatshroom** | `bloatshroom` | hostile | 0.8×1.0 | 16 | Waddles close, swells over 30 ticks and bursts into a spore cloud (r 3.5: Mycosis 20 s, Nausea 6 s, Blindness 2 s). No block damage. Fire makes it burst. Drops 1-2 Puffballs |
| **Shambler** | `shambler` | hostile | 0.7×2.1 | 26 | Cap-headed fungal walker. Hits for 4 + Mycosis 8 s. Does not burn; wilts (−25% speed) in direct sunlight. Rises from the infected dead. Drops thread, a fungus, Mycelial Core 5% |
| **Sporemaw** | `sporemaw` | hostile, rooted | 0.9×1.3 | 20 | Hides burrowed (only its cap shows). Emerges near players and lobs arcing Spore Globs (3 damage + small cloud) every 2 s. Burrows and resurfaces up to 8 blocks away after 3 hits or losing sight |
| **Mimicap** | `mimicap` | hostile, climbs | 1.0×0.9 | 22 | Sits disguised as a big red or brown mushroom. Within 5 blocks it unfolds six legs and hunts; bite 5 + Rooted 1.5 s. Settles back into hiding after losing you |
| **Glowmoth** | `glowmoth` | ambient, flying | 0.5×0.4 | 4 | Glowing wings, drawn to light and glowcaps. Drops Lumen Spores |
| **Truffler** | `truffler` | passive, breedable | 0.9×0.9 | 14 | Mossy boar with mushrooms on its back. Sniffs the ground and now and then digs up a Truffle; roots out nearby Truffle Soil. Breeds with Truffles |
| **The Myceliarch** | `myceliarch` | boss | 2.0×4.2 | 300 | See below |

### 4.1 The Myceliarch

The ruler of the mycelium: a towering walker of braided stems under a vast glowing cap, with root legs and long
root-clawed arms. Armor 10, attack 14, knockback resistance 1, follow range 48, green boss bar.

- **Summoning:** use a **Fruiting Heart** on Mycelium, Mycelial Soil, Podzol or Moss. Roots and spores rise for 3 s,
  then it emerges from the ground (invulnerable while emerging).
- **Slam** (≤ 4 blocks): both arms crash down, 14 damage in front, knockback, a ring of Root Spikes.
- **Root Eruption** (6-20 blocks): a line of 12 Root Spikes runs at the target, each 8 damage + Rooted 2 s.
- **Spore Nova** (every 15 s): its cap swells, then a ring of spores bursts out (r 7, Mycosis II 10 s) and shoves
  everything back.
- **Brood Call** (every 25 s, at most 6 minions): calls up 2 Bloatshrooms and a Shambler.
- **Second bloom** (≤ 50% health): a roar (invulnerable 2 s), its gills burn brighter, it moves 30% faster,
  attack cooldowns ×0.6, and it adds **Spore Rain**: Spore Globs fall around the target for 5 s.
- **Death:** it collapses into a cloud of spores over 3 s. Drops the **Spore Heart**, 4-8 Mycoleather, 8-16 Lumen
  Spores and 250 experience.

Projectiles and effects: `spore_glob`, `spore_bomb` (thrown items) and `root_spike` (an evoker-fang-like root that
erupts, hits at tick 6 and sinks back).

## 5. World

No new biomes (so no dependencies and no world-type conflicts): Spore & Stem grows into the vanilla ones. Every
feature and spawn is added through biome tags under `data/spore_and_stem/tags/worldgen/biome/`, identical on Fabric
and NeoForge, so datapacks can move them.

| Feature | Biomes |
| --- | --- |
| Huge Glowcaps | Mushroom fields; lush caves and cave floors below y 40 |
| Huge Bouncecaps | Flower forest, mushroom fields, meadow (rare) |
| Huge Inkcaps | Dark forest, swamp, mushroom fields |
| Glowcap patches | Mushroom fields, dark forest, cave floors below y 50 |
| Bouncecap patches | Flower forest, meadow, birch forest, cherry grove, mushroom fields |
| Inkcap patches | Swamp, mangrove swamp, dark forest, old growth taiga |
| Morel / Chanterelle / Deathcap / Frostcap / Puffball patches | see 1.2 |
| Emberstool | Cave floors below y 0 near lava, crimson forest, basalt deltas |
| Giant Puffballs | Plains, meadow, savanna (rare) |
| Shelf Fungus | On trunks in dark forest, old growth taiga/birch, swamp, forest |
| Mycelial Veils | Cave ceilings, under huge glowcaps |
| Fairy Rings | Plains, meadow, forest, flower forest, birch (1 in 48 chunks): a ring of mushrooms r 3-5 |
| Truffle Soil | Underground dirt in forests, dark forest, taiga |

| Creature | Spawns | Weight |
| --- | --- | --- |
| Sporeling | Mushroom fields, dark forest, flower forest, meadow, swamp, taiga, lush caves | 10 (creature) |
| Truffler | Dark forest, old growth taiga, forest, mushroom fields | 6 (creature) |
| Glowmoth | Lush caves, dark forest, mushroom fields, all overworld caves | 8 (ambient) |
| Bloatshroom | Overworld (monster) | 25 |
| Shambler | Dark forest, swamp, mangrove, overworld caves (monster) | 20 |
| Sporemaw | Dark forest, swamp, lush caves, overworld caves (monster) | 10 |
| Mimicap | Forest, dark forest, birch, taiga (any light), caves | 8 |

## 6. Advancements

Root **Spore & Stem** (any fungus) → Lights Out, Caps On (glowcap) · Bounce House (stand on a bouncecap cap) ·
Mycophile (every small fungus) · Patience of a Log (inoculate a cultivation log) · Grown, Not Tanned (mycoleather) →
Mycologist (full mycoleather) · A Friend in Spores (tame a sporeling) · Truffle Shuffle (a truffle) · Pop Goes the
Puffball (kill a bloatshroom) · That Mushroom Has Teeth (bitten by a mimicap) · Clean Bill of Health (drink an
antifungal tonic) · The Fruiting Body (summon the Myceliarch) → Uprooted (defeat it) → Reap What You Sow
(Bloomreaver).

## 7. Configuration

`config/spore_and_stem.json`, created on first launch with every key commented (`_comment` fields). Missing keys
are added, your values kept.

- `mycosis_enabled` (true), `mycosis_rising` (true): the infected dead rise as Shamblers.
- `mycosis_damage_interval` (80 ticks).
- `myceliarch_health` (300), `myceliarch_damage_multiplier` (1.0).
- `sporeling_shed_minutes` (5-10, as `sporeling_shed_min` / `sporeling_shed_max`).
- `truffler_dig_chance` (0.15 per sniff).

## 8. Sounds

Every creature and fungal action has its own sound event with a subtitle. The audio is synthesised by
`tools/assets/sounds.py` (no vanilla files are shipped). Block sound types reuse vanilla sound events by name.
