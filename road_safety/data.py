from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from .labels import AGE_GROUPS, UNKNOWN, category_label

COLLISION_COLUMNS = ['collision_index', 'date', 'time', 'longitude', 'latitude', 'police_force',
                     'collision_severity', 'local_authority_ons_district', 'urban_or_rural_area',
                     'weather_conditions', 'light_conditions', 'road_surface_conditions', 'road_type', 'speed_limit']
VEHICLE_COLUMNS = ['collision_index', 'vehicle_key', 'vehicle_type']
CASUALTY_COLUMNS = ['collision_index', 'casualty_key', 'casualty_severity', 'age_of_casualty',
                    'sex_of_casualty', 'casualty_class']
REQUIRED_COLUMNS = set(COLLISION_COLUMNS + VEHICLE_COLUMNS + CASUALTY_COLUMNS + ['has_casualty_record'])
DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / 'du_lieu_tai_nan_2024_san_sang_truc_quan.csv'


@dataclass
class DataBundle:
    collisions: pd.DataFrame
    vehicles: pd.DataFrame
    casualties: pd.DataFrame
    quality: dict[str, int]


def _one_per_key(frame: pd.DataFrame, key: str, columns: list[str]) -> pd.DataFrame:
    values = frame[key].astype('string')
    if values.isna().any() or values.str.strip().eq('').any():
        raise ValueError(f'Khóa {key} bị thiếu hoặc rỗng. Hãy kiểm tra tệp dữ liệu.')
    distinct = frame[columns].drop_duplicates()
    if distinct[key].duplicated().any():
        raise ValueError(f'Dữ liệu mâu thuẫn giữa các dòng cùng khóa {key}.')
    return distinct.reset_index(drop=True).copy()


def normalize_data(frame: pd.DataFrame) -> DataBundle:
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError('Thiếu cột bắt buộc: ' + ', '.join(sorted(missing)))
    df = frame[list(REQUIRED_COLUMNS)].copy()
    present = df.has_casualty_record.astype('string').str.lower().str.strip()
    if not present.isin(['true', 'false', '1', '0']).all():
        raise ValueError('has_casualty_record có giá trị không hợp lệ.')
    c = _one_per_key(df, 'collision_index', COLLISION_COLUMNS)
    v = _one_per_key(df, 'vehicle_key', VEHICLE_COLUMNS)
    p = _one_per_key(df[present.isin(['true', '1'])], 'casualty_key', CASUALTY_COLUMNS)
    c['date'] = pd.to_datetime(c.date, format='%Y-%m-%d', errors='coerce')
    if c.date.isna().any():
        raise ValueError('Ngày không hợp lệ: cần định dạng YYYY-MM-DD và không để trống.')
    for table, columns in [(c, ['police_force', 'collision_severity', 'urban_or_rural_area',
                              'weather_conditions', 'light_conditions', 'road_surface_conditions', 'road_type', 'speed_limit']),
                           (v, ['vehicle_type']), (p, ['casualty_severity', 'sex_of_casualty', 'casualty_class'])]:
        for column in columns:
            table[column] = pd.to_numeric(table[column], errors='coerce').fillna(-1).astype(int)
            table[column + '_label'] = table[column].map(lambda value: category_label(column, value))
    c['country'] = c.local_authority_ons_district.astype('string').str[0].map(
        {'E': 'England', 'S': 'Scotland', 'W': 'Wales'}).fillna(UNKNOWN)
    c['month'] = c.date.dt.month
    c['weekday'] = c.date.dt.dayofweek
    c['is_weekend'] = c.weekday.ge(5)
    times = pd.to_datetime(c.time, format='%H:%M', errors='coerce')
    c['hour'] = times.dt.hour.astype('Int64')
    for col in ['longitude', 'latitude']:
        c[col] = pd.to_numeric(c[col], errors='coerce')
    c['valid_coordinates'] = c.longitude.between(-9, 3) & c.latitude.between(49, 61)
    c['severity_label'] = c.collision_severity_label
    p['age_of_casualty'] = pd.to_numeric(p.age_of_casualty, errors='coerce')
    ages = p.age_of_casualty.where(p.age_of_casualty.between(0, 120))
    p['age_group'] = pd.cut(ages, [-1, 15, 24, 34, 44, 54, 64, 120], labels=AGE_GROUPS[:-1]).astype('string').fillna(UNKNOWN)
    quality = {'source_rows': len(frame), 'invalid_coordinates': int((~c.valid_coordinates).sum()),
               'missing_hours': int(c.hour.isna().sum()), 'unknown_ages': int(p.age_group.eq(UNKNOWN).sum())}
    return DataBundle(c, v, p, quality)


@st.cache_data(show_spinner='Đang chuẩn bị dữ liệu Great Britain 2024…', max_entries=2)
def load_data(path: Path, mtime_ns: int, file_size: int) -> DataBundle:
    """mtime_ns and file_size deliberately participate in Streamlit's cache key."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f'Không tìm thấy tệp dữ liệu: {path.name}')
    return normalize_data(pd.read_csv(path, usecols=lambda col: col in REQUIRED_COLUMNS, low_memory=False))
