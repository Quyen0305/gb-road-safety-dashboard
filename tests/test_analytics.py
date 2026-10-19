from datetime import date
from io import BytesIO

import pandas as pd
import pytest

from road_safety.data import normalize_data


def test_filter_relates_people_and_vehicles(joined_fixture):
    from road_safety.analytics import FilterSpec, filter_bundle, headline_metrics
    bundle = normalize_data(joined_fixture)
    spec = FilterSpec(date(2024,1,1), date(2024,1,7), ('England',), (1,2,3), (1,), (1,))
    assert headline_metrics(filter_bundle(bundle, spec)) == dict(collisions=1, vehicles=2, casualties=2, fatalities=0)
    spec.severities = ()
    assert headline_metrics(filter_bundle(bundle, spec)) == dict(collisions=0, vehicles=0, casualties=0, fatalities=0)


def test_date_bounds_are_inclusive(joined_fixture):
    from road_safety.analytics import FilterSpec, filter_bundle
    spec = FilterSpec(date(2024,1,6), date(2024,1,6), ('Wales',), (1,2,3), (1,), (1,))
    assert filter_bundle(normalize_data(joined_fixture), spec).collisions.collision_index.tolist() == ['B']


def test_day_type_denominator_includes_zero_collision_dates(joined_fixture):
    from road_safety.analytics import day_type_summary
    c = normalize_data(joined_fixture).collisions
    result = day_type_summary(c, date(2024,1,1), date(2024,1,7))
    assert result.calendar_days.tolist() == [5,2]
    assert result.per_day.tolist() == [0.2,1.0]
    result = day_type_summary(c.iloc[:1], date(2024,1,1), date(2024,1,1))
    assert pd.isna(result.iloc[1].per_day)


def test_severity_percentage_uses_collision_denominator(joined_fixture):
    from road_safety.analytics import severity_by
    result = severity_by(normalize_data(joined_fixture).collisions, 'urban_or_rural_area_label')
    assert result['count'].sum() == 3
    assert result.percentage.sum() == pytest.approx(100)
    assert result.loc[result.severity.isin(['Có tử vong', 'Nghiêm trọng']), 'percentage'].sum() == pytest.approx(200/3)
    assert result.group_total.tolist() == [3,3,3]


def test_chart_totals_and_missing_observations(joined_fixture):
    from road_safety.analytics import count_by, time_heatmap, map_cells
    joined_fixture.loc[joined_fixture.collision_index.eq('A'), ['time', 'longitude']] = None
    c = normalize_data(joined_fixture).collisions
    assert count_by(c, 'month', list(range(1,13)))['count'].sum() == 3
    assert time_heatmap(c).to_numpy().sum() == 2
    assert time_heatmap(c).shape == (7,24)
    assert map_cells(c, 0.1)['count'].sum() == 2
    assert count_by(pd.DataFrame({'g':['England',None]}), 'g', ['England'])['count'].sum() == 2


def test_empty_aggregates_and_csv_preserve_vietnamese(joined_fixture):
    from road_safety.analytics import count_by, severity_by, csv_bytes, map_cells
    c = normalize_data(joined_fixture).collisions.iloc[:0]
    assert severity_by(c, 'country').empty
    assert map_cells(c, 0.1).empty
    table = count_by(pd.DataFrame({'g':['Đô thị','Đô thị']}), 'g')
    raw = csv_bytes(table)
    assert raw.startswith(b'\xef\xbb\xbf')
    back = pd.read_csv(BytesIO(raw))
    assert back.iloc[0].tolist() == ['Đô thị',2]


def test_people_and_vehicle_groups_keep_missing_data(joined_fixture):
    from road_safety.analytics import count_by
    joined_fixture.loc[joined_fixture.casualty_key.eq('P1'), 'age_of_casualty'] = -1
    bundle = normalize_data(joined_fixture)
    assert count_by(bundle.casualties, 'age_group').set_index('group').loc['Không xác định','count'] == 1
    assert count_by(bundle.vehicles, 'vehicle_type_label')['count'].sum() == 4
