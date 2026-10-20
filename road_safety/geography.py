"""Join filtered accident totals to locally bundled ONS boundaries."""
import html
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

COUNTRY_COLORS = {'England':[59,130,246,210], 'Scotland':[15,159,146,210],
                  'Wales':[245,158,11,210]}
ZERO_COLOR = [226,232,240,210]
# Fixed breaks keep the meaning of a shade stable when filters change.
LOCALITY_COLOR_BINS = [
    (1,'1–49',[219,234,254,230]),
    (50,'50–149',[147,197,253,230]),
    (150,'150–399',[96,165,250,230]),
    (400,'400–999',[37,99,235,230]),
    (1000,'≥ 1.000',[30,64,175,230]),
]


def locality_fill_color(count: int) -> list[int]:
    if count <= 0:
        return ZERO_COLOR.copy()
    return next(color.copy() for lower,_,color in reversed(LOCALITY_COLOR_BINS) if count >= lower)


@lru_cache(maxsize=2)
def load_boundaries(level: str) -> dict:
    if level not in ['locality','country']:
        raise ValueError(f'Unknown boundary level: {level}')
    path = Path(__file__).parent / f'assets/gb-{level}-2024.geojson'
    return json.loads(path.read_text(encoding='utf-8'))


def region_features(collisions: pd.DataFrame, level: str) -> dict:
    geometry = load_boundaries(level)
    field = 'country' if level == 'country' else 'local_authority_ons_district'
    counts = collisions.groupby(field,observed=True).size().to_dict()
    features = []
    for feature in geometry['features']:
        props = feature['properties'].copy()
        count = int(counts.get(props['name'] if level == 'country' else props['code'],0))
        props.update(count=count,count_display=f'{count:,}'.replace(',','.'),
                     description=html.escape(f"{props['name']} · {props['code']}"),
                     color=COUNTRY_COLORS[props['name']].copy() if level == 'country' and count else locality_fill_color(count))
        features.append(dict(type='Feature',properties=props,geometry=feature['geometry']))
    return dict(type='FeatureCollection',features=features)
