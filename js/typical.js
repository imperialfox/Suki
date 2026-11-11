/* Suki · typical.js
   Typical prices with their sources, researched 31 Oct 2026 (Q02). Each item id points at a catalogue id.
   kind: fare (set by LTFRB), srp (DTI suggested retail price), shop (a supermarket shelf price), menu (the chain’s own menu),
   listed (published by the company or a news report), guide (a rough guide from travel writers).
   To update: replace a value and its source, url and date together. Never guess a price.
   tests/test_prices.py checks every row (MAINTAINING.md › Updating the typical prices). Rechecked 11 Nov 2026 (Q35); medicines added 11 Nov 2026 (Q37); toiletries, money costs, Intramuros and a haircut added, and the dishes priced
   as one carinderia plate, 11 Nov 2026 (Q38). */
window.sukiTypical = {
 "checked": "2026-11-11",
 "items": {
  "jeepney": [
   {
    "label": "Traditional jeepney",
    "low": 14,
    "high": 14,
    "unit": "first 4 km",
    "area": "Nationwide (LTFRB)",
    "kind": "fare",
    "source": "GMA News",
    "url": "https://www.gmanetwork.com/news/money/economy/1003882/puvs-must-post-fare-matrix-before-charging-higher-fares-acto/story/",
    "date": "2026-09-27",
    "note": "Then ₱2 a km. New fare from 28 Sep 2026 (was ₱13). Drivers must show the new fare matrix before charging it."
   },
   {
    "label": "Modern jeepney",
    "low": 17,
    "high": 17,
    "unit": "first 4 km",
    "area": "Nationwide (LTFRB)",
    "kind": "fare",
    "source": "GMA News",
    "url": "https://www.gmanetwork.com/news/money/economy/1003882/puvs-must-post-fare-matrix-before-charging-higher-fares-acto/story/",
    "date": "2026-09-27",
    "note": "Then ₱2.40 a km. New fare from 28 Sep 2026 (was ₱15)."
   }
  ],
  "bus-city": [
   {
    "label": "Ordinary city bus",
    "low": 15,
    "high": 15,
    "unit": "first 5 km",
    "area": "Metro Manila / city buses (LTFRB)",
    "kind": "fare",
    "source": "Top Gear Philippines",
    "url": "https://www.topgear.com.ph/news/industry-news/dotr-fare-hike-september-28-2026-a6941-20260928",
    "date": "2026-09-28",
    "note": "Then ₱2.49 a km."
   },
   {
    "label": "Air-con city bus",
    "low": 18,
    "high": 18,
    "unit": "first 5 km",
    "area": "Metro Manila / city buses (LTFRB)",
    "kind": "fare",
    "source": "Top Gear Philippines",
    "url": "https://www.topgear.com.ph/news/industry-news/dotr-fare-hike-september-28-2026-a6941-20260928",
    "date": "2026-09-28",
    "note": "Then ₱2.98 a km."
   }
  ],
  "bus-sanjose": [
   {
    "label": "Cubao to San Jose City (Baliwag Transit)",
    "low": 339,
    "high": 339,
    "unit": "one way",
    "area": "Cubao (QC) → San Jose City, Nueva Ecija",
    "kind": "guide",
    "source": "Out of Town Blog",
    "url": "https://outoftownblog.com/baliwag-transit-bus-schedule-terminals-routes-and-fare-rates/",
    "date": "2026-08-30",
    "note": "Listed before the 28 Sep 2026 fare rise, so it’s likely a little higher now. Check at the ticket counter."
   },
   {
    "label": "Cubao to Cabanatuan (Baliwag Transit)",
    "low": 257,
    "high": 275,
    "unit": "one way",
    "area": "Cubao (QC) ↔ Cabanatuan City, Nueva Ecija",
    "kind": "guide",
    "source": "Out of Town Blog",
    "url": "https://outoftownblog.com/baliwag-transit-bus-schedule-terminals-routes-and-fare-rates/",
    "date": "2026-08-30",
    "note": "Listed before the 28 Sep 2026 fare rise. ₱257 towards Cabanatuan, ₱275 back to Cubao."
   }
  ],
  "tricycle": [
   {
    "label": "Dagupan, Pangasinan",
    "low": 20,
    "high": 30,
    "unit": "shortest ride",
    "area": "Dagupan City, Pangasinan (Luzon example, not Nueva Ecija)",
    "kind": "listed",
    "source": "Sunday Punch, Dagupan",
    "url": "https://punch.dagupan.com/?p=617793",
    "date": "2025-11-02",
    "note": "First 2 km, then ₱10 a km. ₱20 a passenger on a shared ride, ₱30 for a special trip on your own. No fare for San Jose City is published online."
   },
   {
    "label": "City of Manila",
    "low": 16,
    "high": 16,
    "unit": "shortest ride",
    "area": "City of Manila (LGU ordinance)",
    "kind": "listed",
    "source": "Inquirer",
    "url": "https://newsinfo.inquirer.net/1856068/manila-sets-new-tricycle-pedicab-fare-of-p16-for-first-kilometer-of-trip",
    "date": "2023-11-07",
    "note": "First 1 km, then ₱5 every 500 m. Set in 2023; it may have changed since."
   }
  ],
  "grab": [
   {
    "label": "Grab or other ride-hailing car, base fare",
    "low": 55,
    "high": 165,
    "unit": "base fare, by car type",
    "area": "Nationwide TNVS (LTFRB)",
    "kind": "fare",
    "source": "SunStar",
    "url": "https://www.sunstar.com.ph/manila/ltfrb-sets-new-puv-rates-effective-sept-28",
    "date": "2026-09-29",
    "note": "Hatchback ₱55, sedan ₱65, SUV ₱75, premium ₱165. Then ₱13–18 a km and ₱2 a minute."
   }
  ],
  "taxi": [
   {
    "label": "Metered taxi, flag-down",
    "low": 65,
    "high": 65,
    "unit": "flag-down, then ₱13.50 a km and ₱2 a minute",
    "area": "Nationwide (LTFRB), provisional",
    "kind": "fare",
    "source": "Philstar",
    "url": "https://www.philstar.com/headlines/2026/09/27/2559277/jeepney-fares-p14-starting-sept-28-buses-taxis-tnvs-also-hike-rates",
    "date": "2026-09-27",
    "note": "Provisional fare from 28 Sep 2026 (was ₱50)."
   }
  ],
  "taxi-naia": [
   {
    "label": "Yellow airport taxi, flag-down",
    "low": 115,
    "high": 115,
    "unit": "first 500 m, then ₱4 every 300 m",
    "area": "NAIA (Manila airport)",
    "kind": "fare",
    "source": "Philstar",
    "url": "https://www.philstar.com/headlines/2026/09/27/2559277/jeepney-fares-p14-starting-sept-28-buses-taxis-tnvs-also-hike-rates",
    "date": "2026-09-27",
    "note": "New flag-down from 28 Sep 2026 (was ₱75)."
   }
  ],
  "bus-naia": [
   {
    "label": "UBE Express, NAIA Terminal 3 to Cubao",
    "low": 200,
    "high": 200,
    "unit": "one way, cash",
    "area": "NAIA Terminal 3 → Araneta City Cubao",
    "kind": "listed",
    "source": "Top Gear Philippines",
    "url": "https://www.topgear.com.ph/features/feature-articles/naia-cubao-p2p-bus-2026-guide-a4682-20260401-lfrm",
    "date": "2026-04-01",
    "note": "April 2026 fare. Airport buses went up 15% on 28 Sep 2026, so it may be higher now."
   }
  ],
  "mrt3": [
   {
    "label": "MRT-3, North Avenue to Taft",
    "low": 6,
    "high": 14,
    "unit": "shortest to longest ride",
    "area": "Metro Manila (EDSA)",
    "kind": "listed",
    "source": "Manila Bulletin",
    "url": "https://mb.com.ph/2026/03/19/mrt-3-lrt-2-to-implement-50-fare-discount-starting-march-23",
    "date": "2026-03-19",
    "note": "Half price for everyone since 23 Mar 2026 (DOTr), until further notice. Full fare ₱13–28."
   }
  ],
  "lrt1": [
   {
    "label": "LRT-1",
    "low": 16,
    "high": 55,
    "unit": "shortest to longest ride",
    "area": "Metro Manila (Taft / Rizal Ave / Cavite ext.)",
    "kind": "fare",
    "source": "Top Gear Philippines",
    "url": "https://topgear.com.ph/news/motoring-news/lrt-1-price-hike-2025-a6888-20250402",
    "date": "2025-04-02",
    "note": "Single-journey ticket ₱20–55; beep card ₱16–52. Not included in the half-price offer."
   }
  ],
  "lrt2": [
   {
    "label": "LRT-2, Recto to Antipolo",
    "low": 8,
    "high": 18,
    "unit": "shortest to longest ride",
    "area": "Metro Manila / Rizal",
    "kind": "listed",
    "source": "Manila Bulletin",
    "url": "https://mb.com.ph/2026/03/19/mrt-3-lrt-2-to-implement-50-fare-discount-starting-march-23",
    "date": "2026-03-19",
    "note": "Half price for everyone since 23 Mar 2026 (DOTr), until further notice. Single-journey ticket; a beep card can be a little less. Full fare ₱15–35 (LRTA, Aug 2023)."
   }
  ],
  "uv": [
   {
    "label": "UV Express",
    "low": 2.6,
    "high": 3,
    "unit": "per km",
    "area": "Nationwide (LTFRB), provisional",
    "kind": "fare",
    "source": "Philstar",
    "url": "https://www.philstar.com/headlines/2026/09/27/2559277/jeepney-fares-p14-starting-sept-28-buses-taxis-tnvs-also-hike-rates",
    "date": "2026-09-27",
    "note": "Provisional from 28 Sep 2026. Traditional ₱2.60 a km, modern ₱3.00 a km."
   }
  ],
  "sim": [
   {
    "label": "Globe prepaid SIM",
    "low": 59,
    "high": 59,
    "unit": "per SIM",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Globe",
    "url": "https://globe.com.ph/prepaid/5g-sim-guide",
    "date": "2026-11-11",
    "note": "You register it with an ID."
   },
   {
    "label": "Globe prepaid eSIM",
    "low": 99,
    "high": 99,
    "unit": "per SIM",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Globe",
    "url": "https://globe.com.ph/prepaid/5g-sim-guide",
    "date": "2026-11-11",
    "note": "Bought in the GlobeOne app. Comes with 2 GB of data and 2 days of unlimited 5G."
   }
  ],
  "sim-tourist": [
   {
    "label": "Smart tourist SIM at the NAIA booth",
    "low": 500,
    "high": 1000,
    "unit": "per package",
    "area": "NAIA, Pasay",
    "kind": "guide",
    "source": "Trvlogue",
    "url": "https://www.trvlogue.com/en/manila-airport-sim-prices",
    "date": "2026-08-08",
    "note": "Airport packages are dearer than a normal SIM and promo from a convenience store."
   }
  ],
  "data": [
   {
    "label": "Globe GoPLUS99 · 8 GB + 8 GB for apps, 7 days",
    "low": 99,
    "high": 99,
    "unit": "per promo",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Globe",
    "url": "https://www.globe.com.ph/go/technology/article/ultimate-list-globe-prepaid-data-promos",
    "date": "2026-11-11"
   },
   {
    "label": "Smart Power All 109 · 10 GB + extras, 7 days",
    "low": 109,
    "high": 109,
    "unit": "per promo",
    "area": "Nationwide",
    "kind": "listed",
    "source": "WalasTech",
    "url": "https://walastech.com/news/new-smart-power-all-prepaid-promos-2026/",
    "date": "2026-07-01"
   },
   {
    "label": "Smart Magic Data 99 · 2 GB, no expiry",
    "low": 99,
    "high": 99,
    "unit": "per promo",
    "area": "Nationwide",
    "kind": "guide",
    "source": "Unbox",
    "url": "https://unbox.ph/news/ph-digital-and-tech/smart-magic-data-no-expiry/amp/",
    "date": "2021-03",
    "note": "From Smart’s launch of the promo in March 2021."
   }
  ],
  "laundry": [
   {
    "label": "Wash, dry and fold",
    "low": 50,
    "high": 90,
    "unit": "per kg, usually 4–5 kg minimum",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Laundry Atlas",
    "url": "https://laundryatlas.com/blog/how-much-does-laundry-cost-in-manila",
    "date": "2026-03-01"
   }
  ],
  "massage": [
   {
    "label": "Home-service massage",
    "low": 500,
    "high": 1000,
    "unit": "1 hour",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Bed n Body",
    "url": "https://bednbody.ph/bednbody-newsroom-guide-how-much-home-massage-cost-philippines",
    "date": "2026-09-04"
   },
   {
    "label": "Spa massage (Swedish)",
    "low": 700,
    "high": 2500,
    "unit": "1 hour",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Top Massage Manila",
    "url": "https://topmassagemanila.com/massage-price-manila",
    "date": "2026-04-19"
   }
  ],
  "chickenjoy": [
   {
    "label": "1-pc Chickenjoy with rice and a drink",
    "low": 99,
    "high": 99,
    "unit": "per meal",
    "area": "Nationwide",
    "kind": "menu",
    "source": "Jollibee",
    "url": "https://www.jollibee.com.ph/news/jollibee-chickenjoy-sarap-savers",
    "date": "2026-01-14"
   },
   {
    "label": "1-pc Chickenjoy, regular menu, alone or with a drink",
    "low": 106,
    "high": 111,
    "unit": "per meal",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Jon to the World",
    "url": "https://jontotheworld.com/jollibee-menu-with-prices/",
    "date": "2026-09-18"
   }
  ],
  "yumburger": [
   {
    "label": "Yumburger",
    "low": 45,
    "high": 56,
    "unit": "per burger",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Jollibee",
    "url": "https://www.jollibee.com.ph/news/jollibee-surprises-commuters-nationwide",
    "date": "2026-02-20",
    "note": "Jollibee said ₱45 in February 2026; a September list says from ₱56."
   }
  ],
  "chickenmcdo": [
   {
    "label": "1-pc Chicken McDo with rice and a drink",
    "low": 99,
    "high": 99,
    "unit": "per meal, from",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Daily Tribune",
    "url": "https://tribune.net.ph/2026/09/01/bigger-savings-fuller-chicken-how-mcdo-keeps-filipinos-coming-back-for-more",
    "date": "2026-09-01"
   }
  ],
  "pm1": [
   {
    "label": "PM1: Paa Large with 1 rice",
    "low": 139,
    "high": 139,
    "unit": "per meal",
    "area": "Nationwide",
    "kind": "menu",
    "source": "Mang Inasal",
    "url": "https://www.manginasal.ph/news/menu-and-prices",
    "date": "2026-08-01",
    "note": "₱170 with a drink."
   }
  ],
  "latte": [
   {
    "label": "Starbucks caffè latte, tall",
    "low": 160,
    "high": 160,
    "unit": "per cup",
    "area": "Nationwide",
    "kind": "listed",
    "source": "Out of Town Blog",
    "url": "https://outoftownblog.com/starbucks-menu-philippines/",
    "date": "2026-08-15",
    "note": "Delivery price; branches vary."
   }
  ],
  "fishball": [
   {
    "label": "Fish ball",
    "low": 10,
    "high": 30,
    "unit": "per stick",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Mighty Travels",
    "url": "https://www.mightytravels.com/2026/08/manila-food-budget-reality-284month-carinderias-and-points/",
    "date": "2026-08-01"
   }
  ],
  "kikiam": [
   {
    "label": "Kikiam",
    "low": 5,
    "high": 30,
    "unit": "per stick",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Things to Do Manila",
    "url": "https://thingstodomanila.com/street-food/",
    "date": "2026-09"
   }
  ],
  "kwek": [
   {
    "label": "Kwek-kwek",
    "low": 10,
    "high": 30,
    "unit": "per stick",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "TravelStar360",
    "url": "https://travelstar360.com/manila-street-food-price-guide/",
    "date": "2026-04-27"
   }
  ],
  "isaw": [
   {
    "label": "Isaw",
    "low": 10,
    "high": 25,
    "unit": "per stick",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Things to Do Manila",
    "url": "https://thingstodomanila.com/street-food/",
    "date": "2026-09"
   }
  ],
  "bananacue": [
   {
    "label": "Banana cue",
    "low": 15,
    "high": 40,
    "unit": "per stick",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "TravelStar360",
    "url": "https://travelstar360.com/manila-street-food-price-guide/",
    "date": "2026-04-27"
   }
  ],
  "turon": [
   {
    "label": "Turon",
    "low": 15,
    "high": 40,
    "unit": "per piece",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "TravelStar360",
    "url": "https://travelstar360.com/manila-street-food-price-guide/",
    "date": "2026-04-27"
   }
  ],
  "taho": [
   {
    "label": "Taho",
    "low": 20,
    "high": 50,
    "unit": "per cup",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Things to Do Manila",
    "url": "https://thingstodomanila.com/street-food/",
    "date": "2026-09"
   }
  ],
  "siomai": [
   {
    "label": "Master Siomai, 4 pieces",
    "low": 60,
    "high": 75,
    "unit": "per order",
    "area": "Metro Manila (Quezon City branch)",
    "kind": "guide",
    "source": "foodpanda",
    "url": "https://www.foodpanda.ph/restaurant/q44r/master-siomai-robinsons-holy-spirit",
    "date": "2026-11-11",
    "note": "Delivery app price, ₱60 on offer and ₱75 normally. At the kiosk it can be less."
   }
  ],
  "halo": [
   {
    "label": "Mang Inasal halo-halo",
    "low": 70,
    "high": 95,
    "unit": "per serving",
    "area": "Nationwide",
    "kind": "menu",
    "source": "Mang Inasal",
    "url": "https://www.manginasal.ph/news/menu-and-prices",
    "date": "2026-08-01"
   },
   {
    "label": "From a stall",
    "low": 20,
    "high": 60,
    "unit": "per serving",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "TravelStar360",
    "url": "https://travelstar360.com/manila-street-food-price-guide/",
    "date": "2026-04-27"
   }
  ],
  "pandesal": [
   {
    "label": "Neighbourhood bakery",
    "low": 2,
    "high": 2.5,
    "unit": "per piece",
    "area": "Philippines (national)",
    "kind": "listed",
    "source": "Malaya Business Insight",
    "url": "https://malaya.com.ph/business/business-news/community-bakers-disappear-as-pandesal-shrinks",
    "date": "2025-09-13",
    "note": "Bakers say pieces have shrunk to about 18 g."
   },
   {
    "label": "Pinoy Pandesal, from a pack of 10",
    "low": 2.73,
    "high": 2.73,
    "unit": "per piece",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11",
    "note": "Sold in a pack of 10 for ₱27.25."
   }
  ],
  "carinderia": [
   {
    "label": "A carinderia plate: one ulam with rice",
    "low": 50,
    "high": 90,
    "unit": "per plate",
    "area": "Metro Manila",
    "kind": "guide",
    "source": "Mighty Travels",
    "url": "https://www.mightytravels.com/2026/08/manila-food-budget-reality-284month-carinderias-and-points/",
    "date": "2026-08-01",
    "note": "A plate of one ulam with rice at a carinderia or turo-turo. Prices vary by place and dish."
   }
  ],
  "tubig": [
   {
    "label": "Nature's Spring Purified Water · 500 ml",
    "low": 10.5,
    "high": 10.5,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Nature's Spring Purified Water · 1 L",
    "low": 16.5,
    "high": 16.5,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Wilkins Pure (purified) · 500 ml",
    "low": 11,
    "high": 11,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Wilkins Pure (purified) · 1 L",
    "low": 18,
    "high": 18,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Summit Mineralized Water · 500 ml",
    "low": 12,
    "high": 12,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Absolute Distilled Water · 500 ml",
    "low": 16.75,
    "high": 16.75,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Absolute Distilled Water · 1 L",
    "low": 25,
    "high": 25,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "softdrinks": [
   {
    "label": "Coca-Cola can",
    "low": 35.75,
    "high": 39,
    "unit": "per bottle/can",
    "area": "Metro Supermarket online / Pandamart QC",
    "kind": "shop",
    "source": "foodpanda",
    "url": "https://www.foodpanda.ph/groceries/product/GX190F/coke-regular-can-320ml",
    "date": "2026-10-31"
   },
   {
    "label": "Coca-Cola 500 ml",
    "low": 38.25,
    "high": 38.25,
    "unit": "per bottle/can",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=coke&post_type=product",
    "date": "2026-10-31"
   },
   {
    "label": "Coca-Cola 1.5 litres",
    "low": 66.75,
    "high": 67.5,
    "unit": "per bottle/can",
    "area": "Metro Supermarket online / Pandamart QC",
    "kind": "shop",
    "source": "foodpanda",
    "url": "https://www.foodpanda.ph/groceries/product/10F7M0/coke-regular-bottle-15l",
    "date": "2026-10-31"
   }
  ],
  "beer": [
   {
    "label": "San Miguel Pale Pilsen, 320 ml bottle",
    "low": 58.3,
    "high": 58.3,
    "unit": "per bottle/can",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/product/san-miguel-pale-pilsen-320ml/",
    "date": "2026-10-31",
    "note": "Supermarket price; bars and sari-sari stores differ."
   },
   {
    "label": "San Miguel Pale Pilsen, can",
    "low": 54.5,
    "high": 57,
    "unit": "per bottle/can",
    "area": "Metro Supermarket online / Pandamart QC",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/product/san-miguel-beer-pale-pilsen-can-330ml/",
    "date": "2026-10-31"
   },
   {
    "label": "Red Horse, 500 ml bottle",
    "low": 70.8,
    "high": 70.8,
    "unit": "per bottle/can",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/product/redhorse-bottle-500ml/",
    "date": "2026-10-31"
   },
   {
    "label": "Red Horse, can",
    "low": 58,
    "high": 59.5,
    "unit": "per bottle/can",
    "area": "Metro Supermarket online / Pandamart QC",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/brand/red-horse/",
    "date": "2026-10-31"
   }
  ],
  "gatorade": [
   {
    "label": "Gatorade 500 ml",
    "low": 49,
    "high": 49,
    "unit": "per bottle",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=gatorade&post_type=product",
    "date": "2026-10-31"
   }
  ],
  "kape": [
   {
    "label": "Nescafe Original 3-in-1 · 20 g",
    "low": 7.75,
    "high": 7.75,
    "unit": "per sachet",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Great Taste Original Twin Pack · 33 g",
    "low": 10,
    "high": 10,
    "unit": "per sachet",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Kopiko Black 3-in-1 · 30 g",
    "low": 8.5,
    "high": 8.5,
    "unit": "per sachet",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "San Mig Coffee 3-in-1 Original · 20 g",
    "low": 7.5,
    "high": 7.5,
    "unit": "per sachet",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "noodles": [
   {
    "label": "Lucky Me! Instant Mami (Chicken na Chicken / Beef na Beef) · 55 g",
    "low": 9,
    "high": 9,
    "unit": "per pack",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Payless Instant Mami (Chicken Espesyal / Beef Paborito) · 55 g",
    "low": 7.5,
    "high": 7.5,
    "unit": "per pack",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Lucky Me! Pancit Canton (Original / Kalamansi / Chilimansi / Sweet & Spicy) · 80 g",
    "low": 14.75,
    "high": 14.75,
    "unit": "per pack",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=pancit+canton&post_type=product",
    "date": "2026-10-31"
   }
  ],
  "sardinas": [
   {
    "label": "555 Sardines Bonus Pack · 155 g",
    "low": 20.5,
    "high": 20.5,
    "unit": "per can",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Mikado Sardines (regular lid) · 155 g",
    "low": 22.5,
    "high": 22.5,
    "unit": "per can",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Saba Philippines Sardines · 155 g",
    "low": 21.5,
    "high": 21.5,
    "unit": "per can",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Ligo Sardines in Tomato Sauce (easy open) · 155 g",
    "low": 24.5,
    "high": 24.5,
    "unit": "per can",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=ligo+sardines&post_type=product",
    "date": "2026-10-31"
   }
  ],
  "cornedbeef": [
   {
    "label": "Argentina Corned Beef · 150 g",
    "low": 36.75,
    "high": 36.75,
    "unit": "per can",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "tasty": [
   {
    "label": "Pinoy Tasty (loaf) · 450 g",
    "low": 44,
    "high": 44,
    "unit": "per loaf",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "asin": [
   {
    "label": "Lasap Iodized Salt · 250 g",
    "low": 9.75,
    "high": 9.75,
    "unit": "per pack",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Fidel Refined Salt (Blue) · 250 g",
    "low": 11.75,
    "high": 11.75,
    "unit": "per pack",
    "area": "Luzon (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "asukal": [
   {
    "label": "Sampaguita Refined Sugar · 250 g",
    "low": 18.75,
    "high": 18.75,
    "unit": "per pack",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=sugar&post_type=product",
    "date": "2026-10-31"
   }
  ],
  "suka": [
   {
    "label": "Datu Puti White Vinegar (bottle) · 350 ml",
    "low": 19.25,
    "high": 19.25,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "toyo": [
   {
    "label": "Silver Swan Soy Sauce (bottle) · 350 ml",
    "low": 22.25,
    "high": 22.25,
    "unit": "per bottle",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "mantika": [
   {
    "label": "Golden Fiesta Cooking Oil (stand-up pouch) · 1 L",
    "low": 144.5,
    "high": 144.5,
    "unit": "per pouch",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=cooking+oil&post_type=product",
    "date": "2026-10-31"
   }
  ],
  "gatas": [
   {
    "label": "Bear Brand Powdered Milk · 135 g",
    "low": 50,
    "high": 50,
    "unit": "per pack",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "sabon": [
   {
    "label": "Safeguard Pure White bath soap · 55 g",
    "low": 22,
    "high": 22,
    "unit": "per bar",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Safeguard Pure White bath soap · 119 g",
    "low": 49,
    "high": 49,
    "unit": "per bar",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "detergent": [
   {
    "label": "Tide Bar Original Scent (laundry bar) · 380 g",
    "low": 24,
    "high": 24,
    "unit": "per bar",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Surf Bar Active Clean (Blue) · 360 g",
    "low": 23.25,
    "high": 23.25,
    "unit": "per bar",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   },
   {
    "label": "Champion Bar (Supra Clean / Citrus Fresh) · 370 g",
    "low": 25,
    "high": 25,
    "unit": "per bar",
    "area": "Nationwide (DTI SRP)",
    "kind": "srp",
    "source": "DTI price bulletin",
    "url": "https://dtiwebfiles.s3.ap-southeast-1.amazonaws.com/e-Presyo/SRP+Basic+Necessities+and+Prime+Commodities/2026/BNPC+SRP+BULLETIN.11+MAY+2026.0010.PSU+[CLEAN+A3-final].pdf",
    "date": "2026-05-11"
   }
  ],
  "toothpaste": [
   {
    "label": "Colgate Fresh Confidence toothpaste · 110 g",
    "low": 102.05,
    "high": 102.05,
    "unit": "per tube",
    "area": "Metro Supermarket (online)",
    "kind": "shop",
    "source": "Metro Supermarket",
    "url": "https://shopmetro.ph/?s=colgate&post_type=product",
    "date": "2026-10-31"
   }
  ],
  "paracetamol": [
   {
    "label": "Paracetamol 500 mg tablet, PhilHealth GAMOT fee",
    "low": 2.25,
    "high": 2.25,
    "unit": "per tablet",
    "area": "Nationwide (PhilHealth GAMOT)",
    "kind": "listed",
    "source": "PhilHealth Circular 2026-0018",
    "url": "https://www.philhealth.gov.ph/circulars/2026/PC-2026-0018.pdf",
    "date": "2026-10",
    "note": "What PhilHealth pays its partner pharmacies for one tablet under its GAMOT benefit. A pharmacy’s own shelf price may be higher."
   }
  ],
  "ors": [
   {
    "label": "Oral rehydration salts sachet, PhilHealth GAMOT fee",
    "low": 12,
    "high": 12,
    "unit": "per sachet",
    "area": "Nationwide (PhilHealth GAMOT)",
    "kind": "listed",
    "source": "PhilHealth Circular 2026-0018",
    "url": "https://www.philhealth.gov.ph/circulars/2026/PC-2026-0018.pdf",
    "date": "2026-10",
    "note": "What PhilHealth pays its partner pharmacies for one sachet under its GAMOT benefit. A pharmacy’s own shelf price may be higher."
   }
  ],
  "cetirizine": [
   {
    "label": "Cetirizine 10 mg tablet, PhilHealth GAMOT fee",
    "low": 11.25,
    "high": 11.25,
    "unit": "per tablet",
    "area": "Nationwide (PhilHealth GAMOT)",
    "kind": "listed",
    "source": "PhilHealth Circular 2026-0018",
    "url": "https://www.philhealth.gov.ph/circulars/2026/PC-2026-0018.pdf",
    "date": "2026-10",
    "note": "What PhilHealth pays its partner pharmacies for one tablet under its GAMOT benefit. A pharmacy’s own shelf price may be higher."
   }
  ],
  "tisyu": [
   {
    "label": "Orita bathroom tissue, single roll · 2-ply, 400 sheets",
    "low": 20,
    "high": 20,
    "unit": "per roll",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/all-brands/b/166070/orita",
    "date": "2026-11-11"
   },
   {
    "label": "Orita bathroom tissue · 2-ply, from the pack of 12",
    "low": 12.92,
    "high": 12.92,
    "unit": "per roll",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/2-ply-bathroom-tissue-12-rolls/p/BP_10078415",
    "date": "2026-11-11",
    "note": "Sold in a pack of 12 for ₱155."
   }
  ],
  "sunscreen": [
   {
    "label": "Watsons Very High Protection SPF 50+ body lotion · 100 ml",
    "low": 239,
    "high": 299,
    "unit": "per bottle",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/skin-care/for-body/c/031160",
    "date": "2026-11-11",
    "note": "On sale for ₱239 on 11 Nov 2026; ₱299 when not on sale."
   },
   {
    "label": "Nivea Sun Protect & Moisture SPF 50 · 125 ml",
    "low": 678,
    "high": 678,
    "unit": "per bottle",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/skin-care/for-body/c/031160",
    "date": "2026-11-11"
   }
  ],
  "repellent": [
   {
    "label": "OFF! Overtime lotion · 50 ml",
    "low": 146,
    "high": 146,
    "unit": "per bottle",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/off-over-time-insect-repellant-50ml/p/BP_10032576",
    "date": "2026-11-11"
   },
   {
    "label": "OFF! Overtime lotion · 100 ml",
    "low": 219.25,
    "high": 219.25,
    "unit": "per bottle",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/p/BP_10032574",
    "date": "2026-11-11"
   }
  ],
  "diaper": [
   {
    "label": "EQ Pants, medium · from the pack of 24",
    "low": 8.58,
    "high": 8.58,
    "unit": "per piece",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/mom-and-baby/pants-diapers/c/080102",
    "date": "2026-11-11",
    "note": "Sold in a pack of 24 for ₱206."
   },
   {
    "label": "EQ Pants, XL · from the pack of 66",
    "low": 9.52,
    "high": 9.52,
    "unit": "per piece",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/mom-and-baby/pants-diapers/c/080102",
    "date": "2026-11-11",
    "note": "Sold in a pack of 66 for ₱628."
   },
   {
    "label": "Watsons baby pants, XXL · from the pack of 4",
    "low": 15,
    "high": 15,
    "unit": "per piece",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/mom-and-baby/pants-diapers/c/080102",
    "date": "2026-11-11",
    "note": "Sold in a pack of 4 for ₱60."
   }
  ],
  "atm-fee": [
   {
    "label": "BDO ATM, card issued overseas",
    "low": 250,
    "high": 250,
    "unit": "per withdrawal",
    "area": "Nationwide (BDO)",
    "kind": "listed",
    "source": "BDO",
    "url": "https://www.bdo.com.ph/personal/digitalbanking/atm-banking",
    "date": "2026-11-11",
    "note": "BDO’s own fee. Your card’s bank may charge its own fee on top."
   },
   {
    "label": "Landbank ATM, card issued abroad",
    "low": 250,
    "high": 250,
    "unit": "per withdrawal",
    "area": "Nationwide (Landbank)",
    "kind": "listed",
    "source": "Landbank",
    "url": "https://www.landbank.com/images/inner_template/1752131646_Bank-Fees-and-Charges-Peso-Transactions-05302025.pdf",
    "date": "2025-05-13",
    "note": "Landbank’s fee list as of 13 May 2025. Your card’s bank may charge its own fee on top."
   }
  ],
  "money-changer": [
   {
    "label": "BPI’s margin when it buys your pounds",
    "low": 200,
    "high": 200,
    "unit": "per £100 changed",
    "area": "Nationwide (BPI)",
    "kind": "listed",
    "source": "BPI",
    "url": "https://www.bpi.com.ph/personal/bank/forex/rates",
    "date": "2026-11-11",
    "note": "On 11 Nov 2026 BPI bought £1 for ₱82.46 and sold £1 for ₱86.46. Halfway between is ₱84.46, so £100 changed there gets about ₱200 less than halfway. Any money changer works the same way: compare its “we buy” rate with Convert’s rate before you change."
   }
  ],
  "intramuros": [
   {
    "label": "Fort Santiago",
    "low": 75,
    "high": 75,
    "unit": "per adult",
    "area": "Intramuros, Manila",
    "kind": "listed",
    "source": "Intramuros Administration",
    "url": "https://intramuros.gov.ph/?p=11401",
    "date": "2024-05-21",
    "note": "₱50 for children under 18, seniors, students, people with disabilities, solo parents and government employees, with ID."
   },
   {
    "label": "Casa Manila or Baluarte de San Diego",
    "low": 75,
    "high": 75,
    "unit": "per adult",
    "area": "Intramuros, Manila",
    "kind": "listed",
    "source": "Intramuros Administration",
    "url": "https://intramuros.gov.ph/?p=8772",
    "date": "2022-10",
    "note": "Each site charges its own fee. ₱50 for children under 18, seniors, students, people with disabilities and government employees, with ID."
   }
  ],
  "haircut": [
   {
    "label": "Haircut at a barbershop in Ortigas",
    "low": 500,
    "high": 500,
    "unit": "per cut",
    "area": "Pasig, Metro Manila",
    "kind": "listed",
    "source": "The Elephant’s Nook Barbershop",
    "url": "https://theelephantsnookbarbershoportigas.setmore.com",
    "date": "2026-11-11",
    "note": "One shop’s own booking page. Prices vary a lot from shop to shop."
   }
  ],
  "shampoo": [
   {
    "label": "Dove shampoo · 12 ml sachet, from the pack of 6",
    "low": 8.75,
    "high": 8.75,
    "unit": "per sachet",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/hair/everyday-shampoo/c/040304",
    "date": "2026-11-11",
    "note": "Sold in a pack of 6 for ₱52.50."
   },
   {
    "label": "Palmolive Naturals shampoo · 15 ml sachet, from the pack of 6",
    "low": 10.17,
    "high": 10.17,
    "unit": "per sachet",
    "area": "Watsons (online)",
    "kind": "listed",
    "source": "Watsons",
    "url": "https://www.watsons.com.ph/hair/everyday-shampoo/c/040304",
    "date": "2026-11-11",
    "note": "Sold in a pack of 6 for ₱61."
   }
  ]
 }
};
