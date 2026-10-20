from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from .data import DataBundle
from .labels import LOCAL_AUTHORITIES, UNKNOWN


@dataclass
class FilterSpec:
    start: date
    end: date
    countries: tuple[str, ...]
    severities: tuple[int, ...]
    urban_areas: tuple[int, ...]
    police_forces: tuple[int, ...]


def filter_bundle(bundle: DataBundle, filters: FilterSpec) -> DataBundle:
    c = bundle.collisions
    keep = (c.date.between(pd.Timestamp(filters.start), pd.Timestamp(filters.end))
            & c.country.isin(filters.countries) & c.collision_severity.isin(filters.severities)
            & c.urban_or_rural_area.isin(filters.urban_areas) & c.police_force.isin(filters.police_forces))
    selected = c.loc[keep].copy()
    # Collision keys are unique after normalization. Index lookup avoids the
    # per-key Arrow scalar conversion in StringArray.isin on large selections.
    ids = pd.Index(selected.collision_index)
    vehicle_rows = ids.get_indexer(bundle.vehicles.collision_index) >= 0
    casualty_rows = ids.get_indexer(bundle.casualties.collision_index) >= 0
    return DataBundle(selected, bundle.vehicles.loc[vehicle_rows].copy(),
                      bundle.casualties.loc[casualty_rows].copy(),
                      {'invalid_coordinates': int((~selected.valid_coordinates).sum()),
                       'missing_hours': int(selected.hour.isna().sum())})


def headline_metrics(bundle: DataBundle) -> dict[str, int]:
    return dict(collisions=len(bundle.collisions), casualties=len(bundle.casualties),
                fatalities=int(bundle.casualties.casualty_severity.eq(1).sum()), vehicles=len(bundle.vehicles))


def count_by(frame: pd.DataFrame, column: str, order: list | None = None) -> pd.DataFrame:
    values = frame[column].astype(object).where(frame[column].notna(), UNKNOWN)
    counts = values.value_counts(sort=False)
    if order is not None:
        counts = counts.reindex(list(order) + [v for v in counts.index if v not in order], fill_value=0)
    else:
        counts = counts.sort_values(ascending=False, kind='stable')
    return counts.rename_axis('group').rename('count').reset_index()


def severity_by(collisions: pd.DataFrame, column: str) -> pd.DataFrame:
    frame = pd.DataFrame({'group': collisions[column].astype(object).where(collisions[column].notna(), UNKNOWN),
                          'severity': collisions.severity_label})
    result = frame.groupby(['group', 'severity'], observed=True, sort=False).size().rename('count').reset_index()
    result['group_total'] = result.groupby('group')['count'].transform('sum')
    result['percentage'] = result['count'].div(result.group_total).mul(100)
    return result


def time_heatmap(collisions: pd.DataFrame) -> pd.DataFrame:
    result = collisions.groupby(['weekday', 'hour'], observed=True).size().unstack('hour', fill_value=0)
    return result.reindex(index=range(7), columns=range(24), fill_value=0).fillna(0).astype(int)


def day_type_summary(collisions: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    days = pd.date_range(start, end)
    n_weekend = int((days.dayofweek >= 5).sum())
    counts = collisions.is_weekend.value_counts()
    result = pd.DataFrame({'day_type': ['Ngày thường', 'Cuối tuần'],
                           'collisions': [int(counts.get(False, 0)), int(counts.get(True, 0))],
                           'calendar_days': [len(days) - n_weekend, n_weekend]})
    result['per_day'] = result.collisions / result.calendar_days.replace(0, np.nan)
    return result


def map_cells(collisions: pd.DataFrame, cell_degrees: float) -> pd.DataFrame:
    if not np.isfinite(cell_degrees) or cell_degrees <= 0:
        raise ValueError('Kích thước ô bản đồ phải lớn hơn 0.')
    points = collisions.loc[collisions.valid_coordinates, ['longitude', 'latitude', 'severity_label']].copy()
    for col in ['longitude', 'latitude']:
        points[col] = (np.floor(points[col] / cell_degrees) + 0.5) * cell_degrees
    return points.groupby(['longitude', 'latitude', 'severity_label'], observed=True, sort=False).size().rename('count').reset_index()


def locality_summary(collisions: pd.DataFrame) -> pd.DataFrame:
    """Count recorded authorities exactly; use valid crash coordinates for markers."""
    frame = pd.DataFrame({
        'area_code': collisions.local_authority_ons_district.astype('string').fillna(UNKNOWN),
        'longitude': collisions.longitude.where(collisions.valid_coordinates),
        'latitude': collisions.latitude.where(collisions.valid_coordinates),
    })
    result = frame.groupby('area_code',sort=True,dropna=False).agg(
        count=('area_code','size'),longitude=('longitude','mean'),latitude=('latitude','mean')).reset_index()
    result['group'] = result.area_code.map(LOCAL_AUTHORITIES).fillna(
        result.area_code.map(lambda code: UNKNOWN if code in ('', '-1', UNKNOWN) else f'Chưa có nhãn ({code})'))
    result = result.sort_values('count',ascending=False,kind='stable').reset_index(drop=True)
    result['rank'] = np.arange(1,len(result)+1)
    return result[['area_code','group','count','longitude','latitude','rank']]


def csv_bytes(table: pd.DataFrame) -> bytes:
    return table.to_csv(index=False).encode('utf-8-sig')
