import pandas as pd
import pytest
from road_safety.data import normalize_data


@pytest.fixture
def source_tables(joined_fixture):
    f=joined_fixture.copy()
    f['vehicle_key']=f.collision_index+'_V'+f.vehicle_key.str[1:]
    f['casualty_key']=f.vehicle_key+'_C'+f.casualty_key.str[1:]
    c=pd.DataFrame({'collision_index':['A','B','C'],'collision_severity':[2,1,3]})
    v=pd.DataFrame({'collision_index':['A','A','B','C'],'vehicle_reference':[1,2,3,4]})
    p=pd.DataFrame({'collision_index':['A','A','B','C'],'vehicle_reference':[1,1,3,4],
                    'casualty_reference':[1,2,3,4],'casualty_severity':[2,3,1,3]})
    return normalize_data(f),c,v,p


def test_raw_sources_reconcile(source_tables):
    from scripts.validate_data import validate_against_raw
    assert validate_against_raw(*source_tables) == dict(collisions=3,casualties=4,fatalities=1,vehicles=4)


def test_same_count_with_wrong_vehicle_ids_is_rejected(source_tables):
    from scripts.validate_data import validate_against_raw
    b,c,v,p=source_tables
    v.loc[0,'vehicle_reference']=5
    with pytest.raises(AssertionError,match='phương tiện'):
        validate_against_raw(b,c,v,p)


def test_wrong_casualty_severity_is_rejected(source_tables):
    from scripts.validate_data import validate_against_raw
    b,c,v,p=source_tables
    p.loc[0,'casualty_severity']=1
    with pytest.raises(AssertionError,match='thương vong'):
        validate_against_raw(b,c,v,p)
