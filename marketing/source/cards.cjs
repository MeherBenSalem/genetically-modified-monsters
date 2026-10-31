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
