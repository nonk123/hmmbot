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
    r"^me+h": "meh",
    r"^he+m": "hem",
    r"^[,.?!:;\^$\[\](){}\-+=_%#@*/\\]+$": "?",
    r"^brb|^gtg|^afk,? +eating": "meh",
    r"^back": "meh",
    r"^ready|ready$": "no, you're not",
    r"^well": "well?"
}

def parse_vgs():
    from pyquery import PyQuery

    vgs = {}

    pq = PyQuery(url="http://wiki.theexiled.pwnageservers.com/Tribes:_Ascend/Voice_Game_System")

    for line in pq("h2 + dl > dd:not(:parent), h2 + dl > dd > dl > dd").items():
        split = line.text().split("] ", 2)

        shortcut = split[0][1:]
        command = split[1].rstrip()

        vgs["^%s$" % shortcut] = command

    return vgs

respond_to.update(parse_vgs())

class HmmBot(discord.Client):
    async def on_ready(self):
        print("Ready, I guess?")

    def split(self, content):
        patterns = [r" *\| *", r" *(?:[.!?/\\\-]+|[@:;]) *"]

        for pattern in patterns:
            if re.search(pattern, content):
                return re.split(pattern, content)

        return [x.strip('"') for x in re.findall(r'".*?"', content)] or [content]

    def respond(self, content):
        for response_regexp, response in respond_to.items():
            if re.search(response_regexp, content, re.IGNORECASE):
                return response

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        responses = map(self.respond, self.split(message.content))
        response = " ".join(s for s in responses if s)

        if response:
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
