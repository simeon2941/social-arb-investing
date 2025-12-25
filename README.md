# The Alpha Protocol

A zero-cost Social Arbitrage / Observational Investing architecture.

## Overview

This system identifies market "blind spots" by detecting viral trends in social data (TikTok, Reddit, Twitter) before they are priced in by institutional investors. It uses GitHub Actions for orchestration, Git for storage, and open-source intelligence (OSINT) tools.

## Structure

- `src/scrapers`: Data collection modules (TikTok, Reddit, Trends, News).
- `src/analysis`: Core logic for Entity Resolution and Sentiment Analysis.
- `src/ui`: Terminal User Interface (TUI) for local monitoring.
- `data/`: JSON/CSV storage (the "Ledger").
- `.github/workflows`: Automation rules.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    # OR if using PDM/Poetry
    pdm install
    ```

2.  Run the engine locally:
    ```bash
    python src/main_engine.py
    ```

3.  Launch the Terminal Interface:
    ```bash
    python src/ui/tui.py
    ```

## Disclaimer
This software is for educational purposes only. Do not invest money you cannot afford to lose.
