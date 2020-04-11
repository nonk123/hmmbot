#!/usr/bin/python3

import discord

import os.path
import json
import re

class HmmBot(discord.Client):
    async def on_ready(self):
        print("Ready, I guess?")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        respond_to = {
            r"[Hh]m+[!?]*": "hmm?",
            r"[Mm]eh\??": "meh",
            r"[Hh]em\??": "hem",
            r"[!?]+": "?"
        }

        for response_regexp, response in respond_to.items():
            if re.match(response_regexp, message.content):
                await message.channel.send(response)

def main():
    file = "config.json"

    if os.path.exists(file):
        with open(file, "r") as config:
            HmmBot().run(json.load(config)["token"])
    else:
        raise Exception("Config file doesn't exist: %s" % file)

if __name__ == "__main__":
    main()
