/* Suki · news.js (Q23)
   The news notes on Rate history: what moved the peso or the pound, in plain words, each linked to the official
   statement or record (bsp.gov.ph, bankofengland.co.uk or psa.gov.ph). Hand-checked; refreshed about monthly, or when
   Ivan asks (MAINTAINING.md › Rate history). Rules, checked by tests/test_history.py: a real date, not in the future;
   a side (peso or pound); a title under about 60 characters; an official link; no two on the same day and side.
   `checked` is the day they were last checked: after a month the page says so and greys the news lane after it.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */
window.sukiNews = {
  checked: '2026-11-03',
  notes: [
    {
      date: '2026-10-27',
      side: 'peso',
      tag: 'BSP',
      title: 'Peso at its weakest ever against the dollar',
      body: 'The peso closed at about ₱64 to the US dollar, its weakest on record, with oil still expensive and prices in the Philippines rising fast. A weaker peso is why your pound buys more pesos.',
      url: 'https://www.bsp.gov.ph/statistics/external/day99_data.aspx',
      src: 'BSP daily peso–dollar rates',
    },
    {
      date: '2026-10-22',
      side: 'peso',
      tag: 'BSP',
      title: 'BSP raises its rate to 5.50%',
      body: 'The Philippine central bank raised its rate by half a point, its biggest rise since February 2023 and the fourth in a row, to bring rising prices under control. A higher rate usually helps a currency, but the peso kept sliding as oil stayed expensive.',
      url: 'https://www.bsp.gov.ph/statistics/keystat/sefi.pdf',
      src: 'Bangko Sentral ng Pilipinas',
    },
    {
      date: '2026-09-17',
      side: 'pound',
      tag: 'BoE',
      title: 'Bank of England holds at 3.75%',
      body: 'The UK’s central bank kept its rate the same, but three of its nine members voted to raise it to 4%. A bank leaning towards higher rates tends to keep the pound steady.',
      url: 'https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/september-2026',
      src: 'Bank of England',
    },
    {
      date: '2026-08-27',
      side: 'peso',
      tag: 'BSP',
      title: 'BSP raises its rate to 5.00%',
      body: 'The third rise this year, as prices kept climbing. The peso still fell to a new low against the dollar the same day.',
      url: 'https://www.bsp.gov.ph/Price%20Stability/MonetaryPolicyReport/FullReport-Aug2026.pdf',
      src: 'Bangko Sentral ng Pilipinas',
    },
    {
      date: '2026-07-30',
      side: 'pound',
      tag: 'BoE',
      title: 'Bank of England holds at 3.75%; three want a rise',
      body: 'The rate stayed the same, with three members wanting it higher, up from two in June.',
      url: 'https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/july-2026',
      src: 'Bank of England',
    },
    {
      date: '2026-06-18',
      side: 'peso',
      tag: 'BSP',
      title: 'BSP raises its rate to 4.75%',
      body: 'A second rise, as price rises spread from fuel into food, wages and transport.',
      url: 'https://www.bsp.gov.ph/SitePages/PriceStability/FullReportMPR/MonetaryPolicyReport-Full-June2026.aspx',
      src: 'Bangko Sentral ng Pilipinas',
    },
    {
      date: '2026-04-23',
      side: 'peso',
      tag: 'BSP',
      title: 'BSP raises its rate to 4.50%',
      body: 'The first rise of the year, after war in the Middle East pushed up oil prices, and with them prices in the Philippines.',
      url: 'https://www.bsp.gov.ph/Price%20Stability/MonetaryPolicyReport/SummaryofMPDecisions-Aug2026.pdf',
      src: 'Bangko Sentral ng Pilipinas',
    },
    {
      date: '2022-09-28',
      side: 'pound',
      tag: 'BoE',
      title: 'Bank of England steps in after the mini-budget',
      body: 'The UK government’s mini-budget on 23 September promised big tax cuts with no plan to pay for them. The pound fell fast and UK government bonds slumped, so the Bank of England stepped in to buy bonds and calm markets. £1 went from ₱66.15 on 22 September to ₱62.62 on the 28th.',
      url: 'https://www.bankofengland.co.uk/news/2022/september/bank-of-england-announces-gilt-market-operation',
      src: 'Bank of England',
    },
    {
      date: '2016-06-24',
      side: 'pound',
      tag: 'BoE',
      title: 'UK votes to leave the EU',
      body: 'The pound fell sharply the day after the vote, and the Bank of England said it was ready to support markets. £1 went from ₱69.04 to ₱64.33 in a day, the biggest one-day fall since the ECB started publishing pesos.',
      url: 'https://www.bankofengland.co.uk/news/2016/june/statement-from-the-governor-of-the-boe-following-the-eu-referendum-result',
      src: 'Bank of England',
    },
    {
      date: '2008-10-08',
      side: 'pound',
      tag: 'BoE',
      title: 'Bank of England cuts its rate as the crisis spreads',
      body: 'After Lehman Brothers collapsed in September, the financial crisis hit the pound hard. The Bank of England cut its rate to 4.5%, alongside other central banks. £1 went from about ₱83 in September to ₱69 by the end of the year.',
      url: 'https://www.bankofengland.co.uk/news/2008/october/mpc-october-2008',
      src: 'Bank of England',
    },
  ],
};
