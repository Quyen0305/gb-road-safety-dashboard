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
