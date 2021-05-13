#Python 3.10
import string, math, re

def findall(s, p):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

def findClosing(s : str, f : int, l : str):
    count = 1
    for i, v in enumerate(s[f + 1:]):
        if v == l: count -= 1
        if count == 0: return i + f + 2
        if v == s[f]: count += 1
    raise Exception("kys", s[f], s, f, l)

def getInclosed(s, f, l):
    return s[f:findClosing(s, f, l)]

def getInclosedNoParam(s, f, l):
    return s[f + 1:findClosing(s, f, l) - 1]

def eqToPy(s):
    s = s.replace(r'\ ', '')
    s = s.replace(r'\left|', r'\abs(').replace(r'\right|', ')')
    s = s.replace(r'\left', '').replace(r'\right', '')
    s = s.replace(r'\le', '<=').replace(r'\ge', '>=')
    s = s.replace(r'\pi', 'π')
    s = s.replace(r'\operatorname{mod}', r'\math.fmod')
    s = s.replace(r'\operatorname{abs}', r'\abs')

    letters = string.ascii_lowercase + string.ascii_uppercase + 'π'
    numbers = string.digits

    functionPrefix = ''
    if (match := re.search(r"^[a-zA-Z0-9,({}_]{1,}\([a-zA-Z0-9,({}_]{1,}\)\=", s)):
        varName = (inner := match.group(0).split('=')[0].split('('))[0]
        inner = inner[1].strip('()').replace(',', ', ')
        s = s[match.span()[1]:]
        functionPrefix = f"{varName} = lambda {inner}: ".replace('{', '').replace('}', '')

    sl = list(s)
    for e in reversed([o for s in list(re.finditer(r"[0-9]{1,}", s)) for o in s.span()]):
        sl[e:e] = ['!']
    s = ''.join(sl)

    f, wait = "", False
    for i, v in enumerate(s):
        if v in "\\_!": wait = v

        if wait:
            if v != '!': f += v
            if wait == '!':
                if v == '!':
                    if i < len(s) - 1 and s[i + 1] in letters + '\\':
                        f += '*'
                    wait = False
            elif wait == '_':
                if v == '}':
                    wait = False
                    if s[i + 1] in letters + numbers:
                        f += '*'
            elif wait == '\\':
                if v in '{(]':
                    wait = False 
        else:
            if v in letters and i < len(s) - 1 and s[i + 1] in (letters + r'\{(!'):
                f += v + '*'
            else:
                f += v
    s = f

    for delim in [(r"\frac", '}}', "frac"), (r"\log_", '})', "log"), (r"\sqrt", ']}', "sqrt"), (r"\tan^", '})', "atan"), (r"\sin^", '})', "asin"), (r"\cos^", '})', "acos")]:
        while delim[0] in s:
            startLoc = s.index(delim[0])

            paraStart1 = startLoc + len(delim[0])
            if delim[2] == 'sqrt' and s[paraStart1] == '{':
                s = s.replace(r'\sqrt', 'math.sqrt', 1)
                continue
            endIndex1 = findClosing(s, paraStart1, delim[1][0])
            trim1 = s[paraStart1 + 1:endIndex1 - 1]

            paraStart2 = endIndex1
            endIndex2 = findClosing(s, paraStart2, delim[1][1])
            trim2 = s[paraStart2 + 1:endIndex2 - 1]

            match delim[2]:
                case 'frac':
                    s = s[:startLoc] + f"({trim1})/({trim2})" + s[endIndex2:]
                case 'log':
                    s = s[:startLoc] + f"math.log({trim2},{trim1})" + s[endIndex2:]
                case 'sqrt':
                    s = s[:startLoc] + f"pow({trim2},1/({trim1}))" + s[endIndex2:]
                case 'atan' | 'asin' | 'acos':
                    s = s[:startLoc] + f"math.{delim[2]}({trim2})" + s[endIndex2:]

    while '_{' in s:
        locS = s.find('_{')
        locE = s.find('}', locS)
        s = s[:locS - 1] + f'({s[locS-1]}_' + s[locS + 2:locE] + ')' + s[locE + 1:]

    s = s.replace('^{', '**(').replace('}', ')').replace('\\', '').replace('{', '(').replace(')(', ')*(')
    f = ""
    for i, v in enumerate(s):
        f += v
        if i == len(s) - 1: break
        if v == ')' and s[i + 1] in letters + numbers + '(':
            f += '*'
    s = f
    s = s.replace('π', 'math.pi').replace('cos(', 'math.cos(').replace('sin(', 'math.sin(')
    s = s.replace(']', '-1]')
    s = s.replace('.x', '[0]').replace('.y', '[1]')
    
    s = functionPrefix + s
    return s

if __name__ == "__main__":
    s = r"s\left(a,b,k\right)=\min\left(a,b\right)-\frac{1}{6}\left(\frac{\max\left(0,k-\operatorname{abs}\left(a-b\right)\right)}{k}\right)^{3}k"
    print(eqToPy(s))