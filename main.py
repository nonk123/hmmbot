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

pick_words = "(choose|pick|select)"
pick_choices_pattern = f"(?:{pick_words}.*[:,] ?| )"
pick_phrases = [
    "i think i'll go with... {}.",
    "hmm... {}, yes.",
    "{} is the most meh option out of these; repick.",
    "definitely not {}.",
    "repick.",
    "meh.",
    "hmm?"
]

def pick(content):
    choices = re.split(pick_choices_pattern, content, 2)[-1]

    if not choices:
        return "and what should i pick?"

    if "|" in choices:
        choices = re.split(r" *\| *", choices)
    elif '"' in choices:
        choices = [s[1:-1] for s in re.findall(r'".*?"', choices)]
    else:
        choices = re.split(" +", choices)

    choice = "`%s`" % random.choice(choices)
    return random.choice(pick_phrases).format(choice)

modals = "((do|did|can|could|have|has|had|should)(n't)?|shall)"
pronouns = "(I|you|he|she|it|we|they)"

respond_to = {
    fr"(^|.+,? +){pick_words}.*{pick_choices_pattern}": pick,
    fr"{modals} +{pronouns}|you +{modals}": ynm,
    r"^test$": "test?",
    r"^ping$": "pong!",
    r"^pong$": "ping?",
    r"^well([.?]*$|hr?m+$)": "well?",
    word("hr?m+"): "hmm?",
    word("me+h"): "meh.",
    word("he+m"): "hem.",
    r"^[ -/:-@\[-`{-~]+$": "?",
    fr"{word('brb')}|{word('gtg')}|^afk(, *| +)eating|^back(\b|$)": "ok.",
    r"^ready|ready$": "no, you're not.",
    word("(fuck|fric[ck]) +you"): "no u",
    r"^\*\*.+\*\*$": "hmm?"
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
                if callable(response):
                    yield response(content)
                    return
                else:
                    yield response

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
