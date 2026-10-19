import pandas as pd
import pytest


def test_join_duplicates_and_row_order_do_not_change_counts(joined_fixture):
    from road_safety.data import normalize_data
    for frame in [joined_fixture, joined_fixture.sample(frac=1, random_state=7)]:
        bundle = normalize_data(frame)
        assert (len(bundle.collisions), len(bundle.vehicles), len(bundle.casualties)) == (3, 4, 4)
        assert bundle.casualties.casualty_severity.eq(1).sum() == 1


def test_unknown_labels_remain_visible():
    from road_safety.labels import category_label
    assert category_label('weather_conditions', None) == 'Không xác định'
    assert '999' in category_label('weather_conditions', 999)


def test_missing_position_and_time_preserve_collisions(joined_fixture):
    from road_safety.data import normalize_data
    joined_fixture.loc[joined_fixture.collision_index.eq('A'), ['time', 'longitude']] = None
    joined_fixture.loc[joined_fixture.collision_index.eq('B'), 'latitude'] = 500
    bundle = normalize_data(joined_fixture)
    assert len(bundle.collisions) == 3
    assert bundle.collisions.hour.isna().sum() == 1
    assert bundle.collisions.valid_coordinates.sum() == 1


@pytest.mark.parametrize('column,value', [('collision_severity', 1), ('date', '2024-02-01')])
def test_conflicting_collision_attributes_are_rejected(joined_fixture, column, value):
    from road_safety.data import normalize_data
    joined_fixture.loc[0, column] = value
    with pytest.raises(ValueError, match='mâu thuẫn'):
        normalize_data(joined_fixture)


def test_missing_required_column_has_clear_error(joined_fixture):
    from road_safety.data import normalize_data
    with pytest.raises(ValueError, match='collision_index'):
        normalize_data(joined_fixture.drop(columns='collision_index'))


@pytest.mark.parametrize('key', ['collision_index', 'vehicle_key', 'casualty_key'])
def test_invalid_entity_keys_are_rejected(joined_fixture, key):
    from road_safety.data import normalize_data
    joined_fixture.loc[0, key] = ''
    with pytest.raises(ValueError, match=key):
        normalize_data(joined_fixture)
