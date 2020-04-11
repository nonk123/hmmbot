#!/usr/bin/python3

import discord

import os.path
import json

class HmmBot(discord.Client):
    async def on_ready(self):
        print("Ready, I guess?")

def main():
    file = "config.json"

    if os.path.exists(file):
        with open(file, "r") as config:
            HmmBot().run(json.load(config)["token"])
    else:
        raise Exception("Config file doesn't exist: %s" % file)

if __name__ == "__main__":
    main()
