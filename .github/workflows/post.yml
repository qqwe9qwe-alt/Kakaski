name: Post Kakashka

on:
  schedule:
    # Запуск каждый час (в 0 минут). 
    # ВАЖНО: GitHub может задерживать запуск на 10-30 минут.
    - cron: '0 * * * *' 
  workflow_dispatch: # Позволяет запускать бота вручную кнопкой "Run workflow"

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run bot
        env:
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
          CHANNEL_ID: ${{ secrets.CHANNEL_ID }}
        run: python bot.py
