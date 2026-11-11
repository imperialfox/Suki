/* Suki · catalog.js
   The searchable catalogue (Tagalog first, with English names and other spellings) and the fuzzy search.
   Official price references live in js/prices.js and are matched to these items by id.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Catalogue =====
   [id, Tagalog name, English, group, unit, other spellings separated by |]
   Never change an id: saved price notes point at them. */
const CATALOG = [
  ['adobo-p', 'Adobong baboy', 'Pork adobo', 'Ulam / lutong-bahay', 'per serving', 'baboy adobo|pork adobo|adobo baboy|adobong pork'],
  ['adobo-c', 'Adobong manok', 'Chicken adobo', 'Ulam / lutong-bahay', 'per serving', 'manok adobo|chicken adobo|adobo chicken'],
  ['sinigang-p', 'Sinigang na baboy', 'Pork sour soup', 'Ulam / lutong-bahay', 'per serving', 'sinigan baboy|sinigag|sinigang baboy|pork sinigang'],
  ['sinigang-h', 'Sinigang na hipon', 'Sour soup with shrimp', 'Ulam / lutong-bahay', 'per serving', 'sinigang hipon|hipon sinigang|shrimp sinigang'],
  ['tinola', 'Tinolang manok', 'Chicken tinola', 'Ulam / lutong-bahay', 'per serving', 'tinola|chicken tinola'],
  ['menudo', 'Menudo', 'Filipino pork stew', 'Ulam / lutong-bahay', 'per serving', 'menudo baboy|pork menudo'],
  ['afritada', 'Afritada', 'Filipino tomato stew', 'Ulam / lutong-bahay', 'per serving', 'afritadang manok|chicken afritada'],
  ['karekare', 'Kare-kare', 'Peanut stew', 'Ulam / lutong-bahay', 'per serving', 'karekare|kare kare'],
  ['paksiw', 'Paksiw na isda', 'Fish cooked in vinegar', 'Ulam / lutong-bahay', 'per serving', 'paksiw|paksiw isda|fish paksiw'],
  ['giniling', 'Ginisang giniling', 'Filipino ground meat', 'Ulam / lutong-bahay', 'per serving', 'giniling|giniling baboy|ground pork'],
  ['laing', 'Laing', 'Taro leaves in coconut milk', 'Ulam / lutong-bahay', 'per serving', 'laing gulay'],
  ['pinakbet', 'Pinakbet', 'Filipino vegetable stew', 'Ulam / lutong-bahay', 'per serving', 'pakbet|pinak bet'],
  ['talong', 'Tortang talong', 'Aubergine omelette', 'Ulam / lutong-bahay', 'per serving', 'torta talong|eggplant omelette|aubergine omelette'],
  ['sisig', 'Sisig', 'Sizzling chopped pork', 'Ulam / pulutan', 'per serving', 'sisig baboy|pork sisig'],
  ['liempo', 'Inihaw na liempo', 'Grilled pork belly', 'Inihaw', 'per serving', 'inihaw liempo|liempo|grilled pork belly|baboy inihaw'],
  ['kwek', 'Kwek-kwek', 'Quail eggs in orange batter', 'Street food / meryenda', 'per serving', 'kwek kwek|queck queck|kwekwek|orange eggs'],
  ['fishball', 'Fish ball', 'Fish balls', 'Street food', 'per serving', 'fishball|fish balls|bola bola isda'],
  ['isaw', 'Isaw', 'Grilled intestines', 'Street food', 'per stick', 'isaw manok|isaw baboy|grilled intestines'],
  ['taho', 'Taho', 'Silken tofu, arnibal and sago', 'Meryenda', 'per cup', 'taho sago|taho arnibal|soy pudding'],
  ['turon', 'Turon', 'Banana spring roll', 'Meryenda', 'per piece', 'banana turon|turon saging'],
  ['bananacue', 'Banana cue', 'Caramelised banana on a stick', 'Meryenda', 'per stick', 'bananacue|saging cue'],
  ['siomai', 'Siomai', 'Filipino-style dumplings', 'Meryenda', 'per serving', 'shumai|siu mai|siomay'],
  ['lugaw', 'Lugaw', 'Rice porridge', 'Meryenda', 'per bowl', 'arroz caldo|goto|rice porridge'],
  ['halo', 'Halo-halo', 'Shaved ice dessert', 'Dessert', 'per serving', 'halohalo|halo halo'],
  ['leche', 'Leche flan', 'Filipino caramel custard', 'Dessert', 'per serving', 'lecheplan'],
  ['pandesal', 'Pandesal', 'Filipino bread roll', 'Tinapay', 'per piece', 'pan de sal|bread roll|tinapay'],
  ['ensaymada', 'Ensaymada', 'Sweet cheese bread', 'Tinapay', 'per piece', 'ensaimada'],
  ['puto', 'Puto', 'Steamed rice cake', 'Kakanin', 'per piece', 'puto cheese|puto rice cake'],
  ['bibingka', 'Bibingka', 'Filipino rice cake', 'Kakanin', 'per piece', 'bibingka rice cake'],
  ['bigas', 'Bigas', 'Uncooked rice', 'Palengke / groceries', 'per kilogram', 'rice|bigas 1 kilo|isang kilong bigas|1 kilo bigas|rice per kilo|kanin na hilaw'],
  ['itlog', 'Itlog', 'Eggs', 'Palengke / groceries', 'per piece', 'egg|eggs|isang dosenang itlog|dozen eggs'],
  ['baboy', 'Baboy', 'Pork', 'Palengke / groceries', 'per kilogram', 'pork|karne ng baboy|baboy kilo'],
  ['manok', 'Manok', 'Chicken', 'Palengke / groceries', 'per kilogram', 'chicken|karne ng manok|manok kilo'],
  ['isda', 'Isda', 'Fish', 'Palengke / groceries', 'per kilogram', 'fish|fresh fish'],
  ['sibuyas', 'Sibuyas', 'Onion', 'Palengke / groceries', 'per kilogram', 'onion|onions'],
  ['bawang', 'Bawang', 'Garlic', 'Palengke / groceries', 'per kilogram', 'garlic'],
  ['kamatis', 'Kamatis', 'Tomato', 'Palengke / groceries', 'per kilogram', 'tomato|tomatoes'],
  ['patatas', 'Patatas', 'Potato', 'Palengke / groceries', 'per kilogram', 'potato|potatoes'],
  ['mantika', 'Mantika', 'Cooking oil', 'Palengke / groceries', 'per litre', 'oil|cooking oil'],
  ['toyo', 'Toyo', 'Soy sauce', 'Palengke / groceries', 'per bottle', 'soy sauce'],
  ['suka', 'Suka', 'Vinegar', 'Palengke / groceries', 'per bottle', 'vinegar'],
  ['tubig', 'Tubig na bottled', 'Bottled drinking water', 'Inumin', 'per bottle (size varies)', 'tubig bote|bottled water|mineral water|water bottle|drinking water'],
  ['softdrinks', 'Soft drinks', 'Fizzy drink', 'Inumin', 'per bottle/can', 'softdrink|soda|coke|coca cola|royal|sprite'],
  ['kape', 'Kape', 'Coffee', 'Inumin', 'per cup/pack', 'coffee|kapeng barako|instant coffee'],
  ['gatas', 'Gatas', 'Milk', 'Inumin / groceries', 'per litre/carton', 'milk|fresh milk|evaporated milk'],
  ['milo', 'Milo', 'Malted chocolate drink', 'Inumin', 'per serving/pack', 'milo drink'],
  ['sabon', 'Sabon', 'Soap', 'Everyday essentials', 'per bar/pack', 'soap|bath soap'],
  ['shampoo', 'Shampoo', 'Shampoo', 'Everyday essentials', 'per sachet/bottle', 'shampoo sachet'],
  ['toothpaste', 'Toothpaste', 'Toothpaste', 'Everyday essentials', 'per tube', 'tooth paste|pampinis ng ngipin'],
  ['detergent', 'Detergent', 'Laundry detergent', 'Everyday essentials', 'per sachet/pack', 'washing powder|laundry soap|detergent powder'],
  // added in Q02: transport, services, fast food, drinks, pantry
  ['jeepney', 'Dyip', 'Jeepney', 'Transport', 'first 4 km', 'jeep|jeepney|jeepney fare|pamasahe|dyipni|modern jeepney|e-jeep'],
  ['tricycle', 'Traysikel', 'Tricycle', 'Transport', 'per ride', 'trike|tricycle fare|tryk|pedicab|padyak'],
  ['bus-city', 'Bus sa lungsod', 'City bus', 'Transport', 'first 5 km', 'bus|city bus|carousel|aircon bus'],
  ['bus-sanjose', 'Bus papuntang San Jose', 'Bus to San Jose City, Nueva Ecija', 'Transport', 'one way', 'baliwag|baliwag transit|five star|cubao bus|nueva ecija bus|cabanatuan bus|provincial bus'],
  ['bus-naia', 'Airport bus', 'Airport bus, NAIA to Cubao', 'Transport', 'one way', 'ube express|p2p|p2p bus|naia bus|airport bus'],
  ['grab', 'Grab', 'Ride-hailing car', 'Transport', 'base fare', 'grab car|grabcar|ride hailing|uber|tnvs|joyride car'],
  ['taxi', 'Taxi', 'Metered taxi', 'Transport', 'flag-down', 'taxi fare|cab|metered taxi'],
  ['taxi-naia', 'Airport taxi', 'Yellow airport taxi, NAIA', 'Transport', 'flag-down', 'naia taxi|airport taxi|yellow taxi'],
  ['mrt3', 'MRT-3', 'Metro Rail Transit, EDSA', 'Transport', 'per ride', 'mrt|mrt3|metro rail|train|train edsa|tren'],
  ['lrt1', 'LRT-1', 'Light Rail Transit Line 1', 'Transport', 'per ride', 'lrt|lrt1|lrt 1|light rail|train|tren'],
  ['lrt2', 'LRT-2', 'Light Rail Transit Line 2', 'Transport', 'per ride', 'lrt2|lrt 2|light rail|train|tren'],
  ['uv', 'UV Express', 'Shared van', 'Transport', 'per km', 'uv express|fx|van|shuttle van'],
  ['sim', 'SIM card', 'Prepaid SIM', 'Services', 'per SIM', 'sim|esim|globe sim|smart sim|load'],
  // added in Q35: the airport package, split from the SIM card so one item has one unit
  ['sim-tourist', 'Tourist SIM', 'Tourist SIM package', 'Services', 'per package', 'tourist sim|smart tourist sim|airport sim|naia sim|travel sim'],
  ['data', 'Data promo', 'Mobile data', 'Services', 'per promo', 'data|load|mobile data|internet|globe|smart|go99|goplus|magic data|power all'],
  ['laundry', 'Laba', 'Laundry', 'Services', 'per kg', 'laundry|labahan|laundromat|wash dry fold|laundry shop'],
  ['haircut', 'Gupit', 'Haircut', 'Services', 'per cut', 'haircut|barber|barbershop|gupit lalaki|salon'],
  ['massage', 'Masahe', 'Massage', 'Services', '1 hour', 'massage|hilot|spa|masahe|swedish massage'],
  ['chickenjoy', 'Chickenjoy', 'Jollibee fried chicken', 'Fast food', 'per meal', 'jollibee|chicken joy|chickenjoy|fried chicken'],
  ['yumburger', 'Yumburger', 'Jollibee burger', 'Fast food', 'per burger', 'jollibee burger|yum burger|burger'],
  ['chickenmcdo', 'Chicken McDo', 'McDonald’s fried chicken', 'Fast food', 'per meal', 'mcdo|mcdonalds|mcdonald s|chicken mcdo'],
  ['pm1', 'Mang Inasal PM1', 'Grilled chicken with rice', 'Fast food', 'per meal', 'mang inasal|inasal|chicken inasal|pm1|unli rice'],
  ['latte', 'Kape sa café', 'Café latte', 'Fast food', 'per cup', 'starbucks|latte|cafe latte|coffee shop'],
  ['carinderia', 'Karinderya', 'Carinderia meal', 'Ulam / lutong-bahay', 'per plate', 'carinderia|karinderya|turo turo|turo-turo|ulam with rice|rice meal|silog'],
  ['kikiam', 'Kikiam', 'Fried fish roll', 'Street food', 'per stick', 'kikyam|que kiam'],
  ['beer', 'Serbesa', 'Beer', 'Inumin', 'per bottle/can', 'beer|san miguel|pale pilsen|red horse|san mig light|cerveza|alak'],
  ['gatorade', 'Gatorade', 'Sports drink', 'Inumin', 'per bottle', 'sports drink|pocari'],
  ['noodles', 'Instant noodles', 'Instant noodles', 'Palengke / groceries', 'per pack', 'noodles|mami|pancit canton|lucky me|payless|instant mami|ramen|cup noodles'],
  ['sardinas', 'Sardinas', 'Canned sardines', 'Palengke / groceries', 'per can', 'sardines|ligo|555|mega sardines|de lata'],
  ['cornedbeef', 'Corned beef', 'Corned beef', 'Palengke / groceries', 'per can', 'corned beef|argentina|delata|de lata'],
  ['tasty', 'Tinapay na tasty', 'Sliced loaf', 'Tinapay', 'per loaf', 'loaf|sliced bread|pinoy tasty|gardenia|white bread'],
  ['asin', 'Asin', 'Salt', 'Palengke / groceries', 'per pack', 'salt|iodized salt'],
  ['asukal', 'Asukal', 'Sugar', 'Palengke / groceries', 'per pack', 'sugar|white sugar'],
].map((a) => ({ id: a[0], name: a[1], english: a[2], group: a[3], unit: a[4], aliases: a[5].split('|') }));

const itemById = (id) => CATALOG.find((i) => i.id === id);

/* ===== Official price references (js/prices.js) ===== */
const REFS = () => window.sukiPriceReferences || { records: [] };
const refsFor = (id) => (REFS().records || []).filter((r) => r.itemId === id);
// the lowest official price for an item, for the result rows
function refFrom(id) {
  const r = refsFor(id);
  if (!r.length) return null;
  const low = r.reduce((a, b) => (b.price < a.price ? b : a));
  return { price: low.price, unit: low.unit, many: r.length > 1 };
}
const OFFICIAL_IDS = () => [...new Set((REFS().records || []).map((r) => r.itemId))].filter(itemById);

/* ===== Typical prices (js/typical.js, Q02) and browsing by kind ===== */
const TYPICAL = () => (window.sukiTypical && window.sukiTypical.items) || {};
const typicalFor = (id) => TYPICAL()[id] || [];
// the price shown in a list row: the official weekly average where there is one, otherwise the typical range
function priceOf(id) {
  const o = refFrom(id);
  if (o) return { low: o.price, high: o.price, unit: o.unit, many: o.many, official: true };
  const t = typicalFor(id);
  if (!t.length) return null;
  return {
    low: Math.min(...t.map((x) => x.low)),
    high: Math.max(...t.map((x) => x.high)),
    unit: '',
    many: t.length > 1,
  };
}
// the chips on Search: every catalogue item belongs to one
const BROWSE = [['all', 'All'], ['transport', 'Transport'], ['food', 'Food'], ['market', 'Market'], ['drinks', 'Drinks'], ['services', 'Services'], ['essentials', 'Essentials']];
function browseOf(it) {
  const g = it.group || '';
  if (g === 'Transport') return 'transport';
  if (g === 'Services') return 'services';
  if (/inumin/i.test(g)) return 'drinks';
  if (/palengke|groceries/i.test(g)) return 'market';
  if (/essential/i.test(g)) return 'essentials';
  return 'food';
}
// which catalogue item a logged purchase is ("Jeepney to Cubao" is the jeepney), or null when nothing is a clear match
const matchCache = {};
function itemFor(text) {
  const k = norm(text);
  if (k in matchCache) return matchCache[k];
  const h = searchItems(k, 1)[0];
  return (matchCache[k] = h && score(h, k) >= 70 ? h.id : null);
}

// the stricter match behind a purchase's "… prices" row (Q08): the item's name or English name must appear in what
// you typed as whole words, plurals allowed ("Jeepney to Cubao", "Fish balls"), so a loose match like
// Spaghetti → Massage or Mango → Mang Inasal never offers the wrong prices. "You paid" uses wordMatch (Q14), below.
const plainWord = (w) => (w.length > 4 && w.endsWith('es') ? w.slice(0, -2) : w.length > 3 && w.endsWith('s') ? w.slice(0, -1) : w);
function wholeWords(text, name) {
  const t = norm(text).split(' ').filter(Boolean).map(plainWord),
    n = norm(name).split(' ').filter(Boolean).map(plainWord);
  if (!n.length || n.length > t.length) return false;
  for (let i = 0; i + n.length <= t.length; i++) if (n.every((w, j) => t[i + j] === w)) return true;
  return false;
}
// the item whose name or English name appears whole in the text; the longest name wins ("Laundry detergent" over "Laundry")
const strictCache = {};
function strictItemFor(text) {
  const k = norm(text);
  if (k in strictCache) return strictCache[k];
  let best = null,
    bestLen = 0;
  CATALOG.forEach((it) =>
    [it.name, it.english].forEach((n) => {
      const len = norm(n).length;
      if (len > bestLen && wholeWords(k, n)) {
        best = it.id;
        bestLen = len;
      }
    })
  );
  return (strictCache[k] = best);
}

// the purchase category for a catalogue item, the same mapping as an item's "Log what you paid"
const catOf = (it) => ({ transport: 'Transport', market: 'Groceries', essentials: 'Shopping', services: 'Other' })[browseOf(it)] || 'Food & drink';

/* ===== Matching a logged purchase to an item (Q14) =====
   Whole words only: an item's name, its English name (up to three words) or one of its other spellings has to appear
   in full. Plurals count ("fish balls"), and a one-letter slip counts in words of six letters or more ("tricyle").
   A word that merely starts like a name (mango, spaghetti) or sits inside a longer word (tourist) never counts, so
   Mango → Mang Inasal and Spaghetti → Massage are gone. The longest name wins. `whole` says the name covers everything
   typed ("jeep", not "jeep to Cubao"). Smart add, "Your usual" and "You paid" use this; Search keeps searchItems. */
const W_ITEMS = () =>
  W_ITEMS.v ||
  (W_ITEMS.v = CATALOG.map((it) => {
    const names = [it.name, ...it.aliases];
    if (it.english.split(' ').length <= 3) names.push(it.english);
    return { it, variants: [...new Set(names.map(norm).filter(Boolean))].map((v) => v.split(' ')) };
  }));
const sameWord = (t, v) => t === v || t === v + 's' || t === v + 'es' || (v.length >= 6 && t.length >= 6 && editDist(t, v) <= 1);
const wordCache = {};
function wordMatch(text) {
  const k = norm(text);
  if (k in wordCache) return wordCache[k];
  const t = k.split(' ').filter(Boolean);
  let best = null;
  W_ITEMS().forEach(({ it, variants }) =>
    variants.forEach((v) => {
      for (let i = 0; i + v.length <= t.length; i++)
        if (v.every((w, j) => sameWord(t[i + j], w))) {
          const s = v.length * 100 + v.join('').length;
          if (!best || s > best.s) best = { id: it.id, s, whole: v.length === t.length };
        }
    })
  );
  return (wordCache[k] = best && { id: best.id, whole: best.whole });
}
const wordItemFor = (text) => {
  const m = wordMatch(text);
  return m ? m.id : null;
};

/* ===== Fuzzy search =====
   Exact names and spellings score highest, then names containing what you typed, then word-by-word likeness,
   so misspellings ("sinigan"), mixed languages and phrases like "1 kilo bigas" still find the right item. */
function norm(s) {
  return String(s || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
function editDist(a, b) {
  let p = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const c = [i];
    for (let j = 1; j <= b.length; j++) c[j] = Math.min(c[j - 1] + 1, p[j] + 1, p[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    p = c;
  }
  return p[b.length];
}
function likeness(a, b) {
  if (!a || !b) return 0;
  if (a === b) return 1;
  if (a.startsWith(b) || b.startsWith(a)) return (Math.min(a.length, b.length) / Math.max(a.length, b.length)) * 0.4 + 0.6;
  // short words need to be nearly exact, so "water" doesn't match "batter" or "rice" match "ice"
  const d = editDist(a, b),
    n = Math.max(a.length, b.length);
  if (n <= 5 && d > 1) return 0;
  return 1 - d / n;
}
const FILLER = ['kilo', 'kg', 'gram', 'grams', 'g', 'isang', 'na', 'per', 'the', 'a', 'ng', 'for'];
function score(item, q) {
  q = norm(q);
  const names = [item.name, item.english, ...item.aliases].map(norm);
  if (names.includes(q)) return 100;
  if (names.some((n) => n.includes(q))) return 90;
  const toks = q.split(' ').filter((t) => t && !/^\d+(\.\d+)?$/.test(t) && !FILLER.includes(t));
  if (!toks.length) return 0;
  const words = names.join(' ').split(' ');
  let sum = 0;
  for (const t of toks) {
    const best = Math.max(0, ...words.map((w) => likeness(t, w)));
    if (best >= 0.7) sum += best;
  }
  return (
    (sum / toks.length) * 72 + Math.max(0, ...names.map((n) => likeness(q, n))) * 24 + (sum / toks.length === 1 ? 4 : 0)
  );
}
function searchItems(q, max = 12) {
  if (!norm(q)) return [];
  const hits = CATALOG.map((i) => ({ i, s: score(i, q) }))
    .filter((x) => x.s >= 40)
    .sort((a, b) => b.s - a.s);
  // keep only results close to the best one, so a clear match isn't followed by unrelated items
  const top = hits.length ? hits[0].s : 0;
  return hits
    .filter((x) => x.s >= top * 0.72)
    .slice(0, max)
    .map((x) => x.i);
}
