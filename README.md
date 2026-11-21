# THE WORLD TODAY — Saturday 21 November 2026

A newspaper front page summing up the world's news of Saturday
21 November 2026, drawn entirely in code by `main.py` (Python 3,
standard library only, no network at runtime).

## The front page

Masthead **THE WORLD TODAY — SATURDAY 21 NOVEMBER 2026**, then six
stories, each with a headline, a short standfirst and a small picture
drawn in code:

1. **TOP STORY — AI SELL-OFF DEEPENS.** Anthropic shares fall more
   than 9% the day after its record IPO; the Nasdaq fell 5.28% on
   Friday and Nvidia dropped about 14%. Picture: a falling market
   chart. Source: NDTV, 21 Nov 2026.
2. **GAMING — GTA VI BANKS $3.79 BILLION ON DAY ONE.** Record
   first-day retail sales for the game. Picture: a city skyline at
   sunset. Source: NDTV, 21 Nov 2026.
3. **NEW YORK — MAMDANI TO CLOSE RIKERS ISLAND BY 2032.** The
   mayor-elect announces a plan to shut the jail. Picture: a barred
   jail building by the water. Source: BBC, 21 Nov 2026.
4. **COURTS — JUDGE APPROVES BAYER $7.25BN ROUNDUP DEAL.** A US
   judge signs off on the cancer settlement. Picture: a gavel.
   Source: Deutsche Welle, 21 Nov 2026.
5. **JUSTICE — 19 YEARS FOR US ASSASSINATION PLOT.** An Indian man
   is jailed over a plot to kill a Sikh separatist leader in the US.
   Picture: a courthouse. Source: BBC, 21 Nov 2026.
6. **TRADE — TRUMP CLOSE TO MEXICO TRADE DEAL.** The president says
   more work to do with Canada. Picture: the US and Mexican flags.
   Source: reporting of 21 Nov 2026.

Every number is as reported; nothing is hyped or speculated.

## How it works

`main.py` keeps a 1024×1024 RGB canvas in a byte array and draws on
it with its own primitives (rectangles, lines, circles, triangles),
its own hand-made 5×7 bitmap font, and six small scene-drawing
functions. It then writes the canvas out with its own PNG writer
(signature, IHDR, zlib-compressed IDAT, IEND, CRC32 checksums).
There is no randomness, no clock, no network and no file input, so
the output is byte-identical on every run.

## Run and verify

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024×1024, under 1 MiB). Run it twice
into two different directories and compare:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/run1 python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/run2 python3 main.py
sha256sum /tmp/run1/entry.png /tmp/run2/entry.png
```

The two hashes must match. The default output directory is `/output`
when `MAKEFUN_OUTPUT_DIR` is not set, as the competition requires.

## Files

- `main.py` — the program (entrypoint).
- `LICENSE` — MIT.
- `.makefun/owner.json` — wallet claim file.
