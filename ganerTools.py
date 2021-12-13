from downany import download
import asyncio, requests, aiohttp, json, discord, random, os, re, io, threading
from better_desmos_python import eqToPy

url_regex = re.compile(
    r"([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#\.]?[\w-]+)*\/?",
    re.MULTILINE
) # https://stackoverflow.com/a/63022807/14501641

get_urls = lambda s: list(map(lambda x: x.group(), url_regex.finditer(s)))

config = json.load(open('config.json', 'r'))
save_path     = config['save_path']
valid_users   = config['downloader_valid_users']
discord_token = config['discord_token']
access_token  = config['access_token']
cookies_path  = config['cookies']

if save_path[-1] != '/': save_path = save_path + '/'
bot = discord.Client()
rdy, msgque = False, []

splitDelims = lambda x, s: list(filter(None, x.split(s[0]))) if len(s) == 1 else splitDelims(s[-1].join(x.split(s[0])), s[1:])

def convertPathToURL(path):
    return requests.post("https://ganer.xyz/shortenURL", headers = {
        "localpath": "true",
        "access": access_token,
        "url": f"/e/download/{path.removeprefix(save_path)}"
    }).content.decode()

def downloadProc(msg, link, args):
    j = download(link, args, baseDir = save_path, cookies = cookies_path)
    sep = '\n\t'
    msgque.append((msg, f"""\
Downloaded "`{link[:24] + ('…' if len(link) > 23 else '')}`:"
\t{sep.join(f"{i[0]}: {convertPathToURL(i[2])}" for i in j)}"""))

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
                c = spl[1] if len(spl) == 2 else "video gallery"
                rMsg = f"Downloading with parameters `{c}`:"
                counter = 0
                # HERE
                for link in get_urls(spl[0]):
                    link = link.strip()
                    counter += 1
                    rMsg += f'''\n{counter}. `{link}`'''
                    threading.Thread(target = downloadProc, args = (msg, link, c)).start()
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