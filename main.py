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

pick_words = r"(choose|pick|select|decide\s+on)"

pick_phrases = [
    "i think i'll go with... {}.",
    "hmm... {}, yes.",
    "{} is the most meh option out of these; repick.",
    "definitely not {}."
]

def pick(match):
    choices = match.group("choices")

    if not choices:
        return "and what should i pick? (tm)"

    if "|" in choices:
        choices = re.split(r"\s*\|\s*", choices)
    elif '"' in choices:
        choices = [s[1:-1] for s in re.findall(r'".*?"', choices)]
    elif "," in choices:
        choices = re.split(r",\s*", choices)
    else:
        choices = re.split(r"\s+", choices)

    return random.choice(pick_phrases).format(f"__{random.choice(choices)}__")

def evaluate(expression):
    tokens = {
        r"(?P<dice>\d*)d(?P<sides>\d+)": die,
        r"(?P<sign>[-+])?\s*(?P<number>\d+)": number
    }

    result = 0

    remaining = expression

    while remaining:
        found = False

        for token, handler in tokens.items():
            match = re.search(r'^\s*' + token, remaining)

            if not match:
                continue

            result += handler(match)
            remaining = remaining[match.end():]
            found = True

            break

        if not found:
            raise ValueError("something's wrong with syntax, but what?")

    return result

def number(match):
    if match["sign"] == "-":
        sign = -1
    elif match["sign"] == "+" or not match["sign"]:
        sign = 1

    return int(match["number"]) * sign

def die(match):
    sides = int(match["sides"])
    dice = int(match["dice"] or 1)

    return sum(random.randint(1, sides) for counter in range(dice))

def roll(match):
    try:
        result = evaluate(match["expression"])
    except ValueError as ex:
        return f"hmm, doesn't compute: {str(ex)}"

    return f"= {result}"

respond_to = {
    fr"^bot(,\s*|,?\s+){pick_words}[^.?!]*:\s*(?P<choices>.*)$": pick,
    r"^roll:\s*(?P<expression>.+)": roll,
    r"^test$": "test?",
    r"^well((,?\s+hr?m+)|[.?]*)$": "well?",
    r"^hr?m+\??$": "hmm?",
    r"^meh$": "meh.",
    r"^hem$": "hem.",
    r"^[\s -/:-@\[-`{-~]+$": "?",
    r"^ready$": "no, you're not.",
    r"^\*\*.+\*\*$": "hmm?"
}

vgs_lines = {}

def init_vgs():
    from pyquery import PyQuery

    pq = PyQuery(url="http://wiki.theexiled.pwnageservers.com/Tribes:_Ascend/Voice_Game_System")

    for line in pq("{0}:not(:parent), {0} > dl > dd".format("h2 + dl > dd")).items():
        split = line.text().split("] ", 2)

        shortcut = split[0][1:].strip()
        command = split[1].strip()

        vgs_lines[shortcut] = command

    def vgs(match):
        responses = []

        for shortcut in re.findall(match.re, match.string):
            shortcut = shortcut.upper()

            if shortcut in vgs_lines:
                responses.append(vgs_lines[shortcut])

        return " ".join(responses)

    pattern = "|".join(shortcut for shortcut, _ in vgs_lines.items())

    respond_to[fr"({pattern}(?:\s+|$))+"] = vgs

init_vgs()

class HmmBot(discord.Client):
    async def on_ready(self):
        respond_to[fr"<@!?{self.user.id}>"] = "yes?"

        print("Ready, I guess?")

    def respond(self, content):
        for pattern, response in respond_to.items():
            match = re.match(pattern, content, re.IGNORECASE)

            if match:
                if callable(response):
                    return response(match)
                else:
                    return response

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        try:
            response = self.respond(message.content)
        except Exception as ex:
            response = f"something's gone wrong: `{ex}`."

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
