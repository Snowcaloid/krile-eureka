# Snowcaloid Discord bot

Created using Python.

## Requirements

### A PostgreSQL database.

After setting up a PostgreSQL server on your platform of choice,
connect and run the following commands:

```postgresql
CREATE DATABASE snowcaloid;
CREATE USER snowcaloid WITH ENCRYPTED PASSWORD 'your-password-here';
GRANT ALL PRIVILEGES ON DATABASE snowcaloid TO snowcaloid;
GRANT ALL ON SCHEMA public TO snowcaloid;
```

You can use any username or database name as long as your
choices here match the environment file.

## Troubleshooting

### Updating the discord API

Information for installing discord.py can be found at <https://discordpy.readthedocs.io/en/stable/intro.html>

Windows: `py -3 -m pip install -U discord.py`

Linux: `python3 -m pip install discord.py`

Create the environment:

`python -m venv bot-env`

Activate the environment:

Windows `.\bot-env\Scripts\activate`

Linux: `source bot-env/bin/activate`

## Disclaimer

This bot has been created with the intent of simplifying tasks of certain discord servers. The use and forks of this project are allowed by third parties, but the original owner holds no responsibility for misuse of the bot's capabilities by third parties. 
