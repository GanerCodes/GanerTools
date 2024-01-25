import random, string, shutil, os, re
from subprocess import Popen
from hashlib import sha256

qsha = lambda data: sha256(data.encode()).hexdigest()
collapseList = lambda l, n = None: (collapseList(l, j := []) and j) if n is None else ([collapseList(i, n) for i in l] if isinstance(l, list) else n.append(l))
random_string = lambda n: ''.join(random.choice(string.ascii_letters) for i in range(n))

def downloadYoutube(link, noPlaylist=False, audioOnly=False, folder="", cookies="cookies.txt"):
    return (folder, Popen(collapseList(["yt-dlp",
        ['-x', "--audio-format", "mp3"] if audioOnly else ["--merge-output-format", "mp4"],
        ["--no-playlist"] if noPlaylist else [], "--cookies", cookies,
        "--no-progress", "--embed-thumbnail", "--no-post-overwrites", "-ciw",
        "--restrict-filenames", "-o", f"{folder}/%(playlist_index)s_%(id)s.%(ext)s", link])))

def downloadGallery(link, folder="", cookies="cookies.txt"):
    return (folder, Popen(["gallery-dl",
        "--config", "gallery_dl.json", "--cookies", cookies, "-o", f"base-directory={folder}", link]))

def downloadWget(link, folder="", cookies="cookies.txt"):
    return (folder, Popen(["wget",
        "--load-cookies", cookies, "-c", "-nd", "-nv", "-P", f"{folder}", link]))

def downloadSpeedaudio(link, arg, folder): # all sorts of hacky
    speed_para = m.group(1) if (m := re.match(r'^([\d.]+)x$', arg)) else 1.25
    ID = random_string(12)
    temp_file, dest_file = f"/tmp/{ID}", os.path.join(folder, f"{ID}_speedup.mp3")
    
    Popen(["wget", "-O", temp_file, link]).wait()
    os.makedirs(folder, exist_ok=True)
    return (folder, Popen(["ffmpeg",
        "-i", temp_file, "-af", f"atempo={speed_para}", dest_file]))

def download(link, args="", baseDir="/tmp/download/", cookies="cookies.txt", move_folder=None):
    args = list(filter(None, args.lower().split(' ')))
    baseFold = f"{baseDir}{(hsh := qsha(link)[:24])}"
    
    print(f'''Downloading "{link}" with args "{', '.join(args)}" to location "{baseFold}"''')
    procs = []
    if len(args) == 0:
        print("No downloader options provided, trying video and wget")
        args = "video wget"
    
    if "video" in args:
        print("Downloading as: video")
        try: procs.append(("video", downloadYoutube(link, audioOnly=0, noPlaylist=("noplaylist" in args), folder=f"{baseFold}/video", cookies=cookies)))
        except Exception as e: print(f"Download Exception: {e}")
    if "audio" in args:
        print("Downloading as: audio")
        try: procs.append(("audio", downloadYoutube(link, audioOnly=1, noPlaylist=("noplaylist" in args), folder=f"{baseFold}/audio", cookies=cookies)))
        except Exception as e: print(f"Download Exception: {e}")
    if "gallery" in args or "image" in args:
        print("Downloading as: gallery")
        try: procs.append(("gallery", downloadGallery(link, folder=f"{baseFold}/gallery", cookies=cookies)))
        except Exception as e: print(f"Download Exception: {e}")
    if "wget" in args or "file" in args:
        print("Downloading as: wget")
        try: procs.append(("wget", downloadWget(link, folder=f"{baseFold}/wget", cookies=cookies)))
        except Exception as e: print(f"Download Exception: {e}")
    for arg in args:
        if arg.startswith("speedaudio"):
            print("Downloading as: speedaudio")
            try: procs.append(("speedaudio", downloadSpeedaudio(link, arg, f"{baseFold}/speedaudio")))
            except Exception as e: print(f"Download Exception: {e}")
            break
    
    final = []
    for proc in procs:
        dtype, (expectedDir, pr) = proc
        pr.wait()
        
        cond1 = cond2 = False
        if (cond1 := os.path.exists(expectedDir)) and (cond2 := len(dr := os.listdir(expectedDir))):
            located_filepath = f"{expectedDir}/{dr[0]}" if len(dr) == 1 else expectedDir
            if move_folder:
                if not os.path.isdir(move_folder):
                    os.mkdir(move_folder)
                
                located_dir, located_filename = os.path.split(located_filepath)
                new_filepath = f"{move_folder}/{located_filename}"
                if os.path.isfile(new_filepath) or os.path.isdir(new_filepath):
                    old_filepath = new_filepath
                    new_filepath = f"{move_folder}/{random_string(12)}_{located_filename}"
                    print(f'Using name "{new_filepath}" as "{old_filepath}" already exists')
                
                shutil.move(located_filepath, new_filepath)
                located_filepath = new_filepath
            final.append((dtype, pr.returncode, located_filepath))
        else:
            print(f"""Failed to download as {dtype} ({pr.returncode}) (expectedDir={expectedDir}): {"No files found in directory" if cond2 else ("Created directroy, but no files found" if cond1 else "No directory created")}""")
    
    return final

if __name__ == "__main__":
    from sys import argv
    r = None
    if len(argv) < 2:
        r = download("https://www.youtube.com/watch?v=Rmea5ET_n9g")
    elif len(argv) == 2:
        r = download(argv[1])
    else:
        r = download(argv[1], ' '.join(argv[2:]))
    print(f"Result: {r}")