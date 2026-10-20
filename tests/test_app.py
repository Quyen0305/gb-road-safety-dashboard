from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def app(joined_fixture, tmp_path, monkeypatch):
    source = tmp_path / 'input.csv'
    joined_fixture.to_csv(source, index=False)
    monkeypatch.setenv('ROADLENS_DATA', str(source))
    return AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30)


def test_filter_persistence_empty_selection_and_reset(app):
    app.run()
    assert not app.exception
    assert [metric.value for metric in app.metric] == ['3','4','1','4']
    app.multiselect(key='f_country').set_value(['England']).run()
    assert [metric.value for metric in app.metric] == ['1','2','0','2']
    app.switch_page('views/temporal.py').run()
    assert not app.exception
    assert app.multiselect(key='f_country').value == ['England']
    assert [metric.value for metric in app.metric] == ['1','2','0','2']
    app.multiselect(key='f_severity').set_value([]).run()
    assert not app.exception
    assert all(metric.value == '0' for metric in app.metric)
    assert any('Không có dữ liệu' in item.value for item in app.info)
    app.button(key='reset_filters').click().run()
    assert not app.exception
    assert [metric.value for metric in app.metric] == ['3','4','1','4']
    assert any(item.value == 'Thời gian' for item in app.subheader)


@pytest.mark.parametrize('page', ['overview', 'temporal', 'spatial', 'severity', 'people_vehicles', 'conditions'])
def test_each_page_works_with_one_collision(app, page):
    app.run()
    app.multiselect(key='f_country').set_value(['Wales']).run()
    app.switch_page(f'views/{page}.py').run()
    assert not app.exception
    assert [metric.value for metric in app.metric] == ['1','1','1','1']


def test_all_condition_choices(app):
    app.run().switch_page('views/conditions.py').run()
    for field in ['weather_conditions','light_conditions','road_surface_conditions','road_type','speed_limit']:
        app.selectbox(key='condition').set_value(field).run()
        assert not app.exception


def test_incomplete_date_range_does_not_crash(app):
    app.run()
    app.date_input(key='f_dates').set_value((app.date_input(key='f_dates').value[0],)).run()
    assert not app.exception
    assert any('ngày bắt đầu' in item.value for item in app.info)


@pytest.mark.parametrize('key',['f_country','f_severity','f_urban','f_police'])
def test_clear_all_filter_values_stays_empty_until_reset(app,key):
    app.run()
    before = {name:list(app.multiselect(key=name).value)
              for name in ['f_country','f_severity','f_urban','f_police']}
    app.multiselect(key=key).set_value([]).run()
    assert not app.exception
    assert app.multiselect(key=key).value == []
    assert all(metric.value == '0' for metric in app.metric)
    for other in before:
        if other != key:
            assert app.multiselect(key=other).value == before[other]
    app.switch_page('views/temporal.py').run()
    assert not app.exception
    assert app.multiselect(key=key).value == []
    app.button(key='reset_filters').click().run()
    assert not app.exception
    assert [metric.value for metric in app.metric] == ['3','4','1','4']


@pytest.mark.parametrize('key',['f_country','f_severity','f_urban','f_police'])
def test_explicit_clear_button_clears_only_its_filter(app,key):
    app.run()
    previous = {widget.key:list(widget.value) for widget in app.multiselect}
    app.button(key='clear_'+key).click().run()
    assert not app.exception
    assert app.multiselect(key=key).value == []
    assert app.button(key='clear_'+key).disabled
    assert [metric.value for metric in app.metric] == ['0','0','0','0']
    for other in previous:
        if other != key:
            assert app.multiselect(key=other).value == previous[other]
    app.switch_page('views/temporal.py').run()
    assert app.multiselect(key=key).value == []
    app.button(key='reset_filters').click().run()
    assert not app.button(key='clear_'+key).disabled
    assert [metric.value for metric in app.metric] == ['3','4','1','4']


def test_navigation_reuses_selection_but_filter_changes_refresh_it(app):
    app.run()
    original = app.session_state['_dashboard_context'].data
    app.switch_page('views/temporal.py').run()
    assert not app.exception
    assert app.session_state['_dashboard_context'].data is original
    app.multiselect(key='f_country').set_value(['Wales']).run()
    selected = app.session_state['_dashboard_context'].data
    assert selected is not original
    assert [metric.value for metric in app.metric] == ['1','1','1','1']
    app.switch_page('views/overview.py').run()
    assert app.session_state['_dashboard_context'].data is selected


def test_source_file_change_invalidates_session_selection(app):
    import os
    import pandas as pd

    app.run()
    original = app.session_state['_dashboard_context']
    source = original.source_path
    previous_mtime = source.stat().st_mtime_ns
    frame = pd.read_csv(source)
    frame.loc[frame.casualty_key.eq('P3'),'casualty_severity'] = 2
    frame.to_csv(source,index=False)
    # Make the source version change deterministic even on coarse file systems.
    os.utime(source,ns=(previous_mtime + 1_000_000_000,previous_mtime + 1_000_000_000))
    app.run()
    assert not app.exception
    assert app.session_state['_dashboard_context'].data is not original.data
    assert [metric.value for metric in app.metric] == ['3','4','0','4']


def test_spatial_search_and_layers_survive_filter_changes(app):
    app.run().switch_page('views/spatial.py').run()
    code = app.session_state['_dashboard_context'].data.collisions.local_authority_ons_district.iloc[0]
    app.selectbox(key='map_focus').set_value(code).run()
    app.multiselect(key='f_country').set_value(['Wales']).run()
    for mode in ['Tô màu địa phương','Tô màu quốc gia','Theo địa phương','Mật độ theo ô','Điểm theo mức độ']:
        app.selectbox(key='map_mode').set_value(mode).run()
        assert not app.exception
        assert [metric.value for metric in app.metric] == ['1','1','1','1']
