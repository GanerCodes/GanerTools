from downany import download
from renderer import render
import asyncio, datetime, requests, aiohttp, json, discord, random, os, re, io, threading
from better_desmos_python import eqToPy
from forecast import get_forecast

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
daily_channel = config['daily_channel']

if save_path[-1] != '/': save_path = save_path + '/'
bot = discord.Client(intents=discord.Intents.all())
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

Lords_prayer = """Our Father, which art in heaven,
Hallowed be thy Name.
Thy Kingdom come.
Thy will be done in earth,
As it is in heaven.
Give us this day our daily bread.
And forgive us our trespasses,
As we forgive them that trespass against us.
And lead us not into temptation,
But deliver us from evil.
For thine is the kingdom,
The power, and the glory,
For ever and ever.
Amen."""
async def processMsgQue():
    while True:
        while len(msgque) > 0:
            try:
                m = msgque.pop()
                await m[0].channel.send(f"<@{m[0].author.id}> {m[1]}")
            except Exception as e:
                print(e)
        await asyncio.sleep(2.5)

async def set_lights(mode):
    match mode:
        case "dim":
            URLs = ("""https://brynic.ganer.xyz/call/fetch('https%3A%2F%2Fbrynic.ganer.xyz'%2C%20%7Bmethod%3A%20'POST'%2C%20mode%3A%20%22no-cors%22%2C%20body%3A%20%60%7B%22token%22%3A%22haha%22%2C%22uuid%22%3A%22all%22%2C%22mode%22%3A%7B%22modes%22%3A%5B%7B%22type%22%3A%22color%22%2C%22color%22%3A%5B0%2C0%2C10%5D%7D%5D%2C%22mask%22%3A%7B%22default%22%3A0%2C%22segments%22%3A%7B%7D%7D%2C%22shaders%22%3A%5B%5B%22brightnessDiv%22%2C%221%22%5D%5D%2C%22LED_COUNT%22%3A300%2C%22action%22%3A%22mode%22%2C%22duration%22%3A%22-1%22%2C%22isQued%22%3A%22false%22%7D%7D%60%7D)%3B""",
                    """https://brynic.ganer.xyz/call/fetch('https%3A%2F%2Fbrynic.ganer.xyz'%2C%20%7Bmethod%3A%20'POST'%2C%20mode%3A%20%22no-cors%22%2C%20body%3A%20%60%7B%22token%22%3A%22haha%22%2C%22uuid%22%3A%222d265faa%22%2C%22mode%22%3A%7B%22modes%22%3A%5B%7B%22type%22%3A%22color%22%2C%22color%22%3A%5B0%2C0%2C0%5D%7D%5D%2C%22mask%22%3A%7B%22default%22%3A0%2C%22segments%22%3A%7B%7D%7D%2C%22shaders%22%3A%5B%5B%22brightnessDiv%22%2C%221%22%5D%5D%2C%22LED_COUNT%22%3A300%2C%22action%22%3A%22mode%22%2C%22duration%22%3A%22-1%22%2C%22isQued%22%3A%22false%22%7D%7D%60%7D)%3B""")
        case "rainbow":
            URLs = ("""https://brynic.ganer.xyz/call/fetch('https%3A%2F%2Fbrynic.ganer.xyz'%2C%20%7Bmethod%3A%20'POST'%2C%20mode%3A%20%22no-cors%22%2C%20body%3A%20%60%7B%22token%22%3A%22haha%22%2C%22uuid%22%3A%22all%22%2C%22mode%22%3A%7B%22modes%22%3A%5B%7B%22type%22%3A%22rainbow%22%2C%22speed%22%3A%22213%22%2C%22segCount%22%3A%223%22%2C%22direction%22%3A0%7D%5D%2C%22mask%22%3A%7B%22default%22%3A0%2C%22segments%22%3A%7B%7D%7D%2C%22shaders%22%3A%5B%5B%22brightnessDiv%22%2C%2210%22%5D%5D%2C%22LED_COUNT%22%3A300%2C%22action%22%3A%22mode%22%2C%22duration%22%3A%22-1%22%2C%22isQued%22%3A%22false%22%7D%7D%60%7D)%3B""", )
        case _:
            print(f"Unknown light mode: {mode}")
            return
    return [requests.get(URL) for URL in URLs]
    
async def continuous_looper():
    p_t = None
    while True:
<<<<<<< HEAD
        await asyncio.sleep(30)
        
        try:
            now = datetime.datetime.now()
            t = now.hour, now.minute
            if t == p_t: continue
            p_t = t
            
            match t:
                case (6, 0):
                    forecast = get_forecast()
                    channel = bot.get_channel(daily_channel)
                    await channel.send(f"```{forecast}```\n{lords_prayer}")
                    await set_lights("rainbow")
                case (21, 45):
                    await set_lights("dim")
        except Exception as e:
            print(f"Error in continious looper: {e}")
=======
        now = datetime.datetime.now()
        if now.hour == 7 and now.minute == 15:
            forecast = get_forecast()
            channel = bot.get_channel(daily_channel)
            await channel.send(f"```{forecast}```\n{Lords_prayer}")
        await asyncio.sleep(60)
>>>>>>> refs/remotes/origin/main

@bot.event
async def on_ready():
    global rdy
    if not rdy:
        print("Ready")
        bot.loop.create_task(processMsgQue())
        bot.loop.create_task(continuous_looper())
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
            render(x, name := f"{msg.id}.png")
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
