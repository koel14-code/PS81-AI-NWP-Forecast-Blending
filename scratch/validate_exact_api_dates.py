import urllib.request
import json

print("=== EXACT API VALIDATION RESULTS ===")
for d in [1, 2, 3]:
    url = f"http://localhost:8000/api/forecast?location=kolkata&lead_day={d}"
    res = json.loads(urllib.request.urlopen(url).read().decode())['data']
    print(f"\nEndpoint: /api/forecast?location=kolkata&lead_day={d}")
    print(f"  * forecast_run_time : {res.get('forecast_run_time')}")
    print(f"  * target_date       : {res.get('target_date')}")
    print(f"  * first valid_time  : {res['series'][0].get('valid_time')}")
    print(f"  * last valid_time   : {res['series'][-1].get('valid_time')}")
    print(f"  * series count      : {len(res['series'])}")
