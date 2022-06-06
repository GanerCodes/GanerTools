from downany import download
from renderer import Renderer
import asyncio, requests, aiohttp, json, discord, random, os, re, io, threading
from better_desmos_python import eqToPy

url_regex = re.compile(
    r"(http|https)\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?",
    re.MULTILINE
) # https://stackoverflow.com/a/63022807/14501641

get_urls = lambda s: list(map(lambda x: x.group(), url_regex.finditer(s)))

config = json.load(open('config.json', 'r'))
save_path     = config['save_path']
valid_users   = config['downloader_valid_users']
discord_token = config['discord_token']
access_token  = config['access_token']
cookies_path  = config['cookies'] if 'cookies' in config else ''

if save_path[-1] != '/': save_path = save_path + '/'
bot = discord.Client()
rdy, msgque = False, []

splitDelims = lambda x, s: list(filter(None, x.split(s[0]))) if len(s) == 1 else splitDelims(s[-1].join(x.split(s[0])), s[1:])

def makeSafeFilepath(filename):
    return ''.join(map(lambda c: c if c.isalpha() or c.isdigit() else '_', filename)).strip() or "ganerTools"

def convertPathToURL(path):
    return requests.post("https://ganer.xyz/shortenURL", headers = {
        "localpath": "true",
        "access": access_token,
        "url": f"/e/download/{path.removeprefix(save_path)}"
    }).content.decode()

def downloadProc(msg, link, args, move_folder = None):
    j = download(link, args, baseDir = save_path, cookies = cookies_path, move_folder = move_folder)
    sep = '\n\t'
    msgque.append((msg, f"""\
Download result "`{link[:50] + ('…' if len(link) > 49 else '')}`:"
\t{sep.join(f"{i[0]}: {convertPathToURL(i[2])}" for i in j) if len(j) else 'No download results.'}"""))

async def processMsgQue():
    while True:
        while len(msgque) > 0:
            try:
                m = msgque.pop()
                await m[0].channel.send(f"<@{m[0].author.id}> {m[1]}")
            except Exception as e:
                print(e)
        await asyncio.sleep(2.5)

@bot.event
async def on_ready():
    global rdy
    if not rdy:
        print("Ready")
        bot.loop.create_task(processMsgQue())
        rdy = True

@bot.event
async def on_message(msg):
    match msg.content.split(' '):
        case "save", *x:
            if msg.author.id not in valid_users:
                await msg.channel.send("no")
                return
            m = ' '.join(x)
            spl = m.split('|', 1)
            if len(spl) == 0:
                await msg.channel.send("Add a link dumbass")
            else:
                channelName = msg.channel.name
                folder_name = redirfoldspl[-1].strip() if len(redirfoldspl := spl[-1].split('>>')) > 1 else f"{makeSafeFilepath(channelName)}"
                redirfold = f"""{save_path}{folder_name}"""
                c = spl[1].strip() if len(spl) == 2 else "video gallery"
                rMsg = f"Downloading with parameters `{c}` into folder `{redirfold}`:"
                counter = 0
                for link in get_urls(spl[0]):
                    link = link.strip()
                    counter += 1
                    rMsg += f'''\n{counter}. {link}'''
                    threading.Thread(target = downloadProc, args = (msg, link, c), kwargs = {"move_folder": redirfold}).start()
                await msg.reply(rMsg)
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
        case "render", *x:
            x = ' '.join(x).strip().strip('`').strip()
            Renderer.exec(x, name := f"{msg.id}.png")
            await msg.channel.send("Your rendering, sire.",
                file = discord.File(name,
                    filename = f"render_{name}"))
            os.remove(name)
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
                        await msg.channel.send("** **", file = discord.File(f, filename = "image.png"))

bot.run(discord_token)
