# Does copying Congress's stock trades beat the market?

Code and summary results for my video on congressional stock trading, on the [I'm A Doctor, Not A Quant](https://www.youtube.com/@ImADoctorNotAQuant) channel.

There are apps and ETFs built around copying what members of Congress buy, so I pulled every disclosure I could parse and tested it.

Short answer: no. Copying every disclosed stock buy, starting the day after the filing went public, returned 11.8% a year vs 13.7% for the S&P 500 (Jan 2014 to Oct 2026, after trading costs). The gap comes from equal weighting. Against the equal-weight S&P 500 it's roughly a tie, and the picks did about as well as random stocks from the same sectors.

## Results

The sample is 39,477 stock trades (20,290 buys, 19,187 sells) by 270 members, Jul 2012 to Oct 2026. The headline strategy buys at the close of the first trading day after each filing, holds for 63 trading days (about 3 months), weights positions equally and pays 10 bps per side.

| | Copy every buy | S&P 500 (SPY) |
| --- | --- | --- |
| Return per year (CAGR) | 11.8% | 13.7% |
| Sharpe ratio | 0.68 | 0.84 |
| Sharpe difference, 95% bootstrap CI | -0.32 to -0.02 | |
| Max drawdown | -35.1% | -33.7% |
| Beta | 1.00 | |
| CAPM alpha | -1.5%/yr (t -1.6) | |
| Fama-French 5 + momentum alpha | -0.7%/yr (t -0.9) | |
| Years beating SPY | 3 of 13 | |

Other findings:

- Members don't seem to know much. Stocks they bought beat their sector by 0.1% over the next 3 months measured from the trade date, and by -0.04% from the filing date. Nothing unusual happens between the trade and the filing.
- The test had enough power to find an edge if there was one. It would catch a real 2.5%/yr edge 80% of the time, and the 95% CI for alpha (-3.3% to +0.3%/yr) rules out anything above +0.3%.
- Where the gap comes from (CAGR): SPY 13.7%, equal-weight S&P 500 (RSP) 11.0%, random stocks from Congress's pool on the same dates 11.2%, random stocks from the same sector as each buy 12.1%, Congress's actual buys 11.8%.
- Against RSP, copying Congress has an alpha of +1.3%/yr (t 1.1) and a Sharpe of 0.68 vs 0.62. I picked this benchmark after seeing earlier results, so treat it as a robustness check, not the main test.
- Copying only the "good" trades doesn't work either. None of 17 pre-registered subgroups (party, chamber, leadership, trades of $100k+, clusters of 3+ members, past winners, the Pelosi household and others) beats luck after a Benjamini-Hochberg correction, and 0 of 15 pass a frozen test (direction learned before 2020, scored from 2020 on). Cluster buys looked great before 2020 (+6.8%/yr, t 2.6) and dropped to +0.6% after.
- 15 robustness variants (exit rules, holding periods, costs, entry day, weighting) give alphas from -3.0% to +2.2%/yr, none with t > 2.
- The NANC and GOP ETFs (Feb 2023 to Oct 2026) show no alpha once their tech tilt is accounted for (-1.1% and -1.2%/yr).
- $10,000 over 12.8 years grows to $41.6k copying vs $51.9k in SPY before tax. With a $120/yr copy-trading app and a simple tax model it's $22.3k to $24.4k vs $45.6k.

Members' own round trips, the leaderboard luck test, chamber-only runs and the delisting and ticker-reuse checks are in `results/`, with figures in `figures/`.

## How it works

`congress_trading.ipynb` runs top to bottom (23 sections):

1. House: the Clerk's yearly index ZIPs and every Periodic Transaction Report PDF. E-filed PDFs are parsed with `pdfplumber` (a parser self-test runs first). Scanned paper filings are counted but not OCR'd.
2. Senate: the official eFD site (efdsearch.senate.gov) blocks scripted access, so Senate trades come from the Senate Stock Watcher archive, which ends in Mar 2021.
3. Members: `unitedstates/congress-legislators` for party, chamber, state and leadership periods.
4. Prices: adjusted closes from Yahoo Finance (`yfinance`). Sectors come from SEC SIC codes mapped to the sector SPDRs, and factors from the Ken French Data Library.
5. Tests: buy-and-hold abnormal returns vs SPY and vs sector (clustered by month, and by month and stock), calendar-time copy portfolios with CAPM and FF5 + momentum alphas (Newey-West), block-bootstrap Sharpe CIs, 500 placebo portfolios, pre-registered subgroups with Benjamini-Hochberg, a frozen out-of-sample split at 2020, robustness runs and survivorship bounds. 31 consistency checks run at the end; 29 pass, and the two that fail are about Senate coverage.

## Limits

- Not every disclosed trade is in here. Scanned paper House filings (29% of House reports, mostly 2014 to 2018) aren't parsed, and Senate trades end in 2021. House trades run 2014 to 2026.
- About 10% of buys couldn't be priced, mostly delisted stocks. For copying to earn +2%/yr overall, those buys would need to beat their sector by about 4% every 3 months.
- Disclosed amounts are ranges, so dollar weights and round-trip profits are approximate.
- The tax example is simplified: copy-trading gains taxed every year at 32% short-term, the index taxed once at 15%, no dividends or state tax.
- The equal-weight benchmark was added after seeing earlier results.

## Reproduce

```bash
pip install -r requirements.txt
jupyter lab congress_trading.ipynb
```

Set `CONTACT_EMAIL` in section 1 first, since the SEC and the House Clerk expect a real contact in the User-Agent. The first run downloads about 8,400 House PDFs and prices for about 2,600 tickers and takes a few hours. Everything is cached in `data_congress/`, which git ignores. For a quick smoke test, set `MAX_PDFS = 300`.

## Data and legal note

Financial disclosure reports are public, but the Ethics in Government Act (5 U.S.C. § 13107) bars using them for commercial purposes other than news and media, or for credit ratings and solicitation. So this repo has code and summary statistics only, not a trade-level dataset. Nothing here alleges wrongdoing by any member of Congress.

## Prior research

- Ziobrowski, Cheng, Boyd and Ziobrowski (2004, 2011): before the STOCK Act, Senate and House portfolios beat the market.
- Eggers and Hainmueller (2013): House members' portfolios did not beat the market from 2004 to 2008.
- Belmont, Sacerdote, Sehgal and Van Hoek (2022), *Journal of Public Economics*: after the STOCK Act, congressional trades look like random stock picking.
- Wei and Zhou (2025), NBER Working Paper 34524: members who become party leaders outperform matched peers after they move up.

## About the code

I built this with a lot of help from AI (Claude). The questions, analysis choices and sanity checks are mine. If you find a bug, please open an issue.

## License

MIT. For education only, not financial advice.
