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


@pytest.mark.parametrize('groups',[['00h','01h','02h'],['T1','T2','T3']])
def test_time_axis_stays_chronological_when_first_severity_trace_has_gaps(groups):
    table=pd.DataFrame({'group':groups,'severity':['Có tử vong','Nhẹ','Có tử vong'],
                        'count':[1,2,1],'group_total':[1,2,1],'percentage':[100,100,100]})
    figure=severity_chart(table,True)
    assert list(figure.data[0].x) == [groups[0],groups[2]]
    assert figure.layout.xaxis.categoryorder == 'array'
    assert list(figure.layout.xaxis.categoryarray) == groups
