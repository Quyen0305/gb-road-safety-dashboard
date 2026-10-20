import json
import pandas as pd
import pytest

from road_safety.data import normalize_data
from road_safety.charts import bar_chart, collision_map, severity_chart
from road_safety.labels import SEVERITY_COLORS


def test_severity_colors_follow_dashboard_semantics():
    assert SEVERITY_COLORS == {
        'Có tử vong': '#DC2626',
        'Nghiêm trọng': '#F59E0B',
        'Nhẹ': '#3B82F6',
        'Không xác định': '#9CA3AF',
    }


def test_horizontal_bar_can_show_values_at_bar_ends():
    table = pd.DataFrame({'group':['England','Scotland'],'count':[100,20]})
    figure = bar_chart(table,'count','group','Tai nạn theo quốc gia',True,show_values=True)
    assert figure.data[0].texttemplate == '%{x:,.0f}'
    assert figure.data[0].textposition == 'outside'
    assert figure.data[0].cliponaxis is False


def test_stacked_severity_chart_can_show_group_totals():
    table = pd.DataFrame({
        'group':['Đô thị','Đô thị','Nông thôn','Nông thôn'],
        'severity':['Có tử vong','Nhẹ','Có tử vong','Nhẹ'],
        'count':[2,8,1,4],
        'group_total':[10,10,5,5],
        'percentage':[20,80,20,80],
    })
    figure = severity_chart(table,False,show_totals=True)
    assert [annotation.text for annotation in figure.layout.annotations] == ['10','5']


def test_offline_map_has_no_remote_basemap_sources_and_preserves_counts(joined_fixture):
    c=normalize_data(joined_fixture).collisions
    deck=collision_map(c,'Mật độ theo ô',online=False)
    spec=json.loads(deck.to_json())
    # Streamlit distinguishes Pydeck's no-provider sentinel from a null style,
    # which requests Streamlit's online theme default.
    assert spec.get('mapStyle') == '__MAP_STYLE__'
    assert spec.get('mapProvider') is None
    assert sum(row['count'] for row in spec['layers'][-1]['data']) == 3


def test_online_map_does_not_cover_roads_with_opaque_polygons(joined_fixture):
    deck=collision_map(normalize_data(joined_fixture).collisions,'Điểm theo mức độ',online=True)
    assert len(deck.layers) == 1
    assert len(json.loads(deck.to_json())['layers'][0]['data']) == 3


def test_locality_map_names_ranks_and_bubbles_use_the_same_counts(joined_fixture):
    from road_safety.analytics import locality_summary

    joined_fixture['local_authority_ons_district'] = joined_fixture.collision_index.map(
        {'A':'E08000025','B':'E08000035','C':'E08000003'})
    collisions = normalize_data(joined_fixture).collisions
    table = locality_summary(collisions)
    spec = json.loads(collision_map(collisions,'Theo địa phương',places=table).to_json())
    bubbles = next(layer for layer in spec['layers'] if layer['id'] == 'locality-bubbles')
    labels = next(layer for layer in spec['layers'] if layer['id'] == 'locality-names')
    assert sum(row['count'] for row in bubbles['data']) == 3
    assert len(labels['data']) == 3
    assert labels['characterSet'] == 'auto'
    assert labels['getTextAnchor'] == 'middle'
    assert labels['getAlignmentBaseline'] == 'center'
    assert len({tuple(row['label_position']) for row in labels['data']}) == 3
    birmingham = next(row for row in labels['data'] if row['group'] == 'Birmingham')
    assert birmingham['count'] == 1
    assert 'Birmingham' in birmingham['label']
    assert '1 vụ' in birmingham['label']

    focused = json.loads(collision_map(collisions,'Theo địa phương',places=table,
        focus_code='E08000025').to_json())
    assert focused['initialViewState']['zoom'] == 8.5
    focused_labels = next(layer for layer in focused['layers'] if layer['id'] == 'locality-names')
    assert next(row for row in focused_labels['data'] if row['group']=='Birmingham')['priority'] == 1000
    hidden = json.loads(collision_map(collisions,'Theo địa phương',places=table,show_names=False).to_json())
    assert all(layer['id'] != 'locality-names' for layer in hidden['layers'])


@pytest.mark.parametrize('groups',[['00h','01h','02h'],['T1','T2','T3']])
def test_time_axis_stays_chronological_when_first_severity_trace_has_gaps(groups):
    table=pd.DataFrame({'group':groups,'severity':['Có tử vong','Nhẹ','Có tử vong'],
                        'count':[1,2,1],'group_total':[1,2,1],'percentage':[100,100,100]})
    figure=severity_chart(table,True)
    assert list(figure.data[0].x) == [groups[0],groups[2]]
    assert figure.layout.xaxis.categoryorder == 'array'
    assert list(figure.layout.xaxis.categoryarray) == groups
