import json
from pathlib import Path

import pandas as pd

LOOKUPS = json.loads((Path(__file__).parent / 'assets/lookups.json').read_text(encoding='utf-8'))
LOCAL_AUTHORITIES = json.loads((Path(__file__).parent / 'assets/local_authorities.json').read_text(encoding='utf-8'))['names']
UNKNOWN = 'Không xác định'
SEVERITIES = {1: 'Có tử vong', 2: 'Nghiêm trọng', 3: 'Nhẹ'}
SEVERITY_COLORS = {'Có tử vong': '#DC2626', 'Nghiêm trọng': '#F59E0B', 'Nhẹ': '#3B82F6', UNKNOWN: '#9CA3AF'}
WEEKDAYS = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật']
AGE_GROUPS = ['0–15', '16–24', '25–34', '35–44', '45–54', '55–64', '65+', UNKNOWN]
CONDITIONS = {'weather_conditions': 'Thời tiết', 'light_conditions': 'Ánh sáng',
              'road_surface_conditions': 'Mặt đường', 'road_type': 'Loại đường', 'speed_limit': 'Giới hạn tốc độ'}


def category_label(field: str, code: object) -> str:
    if pd.isna(code) or str(code).strip() in ('', 'Không xác định'):
        return UNKNOWN
    try:
        numeric = float(code)
        key = str(int(numeric)) if numeric.is_integer() else str(code)
    except (TypeError, ValueError):
        return str(code)
    if key == '-1':
        return UNKNOWN
    if key == '-2':
        return 'Không áp dụng'
    entry = LOOKUPS['fields'].get(field, {}).get(key)
    if entry:
        return entry['vi']
    if field == 'speed_limit' and numeric > 0 and numeric != 99:
        return f'{key} mph'
    return f'Chưa có nhãn (mã {key})'
