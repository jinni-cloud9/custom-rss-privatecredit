name: Update Wrapper Feeds

on:
  workflow_dispatch:
  schedule:
    • cron: "/30  _ _ *"

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      • name: Check out repo
        uses: actions/checkout@v4

      • name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      • name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      • name: Generate wrapper feeds
        run: python generate_feeds.py

      • name: Commit and push if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add sponsor-backed-ma.xml restructuring.xml private-credit.xml
          git diff --staged --quiet || git commit -m "Update wrapper feeds"
          git push
