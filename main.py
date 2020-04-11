#!/usr/bin/python3

import discord

import os.path
import json
import re

import logging
logging.basicConfig(level=logging.INFO)

respond_to = {
    r"^test": "test?",
    r"^ping": "pong!",
    r"^pong": "ping?",
    r"^hr?m+([^m]|$)": "hmm?",
    r"^meh": "meh",
    r"^hem": "hem",
    r"^[,.?!:;\^$\[\](){}\-+=_%#@*/\\]+$": "?",
    r"^brb|^gtg|^afk,? +eating": "meh",
    r"^back": "meh",
    r"^ready|ready$": "no, you're not",
    r"^well": "well?"
}

def parse_vgs():
    from pyquery import PyQuery

    vgs = {}

    pq = PyQuery(url="https://tribes.fandom.com/wiki/Voice_Game_System")

    for row in pq("h2 + table.wikitable > tr"):
        shortcut = PyQuery(row).find("td").eq(0).text()
        command = PyQuery(row).find("td").eq(1).text()
        vgs["^%s$" % shortcut] = command

    return vgs

respond_to.update(parse_vgs())

class HmmBot(discord.Client):
    async def on_ready(self):
        print("Ready, I guess?")

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        for response_regexp, response in respond_to.items():
            if re.search(response_regexp, message.content, re.IGNORECASE):
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
