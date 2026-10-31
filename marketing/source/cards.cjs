// The feature cards (1600x900). Numbers come from docs/DESIGN.md, the code and the generated data; crops are pixel
// regions of the 1920x1080 captures in marketing/images/screenshots (see capture.py).
module.exports = ({ card, framed, region, label, stats, pair, inset, itemGrid, shot }) => {
  const FUNGI = [
    ['glowcap', 'Glowcap', 'Glows in the dark; Night Vision'],
    ['bouncecap', 'Bouncecap', 'Springy caps; Jump Boost'],
    ['inkcap', 'Inkcap', 'Shaggy bell that drips ink'],
    ['morel', 'Morel', 'Roast it for a hearty meal'],
    ['chanterelle', 'Chanterelle', 'Golden, for toast and stew'],
    ['deathcap', 'Deathcap', 'Don’t: Poison and Mycosis'],
    ['frostcap', 'Frostcap', 'Fire Resistance, a chill'],
    ['emberstool', 'Emberstool', 'Smouldering stalks; Haste'],
    ['puffball', 'Puffball', 'Grows into Giant Puffballs'],
  ];
  const FOOD = [
    ['roasted_morel', 'Roasted Morel', '6 hunger'],
    ['chanterelle_toast', 'Chanterelle Toast', '8 hunger'],
    ['glowcap_soup', 'Glowcap Soup', 'Night Vision, 90 s'],
    ['bouncecap_jelly', 'Bouncecap Jelly', 'Jump Boost II, Slow Falling'],
    ['frostcap_tea', 'Frostcap Tea', 'Fire Resistance, 90 s'],
    ['ember_skewer', 'Ember Skewer', 'Strength, 30 s'],
    ['truffle', 'Truffle', 'Regeneration'],
    ['truffle_stew', 'Truffle Stew', 'Regeneration II, Absorption'],
    ['foragers_stew', 'Forager’s Stew', 'Cures Mycosis'],
    ['antifungal_tonic', 'Antifungal Tonic', 'Spore Ward, 3 min'],
  ];
  const json = (file, rows) => `<div class="frame" style="background:rgba(6,17,19,.93);padding:26px 38px;font-family:monospace;font-size:23px;line-height:1.55;color:var(--text)">
    <div style="color:var(--dim)">${file}</div>
    <pre style="margin:10px 0 0;font-family:inherit">{
${rows.map(([k, v], i) => `  <span style="color:var(--gold)">"${k}"</span>: <span style="color:${v === 'true' || v === 'false' ? 'var(--rose)' : 'var(--glow)'}">${v}</span>${i < rows.length - 1 ? ',' : ''}`).join('\n')}
}</pre></div>`;

  const cards = {
    'card-giants': () => card({
      kicker: 'Three giants', title: 'Fungi the size<br>of trees', titleSize: 66,
      points: ['The <b class="hi">Glowcap</b>, its gills hanging in curtains of light', 'The <b class="hi">Bouncecap</b>: land on its cap and bounce, unhurt',
        'The shaggy <b class="hi">Inkcap</b>, dripping ink from its bell', 'Bone meal grows each one from its small mushroom',
        'They crowd the Mushroom Fields, and Glowcaps light the caves'],
      art: pair('giants-day.jpg', 'glowcap-grove.jpg', 'By day', 'By night', 'left:20px;top:20px', 640)
        + stats([['Giants', '3'], ['Gill light', '14'], ['Bouncecap fall', 'no damage', 1.4]]) }),

    'card-woods': () => card({
      kicker: 'Build with the bloom', title: 'Three<br>fungal woods',
      points: ['Glowcap, Bouncecap and Inkcap: cool blue-grey, rosy tan, charcoal violet', 'Stems, hyphae, planks, stairs, slabs, fences, gates, doors, trapdoors, buttons, plates',
        'Every vanilla wood recipe works with them', 'Fireproof like nether stems, and still good fuel', 'Glowcap Lanterns light the porch'],
      art: framed(region('fungal-cottage.jpg', 200, 60, 1600, 900, 980)) + stats([['Wood sets', '3'], ['Blocks each', '14'], ['Fire', 'proof']]) }),

    'card-world': () => card({
      kicker: 'Into the undergrowth', title: 'Life on every<br>surface', titleSize: 66,
      points: ['Mycelial Veils hang from cave ceilings: pick their glowing bulbs', 'Shelf fungus climbs tree trunks, and you can climb the shelves',
        'Glowcap Gills, Emberstools and Glowmoths light the dark', 'Giant Puffballs soften a fall in a cloud of spores', 'Fairy rings, and truffle soil under the forests'],
      art: inset('glowcap-grotto.jpg', 'mushroom-fields.jpg', [450, 210, 1470, 520], '', 'Mushroom Fields', 440)
        + `<div style="height:56px"></div>` + stats([['Veil bulbs', 'light 10'], ['Shelves', 'climbable'], ['Fairy rings', '1 in 48 chunks', 1.5]]) }),

    'card-cultivation': () => card({
      kicker: 'Grow your own', title: 'Cultivation<br>logs',
      points: ['Inoculate a log with any of seven fungi', 'It fruits through four stages, faster on Mycelial Soil', 'Use a ripe log for two or three mushrooms; it fruits again',
        'Mycelial Soil grows mushrooms in any light', 'A Foraging Knife cuts an extra mushroom'],
      art: framed(region('cultivation.jpg', 0, 0, 1920, 1080, 980)) + stats([['Fungi', '7'], ['Stages', '4'], ['Harvest', '2 – 3']]) }),

    'card-friends': () => card({
      kicker: 'Friends in the dark', title: 'Sporelings &amp;<br>Trufflers',
      points: ['Sporelings wear one of four caps, by biome', 'Tame one with a Truffle: it sits, follows and sheds mushrooms', 'They tend the fungi around them',
        'Trufflers sniff out truffles and root up Truffle Soil', 'Glowmoths drift toward the light, wings aglow'],
      art: inset('friends.jpg', 'glowcap-grotto.jpg', [700, 280, 640, 360], '', 'Glowmoths', 400)
        + `<div style="height:56px"></div>` + stats([['Variants', '4'], ['Taming', '1 in 3'], ['Sheds', '5 – 10 min']]) }),

    'card-foes': () => card({
      kicker: 'Things that bite back', title: 'Fungal<br>foes',
      points: ['<b class="hi">Bloatshroom</b>: swells, then bursts into spores', '<b class="hi">Shambler</b>: its hits infect, and it rises from the infected dead',
        '<b class="hi">Sporemaw</b>: hides burrowed, then lobs spore globs', '<b class="hi">Mimicap</b>: a toadstool, until you come close. Then legs',
        'Every one of them shrugs off Mycosis'],
      art: framed(region('foes.jpg', 360, 300, 1200, 675, 980)) + stats([['Bloatshroom', '16 hp'], ['Shambler', '26 hp'], ['Mimicap', '22 hp']]) }),

    'card-mycosis': () => card({
      kicker: 'The infection', title: 'Mycosis',
      points: ['Shamblers, Deathcaps, spore clouds and Spore Bombs infect', 'It wears you down, but never below one heart', 'Zombies, villagers, illagers and players who die infected rise as Shamblers',
        'Forager’s Stew and the Antifungal Tonic cure it', 'Spore Ward, full Mycoleather or the Crown keep it off'],
      art: itemGrid([['mob_effect/mycosis', 'Mycosis', 'A point of damage every 4 s'], ['mob_effect/spore_ward', 'Spore Ward', 'Immune to Mycosis and spores'],
        ['mob_effect/rooted', 'Rooted', 'Slowed, and no jumping'], ['spore_bomb', 'Spore Bomb', 'Throw a cloud of Mycosis'],
        ['foragers_stew', 'Forager’s Stew', 'Cures Mycosis'], ['antifungal_tonic', 'Antifungal Tonic', 'Cures, then Spore Ward']], 2, 64)
        + stats([['Damage', '1 per 4 s'], ['Never below', '1 heart'], ['Milk', 'cures']]) }),

    'card-boss': () => card({
      kicker: 'The ruler of the mycelium', title: 'The<br>Myceliarch',
      points: ['A towering walker of braided stems under a vast glowing cap', 'Slams, lines of erupting roots and rings of spores',
        'It calls Bloatshrooms and Shamblers to its side', 'At half health its gills burn brighter: the second bloom', 'Its own boss bar, and it never breaks your base'],
      art: framed(region('myceliarch-nova.jpg', 0, 0, 1920, 1080, 980), '', '#48e5c2') + stats([['Health', '300'], ['Armor', '10'], ['Second bloom', '50%']], '#48e5c2') }),

    'card-summon': () => card({
      kicker: 'The Fruiting Heart', title: 'Call it up',
      points: ['Craft a Fruiting Heart from Lumen Spores, Truffles, Mycoleather and a Mycelial Core', 'Use it on Mycelium, Mycelial Soil, Podzol or Moss',
        'Roots and spores rise for three seconds', 'Then the Myceliarch climbs out of the earth', 'Only one at a time within 96 blocks'],
      art: pair('myceliarch-risen.jpg', 'myceliarch.jpg', 'Risen', 'At dusk') }),

    'card-fight': () => card({
      kicker: 'The fight', title: 'Root and<br>spore',
      points: ['<b class="hi">Slam</b>: 14 damage up close, and a ring of Root Spikes', '<b class="hi">Root Eruption</b>: a line of twelve spikes that root you',
        '<b class="hi">Spore Nova</b>: the cap swells, then a ring of Mycosis bursts out', '<b class="hi">Brood Call</b>: two Bloatshrooms and a Shambler',
        '<b class="hi">Spore Rain</b> in the second bloom: globs fall around you'],
      art: pair('myceliarch-windup.jpg', 'myceliarch-roots.jpg', 'Wind-up', 'Root Eruption', 'left:20px;top:20px', 640)
        + stats([['Slam', '14'], ['Root Spike', '8 + Rooted', 1.3], ['Nova radius', '7']], '#48e5c2') }),

    'card-spoils': () => card({
      kicker: 'Spoils of the bloom', title: 'Bloomreaver<br>&amp; Crown',
      points: ['<b class="hi">Spore Heart</b>: the Myceliarch’s prize', '<b class="hi">Bloomreaver</b>: 8 damage, every hit infects; use it for a Spore Burst',
        '<b class="hi">Crown of the Bloom</b>: Night Vision and Spore Ward while worn', '<b class="hi">Mycoleather</b> armor, grown not tanned',
        'A full Mycoleather set wards off spores'],
      art: `<div style="display:flex;gap:28px;align-items:center">${framed(region('inventory.jpg', 690, 285, 545, 500, 520))}
        <div style="flex:1">${itemGrid([['spore_heart', 'Spore Heart', 'From the Myceliarch'], ['bloomreaver', 'Bloomreaver', 'Hits infect; Spore Burst'],
          ['crown_of_the_bloom', 'Crown of the Bloom', 'Night Vision, Spore Ward'], ['mycoleather_tunic', 'Mycoleather', '2 / 5 / 4 / 2 armor']], 1, 56)}</div></div>` }),
    'card-fungi': () => card({
      kicker: 'Nine new mushrooms', title: 'Every one<br>does something', titleSize: 64,
      points: ['Placed, each one is a real 3D model, never a flat cross', 'Pot them, plant them, spread them with bone meal',
        'Most are edible raw, and each has its own effect', 'They live on dirt, moss and mycelium in any light, on stone in the dark',
        'Find them from snowy peaks to the deepest caves'],
      art: itemGrid(FUNGI, 2, 64) }),

    'card-kitchen': () => card({
      kicker: 'From forest floor to bowl', title: 'The Forager’s<br>Kitchen',
      points: ['Ten dishes and drinks, from roasted morels to truffle stew', 'Each one does something: sight in the dark, a softer fall, strength',
        'Forager’s Stew and the Antifungal Tonic cure Mycosis', 'Bowls and bottles come back', 'Trufflers dig up the truffles for you'],
      art: itemGrid(FOOD, 2, 56) }),

    'card-config': () => card({
      kicker: 'Make it yours', title: 'Tune the<br>bloom',
      points: ['One commented file, created on first launch', 'Turn Mycosis off, or keep the infected dead from rising',
        'Set the Myceliarch’s health and damage', 'Every feature and spawn sits in biome tags a datapack can change',
        'Missing keys are added and your values are kept'],
      art: json('config/spore_and_stem.json', [['mycosis_enabled', 'true'], ['mycosis_rising', 'true'], ['mycosis_damage_interval', '80'],
        ['myceliarch_health', '300.0'], ['myceliarch_damage_multiplier', '1.0'], ['sporeling_shed_min', '5'], ['sporeling_shed_max', '10'],
        ['truffler_dig_chance', '0.15']]) }),
  };
  return cards;
};
