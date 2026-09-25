import pandas as pd
df = pd.read_csv('data/processed/multilocation_adaptive_weights_test.csv')
for day in [1, 2, 3]:
    sub = df[(df['location_id']=='kolkata') & (df['lead_hours'] > 24*(day-1)) & (df['lead_hours'] <= 24*day)]
    print(f"Day {day}: count={len(sub)}, min_lh={sub['lead_hours'].min()}, max_lh={sub['lead_hours'].max()}, min_vt={sub['valid_time'].min()}, max_vt={sub['valid_time'].max()}")
