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
    "let's say it's {}.",
    "woody's got {}",
    "according to pythagoras, {} sucks.",
    "{} is meh.",
    "definitely not {}.",
    "let's not go with {}."
]

async def say(context):
    await context["message"].delete()
    return context["match"]["repeat"]

async def pick(context):
    choices = context["match"].group("choices")

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

def die(match):
    sides = int(match["sides"])

    if sides > 10000:
        raise ValueError("sorry, but that's a very **thicc** die")

    dice = int(match["dice"] or 1)

    if dice > 100:
        raise ValueError("are you sure you need this many dice?")

    return [random.randint(1, sides) for counter in range(dice)]

def evaluate(expression):
    if len(expression) > 50:
        raise ValueError("I am **NOT** a calculator")

    tokens = {
        r"(?P<dice>\d*)d(?P<sides>\d+)": die,
        r"-?\d+": lambda match: int(match[0])
    }

    result = 0
    operands = []

    remaining = expression

    while remaining:
        for token, handler in tokens.items():
            match = re.search(r'^\s*' + token, remaining)

            if match:
                values = handler(match)

                if isinstance(values, list):
                    for value in values:
                        result += value
                        operands.append(value)
                else:
                    result += values
                    operands.append(values)

                remaining = remaining[match.end():]

                break
        else:
            raise ValueError("something's wrong with syntax, but what?")

    return result, operands

async def roll(context):
    try:
        result, operands = evaluate(context["match"]["expression"])
    except ValueError as ex:
        return f"hmm, doesn't compute. {str(ex)}"

    if len(operands) <= 1:
        return f"= {result}"

    log = ""

    for operand in operands:
        if log:
            log += " + " if operand >= 0 else " - "
            log += str(abs(operand))
        else:
            log += str(operand)

    return f"__{result}__ = {log}"

respond_to = {
    fr"^{pick_words}[^.?!]*:\s*(?P<choices>.*)$": pick,
    r"^say:\s*(?P<repeat>.+)": say,
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

    async def vgs(context):
        responses = []

        for shortcut in re.findall(context["match"].re, context["match"].string):
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

    async def respond(self, message):
        for pattern, response in respond_to.items():
            match = re.match(pattern, message.content, re.IGNORECASE)

            if match:
                if callable(response):
                    return await response({
                        "message": message,
                        "match": match
                    })
                else:
                    return response

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        try:
            response = await self.respond(message)
        except Exception as ex:
            response = f"something went wrong: `{ex}`."

        if response is not None:
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
