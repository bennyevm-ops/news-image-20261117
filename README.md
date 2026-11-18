# The Day in One Picture — Tuesday 17 November 2026

Entry for the make.fun bounty **news-image-20261117**: sum up 17 November
2026's world news in one image.

`main.py` draws a newspaper front page for that single day, entirely from
scratch. It uses only the Python standard library: a hand-rolled PNG
encoder (zlib + struct), a small raster canvas (rectangles, circles,
thick lines, polygons) and a hand-authored 5x7 bitmap font. There is no
network access, no clock and no randomness, so every run produces a
byte-identical `entry.png` (1024x1024) in `$MAKEFUN_OUTPUT_DIR`.

## The five stories on the page

1. **Lead — Nvidia smashes estimates.** Nvidia reported quarterly results
   after the US close on 17 November: revenue of $115.8 billion, up 103%
   year on year and well ahead of the roughly $109 billion expected, with
   adjusted earnings per share of $2.68 against $2.47 expected and Data
   Center revenue of $107.6 billion; guidance for the next quarter was
   raised to $130 billion. It was the company's first report under interim
   CEO Colette Kress, who stepped in after Jensen Huang resigned on
   12 November. (Company earnings release, as reported by the financial
   press.)
2. **Stocks fall a fourth day.** Wall Street fell for a fourth straight
   session — the S&P 500 and the Nasdaq each lost about 1.1% — as fears
   about AI valuations gripped markets ahead of Nvidia's numbers, with
   Bitcoin near $64,000 and the market fear gauge at extreme fear.
   (US market session reports.)
3. **Anthropic's $1.5 trillion IPO.** Anthropic was reported during the
   day to be pricing its initial public offering on Wednesday 18 November
   at a valuation of about $1.5 trillion, ahead of a Nasdaq debut on
   Thursday under the ticker ANT. (Reports of the IPO pricing.)
4. **Rupiah at a record low.** Indonesia's rupiah fell to its weakest
   level in history on 17 November, with Bank Indonesia's JISDOR reference
   rate at a record low, ahead of the central bank's rate decision on
   18 November, when it was expected to hold its benchmark rate at 5.75%.
   (Bank Indonesia's JISDOR reference rate; Indonesian market reports.)
5. **US shoppers slow.** US data released on 17 November showed retail
   sales rose 0.2% in October, in line with forecasts, while import
   prices jumped 1.1%, more than expected, keeping inflation pressure
   hot; markets priced roughly 95% odds of a Federal Reserve rate hike in
   December. (US Census Bureau retail sales release; US Bureau of Labor
   Statistics import price release.)

## Layout

A masthead names the day in the largest type on the page. Below it, one
wide lead panel (Nvidia, with a computer-chip pictogram) sits over a 2x2
grid: a falling chart for Wall Street, a robot head for Anthropic, a coin
marked RP for the rupiah, and a shopping cart for the US consumer. Every
panel pairs one bold pictogram with a short headline and one short
subline, sized to stay legible when the page is shrunk to about 300
pixels across.
