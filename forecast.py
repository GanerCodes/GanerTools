import requests, datetime

def get_forecast(desc=True):
    query = r"""https://api.open-meteo.com/v1/forecast?latitude=36.0627&longitude=-94.1606&hourly=temperature_2m,precipitation,surface_pressure,cloudcover&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timeformat=unixtime&timezone=America%2FChicago&past_days=1"""
    t = requests.get(query).json()
    now = datetime.datetime.now()
    term_fixer = '' # space if emojis don't wanna mono correctly

    def conv_time(time):
        dt = datetime.datetime.fromtimestamp(time)
        r = dt.strftime("%b %d %I%p").replace(" 0", "  ")
        if all((dt.year == now.year, dt.month == now.month, dt.day == now.day, dt.hour == now.hour)):
            r = f"[{r}]"
        else:
            r = f" {r} "
        return r
    def conv_temp(temp):
        if temp > 85: return '🔥'
        if temp > 75: return '🌞'
        if temp > 64: return '😊'
        if temp > 32: return '🥶'
        return '🧊' + term_fixer
    def conv_precip(precip):
        if precip > 1.00: return '💀'
        if precip > 0.50: return '❗'
        if precip > 0.30: return '😨'
        if precip > 0.10: return '🌧️' + term_fixer
        if precip > 0.01: return '💦'
        return '😊'
    def conv_cloud(cloud):
        if cloud > 0.7: return '😔'
        if cloud > 0.4: return '😕'
        if cloud > 0.2: return '😐'
        return '😊'
    def proc_dat(data):
        return f"{data[0]}: {''.join(data[1:])}"

    ops = (conv_time, conv_temp, conv_precip, conv_cloud)

    d = t['hourly']
    data = [proc_dat(tuple(ops[i](a) for i, a in enumerate(v))) for v in list(zip(d['time'], d['temperature_2m'], d['precipitation'], d['cloudcover']))][:24*4]
    data = data[24:-12]
    k = 30
    
    if desc:
        pre = """Key:
  Temp:  🧊 32🥶64😊75🌞85🔥
  Rain:  😊.01💦.1🌧️.3😨.5❗1.💀
  Cloud: 😊.20😐.4😕.7😔\n"""
    else:
        pre = ''
    
    return pre+('\n'.join(''.join(s) for s in list(zip(*[data[i:i+k] for i in range(0, len(data), k)]))))

if __name__ == "__main__":
    print(get_forecast())
