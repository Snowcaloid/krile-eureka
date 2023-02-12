# Snowcaloid Discord bot

Created usign Python.

## Requirements

PostgreSQL DB "Snowcaloid"

postgres=# CREATE DATABASE Snowcaloid;

postgres=# CREATE USER snowcaloid with encrypted password \<password\>;

postgres=# grant all privileges on database Snowcaloid to snowcaloid;

postgres=# grant all on schema public to Snowcaloid;

## Troubleshooting

### Updating the discord API

<https://discordpy.readthedocs.io/en/stable/intro.html>

Windows: py -3 -m pip install -U discord.py

Linux: python3 -m pip install discord.py

Create the environment:

python -m venv bot-env

Activate the environment:

Windows .\bot-env\Scripts\activate

Linux: source bot-env/bin/activate
