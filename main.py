#!/usr/bin/python3

import discord

import os.path
import json
import re

import random

import logging
logging.basicConfig(level=logging.INFO)

def word(w):
    return "(?:^|{1}){0}(?={1}|$)".format(w, "[,.?!:; ]+")

def ynm(content):
    return random.choice(["yes.", "no.", "maybe."])

modals = "((do|did|have|has|had|should)(n't)?|shall)"
pronouns = "(I|you|he|she|it|we|they)"

respond_to = {
    r"^test$": "test?",
    r"^ping$": "pong!",
    r"^pong$": "ping?",
    r"^well([.?]*$|hr?m+$)": "well?",
    word("hr?m+"): "hmm?",
    word("me+h"): "meh.",
    word("he+m"): "hem.",
    r"^[ -/:-@\[-`{-~]+$": "?",
    fr"{word('brb')}|{word('gtg')}|^afk(, *| +)eating|{word('back')}": "ok.",
    r"^ready|ready$": "no, you're not.",
    r"^\*\*.+\*\*$": "hmm?",
    fr"{modals} +{pronouns}": ynm
}

def parse_vgs():
    from pyquery import PyQuery

    vgs = {}

    pq = PyQuery(url="http://wiki.theexiled.pwnageservers.com/Tribes:_Ascend/Voice_Game_System")

    for line in pq("{0}:not(:parent), {0} > dl > dd".format("h2 + dl > dd")).items():
        split = line.text().split("] ", 2)

        shortcut = split[0][1:]
        command = split[1].rstrip()

        vgs[word(shortcut)] = command

    return vgs

respond_to.update(parse_vgs())

class HmmBot(discord.Client):
    async def on_ready(self):
        respond_to[fr"<@!?{self.user.id}>"] = "yes?"
        respond_to[fr"<@!?(\d+(?<!{self.user.id}))>"] = "hmm?"

        print("Ready, I guess?")

    def respond(self, content):
        for response_regexp, response in respond_to.items():
            for match in re.findall(response_regexp, content, re.IGNORECASE):
                yield response(content) if callable(response) else response

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        responses = list(self.respond(message.content))

        if responses:
            await message.channel.send(" ".join(responses))

def main():
    file = "config.json"

    if os.path.exists(file):
        with open(file, "r") as config:
            HmmBot().run(json.load(config)["token"])
    else:
        raise Exception("Config file doesn't exist: %s" % file)

if __name__ == "__main__":
    main()
