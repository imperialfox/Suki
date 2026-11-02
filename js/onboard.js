/* Suki · onboard.js (Q07)
   Getting going without a tour, following Apple's onboarding guidance:
   - Opened in a Safari tab on iPhone or iPad: a sheet with the three steps to add Suki to the Home Screen.
   - The first Home Screen launch with nothing saved: one welcome card.
   - Tips, one at a time, next to the hidden gestures they explain. Each goes when you do it or tap ✕.
   - Settings › Help: show the welcome again, the Show tips switch, the hidden gestures and the Home Screen steps.
   What's been seen lives in localStorage 'suki:onboard' on this device only, never in backups.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const OB_KEY = 'suki:onboard';
let OB = null; // {welcome: seen, tips: on, seen: {till, pull, swipe, sheet}}
function obLoad() {
  try {
    const o = JSON.parse(localStorage.getItem(OB_KEY) || 'null');
    if (o && typeof o === 'object') return { welcome: !!o.welcome, tips: !!o.tips, seen: o.seen && typeof o.seen === 'object' ? o.seen : {} };
  } catch (e) {}
  return null;
}
function obSave() {
  try {
    localStorage.setItem(OB_KEY, JSON.stringify(OB));
  } catch (e) {}
}
// iPhone or iPad Safari, not the Home Screen app: that's where the Home Screen steps help
const inBrowserTab = () => APPLE && navigator.maxTouchPoints > 0 && navigator.standalone === false;
const TOUCH = () => navigator.maxTouchPoints > 0 || 'ontouchstart' in window;

/* ===== Starting: after the launch screen has gone ===== */
function onboardStart() {
  OB = obLoad();
  if (!OB) {
    // a fresh install gets the welcome and tips; an install that already has data (an update) gets neither
    const has = D.purchases.length + D.observations.length > 0;
    OB = { welcome: has, tips: !has, seen: {} };
    obSave();
  }
  if (inBrowserTab()) return openSheet('ahs', { safari: true });
  if (!OB.welcome && !D.purchases.length && !D.observations.length) return openSheet('welcome');
  maybeTip();
}

/* ===== The welcome card and the Home Screen steps (drawn by sheetHTML in ui.js) ===== */
const WELCOME_ROWS = [
  ['blue', 'convert', 'Convert and count change', 'Pesos to pounds, and the change you’re owed at the till.'],
  ['orange', 'search', 'Look up fair prices', 'What dishes, groceries and fares usually cost, with sources.'],
  ['green', 'spending', 'Track your spending', 'Log what you buy and see where your money goes.'],
];
function welcomeBody() {
  return (
    '<div class="wel"><img class="wico" src="apple-touch-icon.png" alt="" width="84" height="84"><h1>Welcome to Suki</h1>' +
    WELCOME_ROWS.map((r) => '<div class="wrow">' + stile(r[1], r[0]) + '<div><b>' + r[2] + '</b><span>' + r[3] + '</span></div></div>').join('') +
    '<div class="wsp"></div><p class="wnote">Works with no signal once it’s been opened.</p><button class="cta" data-a="welcomeGo">Continue</button></div>'
  );
}
function ahsBody(safari) {
  return (
    '<p class="note center">Opened from your Home Screen, Suki works with no signal and keeps your purchases saved on this phone.</p>' +
    '<div class="grp tiled steps">' +
    '<div class="row">' + stile('upload', 'blue') + '<span class="lbl"><b>1. Tap ⋯, then Share</b></span></div>' +
    '<div class="row">' + stile('plus', 'blue') + '<span class="lbl"><b>2. Choose Add to Home Screen</b><small>Keep Open as Web App on, then tap Add</small></span></div>' +
    '<div class="row"><img class="appico" src="apple-touch-icon.png" alt="" width="30" height="30"><span class="lbl"><b>3. Open Suki from your Home Screen</b></span></div>' +
    '</div>' +
    (safari ? '<button class="cta" data-a="ahsGot">Got it</button><button class="ghost" data-a="ahsLater">Not now</button>' : '')
  );
}
// Settings › Help › Log by voice with Siri (Q15): the Shortcut he builds on his phone, how to run it, and pasting
// the note into Smart add. The stamp at the start of each line is what lets Suki tell a line is already saved.
const SIRI_STEPS = [
  ['mic', 'purple', 'Dictate Text', 'Language: English (UK). Stop Listening: After Pause'],
  ['clock', 'gray', 'Format Date', 'Current Date, Custom format <code>yyyy-MM-dd HH:mm</code>'],
  ['pencil', 'gray', 'Text', 'Type <code>[</code>, add Formatted Date, type <code>]</code> and a space, then add Dictated Text'],
  ['book', 'yellow', 'Append to Note', 'The Text, to a note called Suki inbox. Make the note in Notes first'],
  ['copy', 'blue', 'Copy to Clipboard', 'The note from step 4, so the clipboard always holds the whole inbox'],
  ['tick', 'green', 'Show Notification', 'Type <code>Saved for Suki:</code> and add Dictated Text, so you can see what Siri heard'],
];
function siriBody() {
  return (
    '<p class="note center">Say a purchase to Siri wherever you are. A Shortcut writes it in a note with the time, and copies the note. Later, paste it into Smart add.</p>' +
    hdr('Make the Shortcut') +
    '<p class="foot top">In Shortcuts, tap +, name it Log to Suki, and add these six actions in order.</p>' +
    '<div class="grp tiled steps" id="siriSteps">' +
    SIRI_STEPS.map((s, i) => '<div class="row">' + stile(s[0], s[1]) + '<span class="lbl"><b>' + (i + 1) + '. ' + s[2] + '</b><small>' + s[3] + '</small></span></div>').join('') +
    '</div><p class="foot">Each line in the note then starts with the time, like <code>[2026-11-21 13:05] tricycle 50 pesos</code>.</p>' +
    hdr('Run it') +
    '<div class="grp tiled steps">' +
    '<div class="row">' + stile('mic', 'purple') + '<span class="lbl"><b>Say “Hey Siri, Log to Suki”</b></span></div>' +
    '<div class="row">' + stile('phone', 'gray') + '<span class="lbl"><b>Or press the Action Button</b><small>Settings › Action Button › Shortcut › Log to Suki</small></span></div>' +
    '<div class="row">' + stile('star', 'blue') + '<span class="lbl"><b>Or add it to your Lock Screen</b><small>Hold the Lock Screen, tap Customise, then a control at the bottom, and choose Shortcut</small></span></div>' +
    '</div>' +
    hdr('In Suki') +
    '<div class="grp tiled steps">' +
    '<div class="row">' + stile('download', 'green') + '<span class="lbl"><b>Open <button class="tlink" data-a="goSmart">Smart add</button> on Home and paste</b><small>Suki shows each purchase before anything is saved</small></span></div>' +
    '<div class="row">' + stile('tick', 'gray') + '<span class="lbl"><b>Paste the whole note every time</b><small>Lines you’ve saved show as Already saved and aren’t saved again</small></span></div>' +
    '</div>' +
    '<p class="foot">Clearing the note is optional. Keep the time at the start of each line: without it Suki still reads the line, but can’t tell it’s already saved.</p>'
  );
}
// the welcome's rows arrive 45 ms apart after the sheet rises; Reduce Motion gives fades only
function welcomeArrive() {
  document.querySelectorAll('#layer .wrow').forEach((r, i) =>
    MOTION.animate(r, [{ transform: 'translateY(16px)', opacity: 0 }, { transform: 'none', opacity: 1 }], { fade: true, delay: 220 + MOTION.stagger(i, 'row'), fill: 'backwards' })
  );
}

/* ===== Tips: one at a time, next to what they explain ===== */
const TIPS = {
  till: { tab: 'till', icon: 'till', t: 'Type or tap what you hand over', b: 'Suki works out your change straight away.', tgt: () => document.querySelector('#app .denoms') },
  pull: { tab: 'home', icon: 'download', t: 'Pull down to refresh', b: 'Checks the rate and fetches any Suki update.', touch: true, tgt: () => document.querySelector('#app h1') },
  swipe: { tab: 'spending', icon: 'back', t: 'Swipe a purchase left', b: 'To delete it. Suki always asks first.', touch: true, tgt: () => document.querySelector('#spendList .sw') },
  sheet: { sheet: true, icon: 'download', t: 'Drag down to close', b: 'Works on every card that slides up.', touch: true, tgt: () => document.querySelector('#layer .sheet:not(.locked) .shead') },
};
const TIP_ORDER = ['till', 'pull', 'swipe', 'sheet'];
const DETAIL_SHEETS = { purchase: 1, item: 1 };
let TIPCUR = null,
  tipT = null;
function tipWanted() {
  if (!OB || !OB.tips || inBrowserTab() || TIPCUR) return null;
  if (U.sheet) {
    const t = TIPS.sheet;
    return DETAIL_SHEETS[U.sheet] && !OB.seen.sheet && TOUCH() && !split() ? 'sheet' : null;
  }
  return TIP_ORDER.find((id) => TIPS[id].tab === U.tab && !OB.seen[id] && (!TIPS[id].touch || TOUCH())) || null;
}
// after a screen or sheet settles, see whether a tip belongs on it
function maybeTip() {
  clearTimeout(tipT);
  if (!OB || !OB.tips) return;
  tipT = setTimeout(() => {
    const id = tipWanted();
    if (id) showTip(id);
  }, MOTION.speed() === 0 ? 0 : 600 * MOTION.speed());
}
function showTip(id) {
  const t = TIPS[id],
    tg = t.tgt();
  if (!tg) return;
  const r = tg.getBoundingClientRect();
  if (!r.width || r.bottom < 0 || r.top > innerHeight) return;
  let el = $('tip');
  if (!el) {
    el = document.createElement('div');
    el.id = 'tip';
    el.className = 'glass';
    el.setAttribute('role', 'status');
    document.body.appendChild(el);
  }
  el.innerHTML =
    '<span class="ar" aria-hidden="true"></span><div class="tt"><span class="tic">' + ICON[t.icon] + '</span>' + t.t + '</div><div class="tb">' + t.b + '</div>' +
    '<button class="tx" data-a="tipX" aria-label="Close tip">' + ICON.x + '</button>';
  el.dataset.id = id;
  TIPCUR = id;
  placeTip();
  el.classList.remove('on');
  void el.offsetWidth;
  el.classList.add('on');
}
// below the target if that covers no main button and stays clear of the tab bar; otherwise above it
function placeTip() {
  const el = $('tip');
  if (!el || !TIPCUR) return;
  const tg = TIPS[TIPCUR].tgt();
  if (!tg) return hideTip();
  const r = tg.getBoundingClientRect(),
    w = Math.min(300, innerWidth - 32),
    h = el.offsetHeight || 84,
    left = Math.max(16, Math.min(innerWidth - w - 16, r.left + r.width / 2 - w / 2)),
    keep = [...document.querySelectorAll('#app .cta, #layer .cta, #dock .tabbar')].map((e) => e.getBoundingClientRect()).filter((b) => b.width),
    hits = (top) => top < 4 || top + h > innerHeight - 4 || keep.some((b) => !(b.right < left || b.left > left + w || b.bottom < top || b.top > top + h));
  let top = r.bottom + 12,
    below = true;
  if (hits(top)) {
    top = r.top - h - 12;
    below = false;
  }
  el.style.width = w + 'px';
  el.style.left = left + 'px';
  el.style.top = top + 'px';
  el.classList.toggle('below', below);
  el.classList.toggle('above', !below);
  const ax = Math.max(18, Math.min(w - 34, r.left + r.width / 2 - left - 8));
  el.querySelector('.ar').style.left = ax + 'px';
  el.style.transformOrigin = ax + 8 + 'px ' + (below ? '0' : '100%');
}
function hideTip() {
  clearTimeout(tipT);
  const el = $('tip');
  TIPCUR = null;
  if (!el) return;
  el.classList.remove('on');
  setTimeout(() => !TIPCUR && el.remove(), MOTION.on() ? 200 : 0);
}
// a tip goes for good once you do what it explains, or tap ✕
function tipDone(id) {
  if (!OB || OB.seen[id]) return;
  OB.seen[id] = true;
  obSave();
  if (TIPCUR === id) hideTip();
}
// after every redraw: a tip whose screen has gone is hidden (not done), then a tip that belongs here can show
function tipsAfterRender() {
  if (!OB) return;
  if (TIPCUR) {
    const t = TIPS[TIPCUR],
      here = t.sheet ? DETAIL_SHEETS[U.sheet] : !U.sheet && U.tab === t.tab;
    if (!here || !t.tgt()) hideTip();
    else placeTip();
  }
  if (!TIPCUR) maybeTip();
}
// a tip follows its target as the page scrolls; one whose target was below the fold shows once it's scrolled into view
let tipRaf = 0;
const tipFollow = () => {
  if (tipRaf || !OB || !OB.tips) return;
  tipRaf = requestAnimationFrame(() => {
    tipRaf = 0;
    if (TIPCUR) placeTip();
    else maybeTip();
  });
};
addEventListener('scroll', tipFollow, { capture: true, passive: true });
addEventListener('resize', tipFollow);
function setTips(on) {
  OB.tips = !!on;
  if (on) OB.seen = {};
  else hideTip();
  obSave();
  toast(on ? 'Tips will show again' : 'Tips off');
}

/* ===== Settings › Help ===== */
function scrHelp() {
  const gest = [
    ['download', 'Pull down', 'On Home or Spending, to refresh'],
    ['back', 'Swipe a purchase left', 'To delete it'],
    ['chevdown', 'Drag a sheet down by its top', 'To close it'],
    ['cal', 'Tap Home’s title', 'To open the calendar (Spending’s date does too)'],
  ];
  return (
    '<h1>Help</h1>' +
    '<div class="grp tiled set">' +
    '<button class="row" data-a="showWelcome">' + stile('star', 'orange') + '<span class="lbl"><b>Show welcome</b><small>The card new users see first</small></span>' + ICON.chev + '</button>' +
    '<label class="row toggle">' + stile('bulb', 'yellow') + '<span class="lbl"><b>Show tips</b></span><input type="checkbox" role="switch" data-a="tipsToggle"' + (OB && OB.tips ? ' checked' : '') + '><span class="sw-ui" aria-hidden="true"></span></label>' +
    '</div><p class="foot">Tips appear once each, next to what they explain. Turning this on shows them all again.</p>' +
    hdr('Hidden gestures') +
    '<div class="grp tiled set">' + gest.map((g) => '<div class="row">' + stile(g[0], 'gray') + '<span class="lbl"><b>' + g[1] + '</b><small>' + g[2] + '</small></span></div>').join('') + '</div>' +
    hdr('Logging') +
    '<div class="grp tiled set"><button class="row" data-a="openSiri">' + stile('mic', 'purple') + '<span class="lbl"><b>Log by voice with Siri</b><small>Say a purchase anywhere, paste it in later</small></span>' + ICON.chev + '</button></div>' +
    hdr('On a new phone') +
    '<div class="grp tiled set"><button class="row" data-a="openAhs">' + stile('phone', 'blue') + '<span class="lbl"><b>Add Suki to your Home Screen</b></span>' + ICON.chev + '</button></div>'
  );
}
SCREENS.help = scrHelp;
NARROW.help = 1;
TAB_TITLE.help = 'Help';
