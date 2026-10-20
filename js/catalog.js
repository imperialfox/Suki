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
  return 1 - editDist(a, b) / Math.max(a.length, b.length);
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
    if (best >= 0.56) sum += best;
  }
  return (
    (sum / toks.length) * 72 + Math.max(0, ...names.map((n) => likeness(q, n))) * 24 + (sum / toks.length === 1 ? 4 : 0)
  );
}
function searchItems(q, max = 12) {
  if (!norm(q)) return [];
  return CATALOG.map((i) => ({ i, s: score(i, q) }))
    .filter((x) => x.s >= 38)
    .sort((a, b) => b.s - a.s)
    .slice(0, max)
    .map((x) => x.i);
}
