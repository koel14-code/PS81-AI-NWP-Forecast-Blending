import urllib.request
import json

LOCATIONS = ['kolkata', 'delhi', 'mumbai', 'chennai', 'guwahati', 'bengaluru']
LEAD_DAYS = [1, 2, 3]

print("=== 1. TESTING FORECAST DATA DYNAMICS ===")
for loc in LOCATIONS:
    for day in LEAD_DAYS:
        url = f"http://localhost:8000/api/forecast?location={loc}&lead_day={day}"
        res = json.loads(urllib.request.urlopen(url).read().decode())
        series = res['data']['series']
        max_rain = max(s['blended_precipitation'] for s in series)
        print(f"Forecast {loc.upper()} Day {day}: {len(series)} points, max rain = {max_rain:.2f} mm/h")

print("\n=== 2. TESTING WEIGHTS DATA DYNAMICS ===")
for loc in LOCATIONS:
    for day in LEAD_DAYS:
        url = f"http://localhost:8000/api/weights?location={loc}&lead_day={day}"
        res = json.loads(urllib.request.urlopen(url).read().decode())
        means = res['data']['means']
        ecmwf = means.get("ECMWF_IFS", 0)
        gfs = means.get("NOAA_GFS", 0)
        icon = means.get("DWD_ICON", 0)
        print(f"Weights {loc.upper()} Day {day}: ECMWF={ecmwf:.3f}, GFS={gfs:.3f}, ICON={icon:.3f}")

print("\n=== 3. TESTING SPATIAL WEIGHTS DATA DYNAMICS ===")
for day in LEAD_DAYS:
    url = f"http://localhost:8000/api/spatial-weights?lead_day={day}"
    res = json.loads(urllib.request.urlopen(url).read().decode())
    locs = res['data']['locations']
    print(f"Spatial Day {day}: {len(locs)} cities. First city: {locs[0]['name']} dominant={locs[0]['dominant_model']}")

print("\n=== 4. TESTING EXTREME SIGNAL DATA DYNAMICS ===")
for loc in LOCATIONS:
    for day in LEAD_DAYS:
        url = f"http://localhost:8000/api/extreme-signal?location={loc}&lead_day={day}"
        res = json.loads(urllib.request.urlopen(url).read().decode())
        d = res['data']
        print(f"Extreme {loc.upper()} Day {day}: status={d['status']}, max_blended={d['max_blended']:.2f}")

print("\n=== 5. TESTING VERIFICATION & METHODOLOGY DATA ===")
verif = json.loads(urllib.request.urlopen("http://localhost:8000/api/verification").read().decode())
print(f"Verification table rows: {len(verif['data']['table'])}")

meth = json.loads(urllib.request.urlopen("http://localhost:8000/api/methodology").read().decode())
print(f"Methodology steps: {len(meth['data']['pipeline_stages'])}")
