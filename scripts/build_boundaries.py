"""Bundle generalised official ONS 2024 boundaries; no downloads at app runtime."""
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVICE = 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/'
SOURCES = {
    'locality': ('Local_Authority_Districts_May_2024_Boundaries_UK_BGC', 'LAD24', 350),
    'country': ('Countries_December_2024_Boundaries_UK_BGC', 'CTRY24', 3),
}


def download(level):
    service, field, expected = SOURCES[level]
    endpoint = SERVICE + service + '/FeatureServer/0/query'
    params = dict(where=f"{field}CD NOT LIKE 'N%'",outFields=f'{field}CD,{field}NM,LONG,LAT',
                  outSR=4326,returnGeometry='true',maxAllowableOffset=0.001,
                  geometryPrecision=5,f='geojson')
    with urlopen(endpoint + '?' + urlencode(params),timeout=90) as response:
        data = json.load(response)
    features = data.get('features',[])
    if len(features) != expected or data.get('exceededTransferLimit'):
        raise ValueError(f'Incomplete {level} boundaries: {len(features)} / {expected}')
    for feature in features:
        props = feature['properties']
        feature['properties'] = dict(code=props[field+'CD'],name=props[field+'NM'],
                                     longitude=props['LONG'],latitude=props['LAT'])
        if feature['geometry']['type'] not in ['Polygon','MultiPolygon']:
            raise ValueError('Expected polygon boundaries')
    output = dict(type='FeatureCollection',features=features,
                  source=endpoint,source_dataset=service,retrieved=date.today().isoformat(),
                  generalisation='ONS BGC (20m), further generalised to 0.001 degrees for display',
                  attribution='Contains OS data © Crown copyright and database right 2024. '
                              'Contains National Statistics data © Crown copyright and database right 2024.',
                  license='Open Government Licence v3.0')
    path = ROOT / f'road_safety/assets/gb-{level}-2024.geojson'
    path.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(f'{level}: {len(features)} regions, {path.stat().st_size:,} bytes')


if __name__ == '__main__':
    for level in SOURCES:
        download(level)
