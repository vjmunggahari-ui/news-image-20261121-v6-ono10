# Saturday 21 November 2026: 50 stories, 9 regions — GTA VI's $3.79bn day, Nasdaq's -5.3% rout, Russia's biggest attack of the year

[![bounty](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/vjmunggahari-ui/news-image-20261121-v6-ono10/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard)
[![reward](https://make.fun/badge/news-image-20261121/vjmunggahari-ui/news-image-20261121-v6-ono10/reward.svg)](https://make.fun/bounty/news-image-20261121/leaderboard)

One image that sums up the world's news of Saturday 21 November 2026:
**50 stories, 9 regions, one front page.**

## The day in one line

**THE GREAT UNWIND** — markets fell, war widened, and a video game made
$3.79 billion in a day.

- **$3.79bn** — GTA VI's first-day retail sales, the biggest entertainment launch ever.
- **-5.3%** — the Nasdaq's worst week since 2020; $4tn of market value wiped out.
- **400+** — drones in Russia's biggest assault on Ukraine this year.
- **$119.5bn** — Anthropic's IPO financing closed, then its shares slid 13.5%.

## How to read it

- **Masthead + numbers band** — the date, the hook, and the four numbers that define the day.
- **The spine** — the day's defining thread, in one sentence, across the page.
- **The grid** — all 50 stories, numbered, each with a consequence line
  ("what happens next / why it matters tomorrow") and three tags:
  region, story beat, and **half-life** (HL 6h = breaking, 12h = developing,
  24h = today's news, 3d = the week's story, 7d = slow burn).
- **Date check** — 50/50 stories dated. 44 happened on 21 Nov; 6 marked †
  happened on Friday evening and were first reported on Saturday.

## Run it

```sh
node main.ts
# writes entry.png to $MAKEFUN_OUTPUT_DIR (or ./output), then reads it back
# and verifies PNG magic, 1024x1024, ≤1 MiB, matching sha256, complete IEND.
```

`draw_frontpage.py` renders the image deterministically from `stories.json`
(layouts A/B/C; the shipped image is layout C). Two runs produce
byte-identical PNGs.

## Files

- `entry.png` — the front page (1024×1024, 232,483 bytes)
- `main.ts` — the entry program (Node 22, stdlib only)
- `stories.json` — the 50 dated stories, 9 regions, spine, lead numbers
- `draw_frontpage.py` — the deterministic renderer (3 layouts)
- `NOTES.md` — judging notes, QA measurements, skill/relay report
