#this is a mess

import asyncio, aiohttp, discord, random, os, io
from better_desmos_python import eqToPy
token = "TOKEN"

bot = discord.Client()

@bot.event
async def on_ready():
    print("READY")

@bot.event
async def on_message(msg):
    match msg.content.split(' '):
        case "ptdfm", x:
            f = msg.attachments[0]
            await f.save(name := f"{str(random.random()).replace('.', '')}.txt")
            print("Saved:", name)
            with open(name, 'r') as read:
                content = read.readlines()
            content = [line.rstrip('\n') for line in content]
            l = []
            t = ""
            p = 0
            while p < len(content):
                j = False
                if len(t) + len(content[p]) < 1985:
                    t += content[p] + '\n'
                else:
                    j = True
                if j or p == len(content) - 1:
                    l += ['```' + x + '\n' + t + '```']
                    t = ""
                p += 1
            for i in l:
                await msg.channel.send(i)
            os.remove(name)
        case "desmos", *x:
            x = ' '.join(x).strip('`')
            await msg.channel.send(f"```py\n{eqToPy(x)}```")
        case "tex", *x:
            dat = {
                "formula": ' '.join(x).strip('`'),
                "fsize": "25px",
                "fcolor": "FFFFFF",
                "bcolor": "000000",
                "mode": "0",
                "out": "1",
                "remhost": "quicklatex.com",
                "preamble": r"""\usepackage{amsmath}
                \usepackage{amsfonts}
                \usepackage{amssymb}""",
                "rnd": str(random.random())
            }
            async with aiohttp.ClientSession() as session:
                async with session.get("https://quicklatex.com/latex3.f", data = dat) as resp:
                    resp = await resp.text()
                    resp = resp.split('\n')[1].split(' ')[0]
                    print(resp)
                    async with session.get(resp) as resp2:
                        f = await resp2.read()
                        f = io.BytesIO(f)
                        await msg.channel.send("fasdf", file = discord.File(f, filename = "image.png"))

bot.run(token)