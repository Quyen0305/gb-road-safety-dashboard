import pandas as pd
import pytest


@pytest.fixture
def joined_fixture():
    base = dict(time='09:30', longitude=-1.2, latitude=52.2, police_force=1,
                urban_or_rural_area=1, weather_conditions=1, light_conditions=1,
                road_surface_conditions=1, road_type=6, speed_limit=30,
                vehicle_type=9, age_of_casualty=30, sex_of_casualty=1, casualty_class=1)
    rows = []
    for cid, date, country, severity, vid, pid, person_severity in [
        ('A', '2024-01-01', 'E1', 2, 'V1', 'P1', 2),
        ('A', '2024-01-01', 'E1', 2, 'V1', 'P2', 3),
        ('A', '2024-01-01', 'E1', 2, 'V2', None, None),
        ('B', '2024-01-06', 'W1', 1, 'V3', 'P3', 1),
        ('C', '2024-01-07', 'S1', 3, 'V4', 'P4', 3),
    ]:
        rows.append(dict(base, collision_index=cid, date=date,
                         local_authority_ons_district=country, collision_severity=severity,
                         vehicle_key=vid, casualty_key=pid, casualty_severity=person_severity,
                         has_casualty_record=pid is not None))
    return pd.DataFrame(rows + [rows[0].copy()])
