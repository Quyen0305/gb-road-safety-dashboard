import json

from road_safety.data import normalize_data


def test_locality_fill_joins_by_code_and_counts_accidents_without_coordinates(joined_fixture):
    from road_safety.geography import region_features

    joined_fixture['local_authority_ons_district'] = joined_fixture.collision_index.map(
        {'A':'E08000025','B':'W06000015','C':'S12000049'})
    collisions = normalize_data(joined_fixture).collisions
    collisions.loc[collisions.collision_index.eq('A'),'longitude'] = float('nan')
    result = region_features(collisions,'locality')
    areas = {f['properties']['code']:f['properties'] for f in result['features']}
    assert len(areas) == 350
    assert areas['E08000025']['name'] == 'Birmingham'
    assert areas['E08000025']['count'] == 1
    assert sum(area['count'] for area in areas.values()) == 3
    assert all(f['geometry']['type'] in ['Polygon','MultiPolygon'] for f in result['features'])
    assert all(not code.startswith('N') for code in areas)


def test_country_fill_includes_special_heathrow_code_and_respects_filters(joined_fixture):
    from road_safety.geography import region_features

    joined_fixture.loc[joined_fixture.collision_index.eq('A'),'local_authority_ons_district'] = 'EHEATHROW'
    collisions = normalize_data(joined_fixture).collisions
    all_regions = region_features(collisions,'country')
    areas = {f['properties']['name']:f['properties'] for f in all_regions['features']}
    assert set(areas) == {'England','Scotland','Wales'}
    assert [areas[name]['count'] for name in ['England','Scotland','Wales']] == [1,1,1]
    assert len({tuple(area['color']) for area in areas.values()}) == 3
    filtered = region_features(collisions.loc[collisions.country.eq('Wales')],'country')
    assert {f['properties']['name']:f['properties']['count'] for f in filtered['features']} == {
        'England':0,'Scotland':0,'Wales':1}
    assert all(f['properties']['count'] == 0 for f in region_features(collisions.iloc[:0],'country')['features'])


def test_fill_colors_use_fixed_bands_and_neutral_zero():
    from road_safety.geography import locality_fill_color

    assert locality_fill_color(0) != locality_fill_color(1)
    assert locality_fill_color(49) == locality_fill_color(1)
    assert locality_fill_color(50) != locality_fill_color(49)
    assert locality_fill_color(999) != locality_fill_color(1000)
    assert locality_fill_color(1000) == locality_fill_color(10000)


def test_boundary_cache_is_not_mutated_by_filtered_counts(joined_fixture):
    from road_safety.geography import load_boundaries, region_features

    original = json.dumps(load_boundaries('country'),sort_keys=True)
    region_features(normalize_data(joined_fixture).collisions,'country')
    assert json.dumps(load_boundaries('country'),sort_keys=True) == original


def test_locality_choropleth_preserves_unmatched_codes_as_points(joined_fixture):
    from road_safety.charts import collision_map

    joined_fixture['local_authority_ons_district'] = joined_fixture.collision_index.map(
        {'A':'E08000025','B':'W06000015','C':'EHEATHROW'})
    collisions = normalize_data(joined_fixture).collisions
    spec = json.loads(collision_map(collisions,'Tô màu địa phương',show_names=False).to_json())
    regions = next(layer for layer in spec['layers'] if layer['id']=='region-fill')
    unmatched = next(layer for layer in spec['layers'] if layer['id']=='unmatched-localities')
    assert sum(f['properties']['count'] for f in regions['data']['features']) == 2
    assert sum(point['count'] for point in unmatched['data']) == 1
    assert unmatched['data'][0]['area_code'] == 'EHEATHROW'
    assert regions['getFillColor'] == '@@=properties.color'
    assert spec.get('mapProvider') is None


def test_country_choropleth_keeps_local_polygons_off_online_roads(joined_fixture):
    from road_safety.charts import collision_map

    spec = json.loads(collision_map(normalize_data(joined_fixture).collisions,
        'Tô màu quốc gia',online=True,show_names=False).to_json())
    assert [layer['id'] for layer in spec['layers']] == ['region-fill']
    assert len(spec['layers'][0]['data']['features']) == 3
    assert spec['layers'][0]['opacity'] < 1


def test_country_labels_show_totals_and_selected_locality(joined_fixture):
    from road_safety.charts import collision_map

    joined_fixture['local_authority_ons_district'] = joined_fixture.collision_index.map(
        {'A':'E08000025','B':'W06000015','C':'S12000049'})
    collisions = normalize_data(joined_fixture).collisions
    spec = json.loads(collision_map(collisions,'Tô màu quốc gia',focus_code='E08000025').to_json())
    labels = next(layer for layer in spec['layers'] if layer['id']=='locality-names')['data']
    assert {row['group'] for row in labels} == {'England','Scotland','Wales','Birmingham'}
    assert all('1 vụ' in row['label'] for row in labels)
    assert spec['initialViewState']['zoom'] == 8.5
