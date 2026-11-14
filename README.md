# End-to-End ELT Pipeline for YouTube Data & AI Educator Analytics

A quota-aware ELT pipeline: **YouTube Data API -> Python -> Snowflake (RAW) -> dbt (STAGING -> MARTS) -> Power BI**, scheduled daily with GitHub Actions.

Python extracts and loads raw data. dbt does all cleaning and modelling inside Snowflake. Daily snapshots build a history, so growth and engagement trends can be measured. Everything runs on free tiers.

## Project layout

```
src/yt_pipeline/   config, quota guard, YouTube client, extract, load
scripts/           discover_channels.py, generate_keys.py
sql/               snowflake_setup.sql, create_raw_tables.sql
dbt_project/       models (staging, intermediate, marts), seeds, macros, tests
tests/             pytest tests (no API or Snowflake needed)
run_pipeline.py    extract + load entry point
run_dbt.py         runs dbt using your .env settings
```

## Setup

1. **Python 3.11 or 3.12.** dbt may not support the newest Python releases yet. Check with `python --version`.
2. **Create a virtual environment and install packages**
   ```
   python -m venv .venv
   # Windows PowerShell:  .venv\Scripts\Activate.ps1
   # macOS / Linux:       source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```
3. **Configure settings:** copy `.env.example` to `.env` and fill it in. Never commit `.env` or anything in `keys/`.
4. **YouTube API key:** Google Cloud Console -> new project -> enable *YouTube Data API v3* -> Credentials -> API key. Put it in `.env`.
5. **Build your channel list (costs 100 quota units per search):**
   ```
   python scripts/discover_channels.py "data analysis"
   python scripts/discover_channels.py "data engineering"
   ```
   Open `data/channels.csv` and delete any channels you do not want. Aim for 20 to 30.
6. **Test extraction with no Snowflake:**
   ```
   python run_pipeline.py --extract-only
   ```
   CSVs appear in `data/output/`.
7. **Snowflake key-pair authentication** (password sign-in is being phased out):
   ```
   python scripts/generate_keys.py
   ```
   Paste the printed public key into `sql/snowflake_setup.sql` (twice), then run that whole file in a Snowsight worksheet as the account admin.
8. **Fill the Snowflake values in `.env`** (account identifier, `YT_PIPELINE` user, key path) and load:
   ```
   python run_pipeline.py
   ```
9. **Run dbt**
   ```
   python run_dbt.py debug
   python run_dbt.py build
   python run_dbt.py source freshness
   python run_dbt.py docs generate
   python run_dbt.py docs serve
   ```
10. **Power BI:** Get Data -> Snowflake -> server `<account>.snowflakecomputing.com`, warehouse `YT_WH` -> authentication *Key Pair*, user `YT_REPORTER`, paste the private key (PEM). Import the tables from `YOUTUBE_DB.MARTS`.

## Run the tests

```
pytest
```

## Daily automation

`.github/workflows/daily_pipeline.yml` runs the pipeline and `dbt build` every day. Add these repository secrets: `YOUTUBE_API_KEY`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, and `SNOWFLAKE_PRIVATE_KEY` (the full contents of `keys/rsa_key.p8`).

## API quota

The free YouTube API tier allows 10,000 units per day by default. This pipeline uses about 61 units per run for 30 channels and 1,500 videos, and stops itself at `QUOTA_LIMIT` (default 8,000). `search.list` costs 100 units, so it is used only by `discover_channels.py`. Confirm current costs in Google's quota documentation.

## Design notes

- RAW tables are loaded as-is with `snapshot_date` and `loaded_at`. Re-running on the same day deletes and replaces that day's rows.
- Marts are rebuilt in full from the RAW history on each run, so surrogate keys on dimensions are regenerated each time.
- Shorts are labelled by duration only (`short_max_seconds` in `dbt_project.yml`, default 60). YouTube now allows Shorts up to 3 minutes, so change the variable if you want a broader definition.
- Each channel's latest 50 videos are tracked, so "videos in the last 30 days" is capped at 50.

## Troubleshooting

- `Missing environment variable`: check your `.env` file is in the project root.
- Snowflake authentication errors: confirm the public key was pasted without the BEGIN/END lines, and that your account identifier is in `orgname-accountname` form.
- `dbt: command not found`: activate the virtual environment first.

