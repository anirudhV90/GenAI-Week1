# Week 1 Project — Tech Layoffs Tracker

**Mastering Agentic AI Bootcamp | The Gen Academy | Week 1: Gen AI Building Blocks**

## Project Overview

For Week 1, I built a **Tech Layoffs Tracker** — an interactive Streamlit dashboard that
analyzes and visualizes tech industry layoffs from 2020 to present. This was a **Path B**
project (own idea, own dataset) rather than replicating the stock portfolio analyzer shown
in the live session, chosen to practice the vibe-coding workflow on a problem I hadn't seen
solved before.

The app lets a user explore layoff events by date range, industry, country, and company
funding stage, and surfaces trends across three views: an Overview (top industries/countries,
funding-stage breakdown), Trends (monthly time series, industry trend lines), and a Company
Drilldown (treemap + searchable table).

**Stack:** Streamlit + pandas + Plotly, Python 3, run in a local venv.

**AI coding assistant used:** Claude Code (Anthropic), used conversationally to scaffold,
build, debug, and iterate on the app end-to-end.

## Dataset

- **Source:** Kaggle — [`swaptr/layoffs-2022`](https://www.kaggle.com/datasets/swaptr/layoffs-2022)
  (mirrors layoffs.fyi; despite the dataset's name it is continuously updated)
- **Size:** 4,563 layoff events
- **Columns:** `company, location, total_laid_off, date, percentage_laid_off, industry,
  source, stage, funds_raised, country, date_added`
- **Coverage:** March 2020 – August 2026, 30 industries, 66 countries, 16 funding stages
- Downloaded programmatically via the Kaggle API (`kaggle datasets download`) after
  configuring API credentials locally.

## Prompts Used During Vibe Coding

Rather than prompting a separate tool like Codex, I worked directly with Claude Code as my
AI pair programmer for the entire build. Below is the actual sequence of prompts/requests
used, condensed:

1. *"Read the [Week 1 project handout] PDF and tell me what you understood."*
   → Assistant summarized the assignment requirements (Path A/B, deliverables, deadline).

2. *"Create a week1 project folder... I'm thinking stock portfolio analyzer or something
   else — give me ideas."*
   → Assistant proposed several Path B dataset ideas (Spotify trends, layoffs tracker, video
   game sales, CO2 emissions, Netflix catalog).

3. *"How will vibe coding be involved in the layoffs tracker?"*
   → Assistant explained the prompt-chain approach (scaffold → core viz → interactivity →
   deeper analysis → polish) before any code was written.

4. *"Let's go for a code-heavy track. Build the layoffs analyzer. Let me know what you need
   from me."*
   → Assistant set up the venv, requirements, and asked for the dataset.

5. *"I've added Kaggle's access key... use that to download the data."* / *"try using
   anirudhv"* (Kaggle username)
   → Assistant built a proper `kaggle.json` from the raw key + username and downloaded the
   dataset via the Kaggle CLI.

6. Assistant built the initial `app.py`: KPI row, sidebar filters (date/industry/country/
   stage), and three tabs (Overview / Trends / Company Drilldown), then smoke-tested it
   with Streamlit's `AppTest` framework and a live run before handing it back.

7. *"Till when is the Kaggle data source? ... if I select a date range and industry, it
   shows 'No data matches.'"*
   → Bug report and a question about data recency, prompting a debugging round (see below).

8. *"Still doesn't seem fixed"* → *[screenshot of the actual issue]*
   → Iterative debugging using Streamlit's `AppTest` harness and live browser automation to
   reproduce the exact click sequence.

9. *"This seems good for now — write the doc, push to git, help me record the demo."*
   → This document, the GitHub push, and a demo script/recording plan.

## Iterations & Debugging

This project had two real bugs worth documenting, since finding and understanding them was
as much a part of "vibe coding" as writing the first version:

- **Reversed date-range clicks.** Streamlit's `date_input` range picker can return the two
  picked dates in *click order* rather than sorted order — clicking the later date first,
  then the earlier date, silently reset the range instead of extending it. Since the filter
  logic assumed `start <= end`, this produced `date >= start & date <= end` matching nothing.
  **Fix:** sort the tuple (`start, end = sorted(date_range)`) before filtering. Verified via
  Streamlit's `AppTest` framework by simulating both click orders, then confirmed live in a
  real browser session.

- **False alarm: dataset "only goes to 2022."** I initially assumed the "layoffs-2022"
  dataset name meant stale data and that the date-range picker's 2026 upper bound was a bug.
  Checking the raw CSV showed the dataset is actively updated (rows through August 2026,
  matching layoffs.fyi), so the wide date range was correct behavior, not a defect —
  a reminder to verify assumptions against the actual data before "fixing" something.

- **Not a bug: "Select all" landing on the wrong option.** A later "No data" report turned
  out to be a UI mis-click — the Industry filter's "Select all" click landed on the first
  option ("AI") instead, and the AI industry category has zero events before July 2023. This
  was confirmed by directly querying the dataset and by reproducing the exact click sequence
  in a live browser. Verifying against ground truth kept me from "fixing" behavior that was
  already correct.

- **Hot-reload gotcha.** An edit to `app.py` wasn't reflected in the running app because the
  `watchdog` package (which Streamlit uses for reliable file-change detection) wasn't
  installed — the server had to be restarted manually to pick up the fix. Installed
  `watchdog` afterward so future edits hot-reload automatically.

## Learnings / Observations

- Treating an AI coding assistant as a collaborator works best when you **push back with
  concrete evidence** (a screenshot, a specific date range) rather than just "it's still
  broken" — that's what turned a vague bug report into a reproducible, fixable issue.
- Automated verification (Streamlit's `AppTest`, browser automation) caught that my first
  "fix" for the date-order bug was correct in isolation, which helped separate "the code is
  right but the server is stale" from "the code is still wrong" — two very different
  problems that look identical from the UI.
- Not every "No data" report is a bug — checking the underlying data first (e.g., does the
  AI industry even have events in 2020?) avoided chasing a fix for correct behavior.
- Kaggle datasets named after a specific year aren't necessarily frozen in time — worth
  checking actual row dates rather than trusting the dataset title.

## Repository

Code is available at: https://github.com/anirudhV90/GenAI-Week1
