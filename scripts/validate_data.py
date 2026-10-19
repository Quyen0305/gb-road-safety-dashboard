"""Independent reconciliation against the three original DfT tables."""
import json
from pathlib import Path
import sys

import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from road_safety.analytics import headline_metrics
from road_safety.data import DataBundle, DEFAULT_SOURCE, load_data


def validate_against_raw(bundle: DataBundle, collisions: pd.DataFrame,
                         vehicles: pd.DataFrame, casualties: pd.DataFrame) -> dict[str,int]:
    vehicle_ids=vehicles.collision_index.astype(str)+'_V'+vehicles.vehicle_reference.astype(str)
    casualty_ids=(casualties.collision_index.astype(str)+'_V'+casualties.vehicle_reference.astype(str)
                   +'_C'+casualties.casualty_reference.astype(str))
    for label, actual, expected in [('vụ tai nạn',bundle.collisions.collision_index,collisions.collision_index),
                                    ('phương tiện',bundle.vehicles.vehicle_key,vehicle_ids),
                                    ('thương vong',bundle.casualties.casualty_key,casualty_ids)]:
        assert len(actual)==len(expected), f'Sai số lượng {label}: {len(actual)} / {len(expected)}'
        assert set(actual)==set(expected), f'Sai tập khóa {label}'
    for label,actual,raw,key,severity in [
        ('vụ tai nạn',bundle.collisions,collisions,'collision_index','collision_severity'),
        ('thương vong',bundle.casualties,casualties.assign(casualty_key=casualty_ids),'casualty_key','casualty_severity')]:
        a=actual.set_index(key)[severity].sort_index()
        b=raw.set_index(key)[severity].sort_index()
        assert a.eq(b).all(), f'Sai mức độ {label}'
    return headline_metrics(bundle)


def main() -> None:
    stat=DEFAULT_SOURCE.stat()
    bundle=load_data(DEFAULT_SOURCE,stat.st_mtime_ns,stat.st_size)
    # Some IDs contain only digits and others contain letters. Preserve every ID
    # as text instead of allowing chunk-dependent numeric inference.
    options={'dtype':{'collision_index':'string'},'low_memory':False}
    c=pd.read_csv(ROOT/'dft-road-casualty-statistics-collision-2024.csv',usecols=['collision_index','collision_severity'],**options)
    v=pd.read_csv(ROOT/'dft-road-casualty-statistics-vehicle-2024.csv',usecols=['collision_index','vehicle_reference'],**options)
    p=pd.read_csv(ROOT/'dft-road-casualty-statistics-casualty-2024.csv',usecols=['collision_index','vehicle_reference','casualty_reference','casualty_severity'],**options)
    result=validate_against_raw(bundle,c,v,p)
    assert result==dict(collisions=100927,casualties=128272,fatalities=1602,vehicles=183514), 'Sai tổng đã đối chiếu của năm 2024'
    assert bundle.collisions.collision_severity.value_counts().to_dict()=={1:1502,2:23567,3:75858}
    assert bundle.collisions.country.value_counts().to_dict()=={'England':93847,'Scotland':4167,'Wales':2913}
    print(json.dumps({'status':'PASS','counts':result,'quality':bundle.quality},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
