"""Rebuild the bundled bilingual lookup from the saved official DfT workbook."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VI = {
 'collision_severity': {1:'Có tử vong',2:'Nghiêm trọng',3:'Nhẹ'},
 'casualty_severity': {1:'Tử vong',2:'Bị thương nặng',3:'Bị thương nhẹ'},
 'urban_or_rural_area': {1:'Đô thị',2:'Nông thôn',3:'Không xác định'},
 'weather_conditions': {1:'Quang, không gió mạnh',2:'Mưa, không gió mạnh',3:'Tuyết, không gió mạnh',4:'Quang, gió mạnh',5:'Mưa, gió mạnh',6:'Tuyết, gió mạnh',7:'Sương mù',8:'Thời tiết khác',9:'Không xác định'},
 'light_conditions': {1:'Ban ngày',4:'Tối, đèn đường bật',5:'Tối, đèn đường tắt',6:'Tối, không có đèn đường',7:'Tối, chưa rõ đèn đường'},
 'road_surface_conditions': {1:'Khô',2:'Ướt / ẩm',3:'Tuyết',4:'Băng / sương giá',5:'Ngập trên 3 cm',6:'Dầu / diesel',7:'Bùn',9:'Không xác định'},
 'road_type': {1:'Vòng xuyến',2:'Đường một chiều',3:'Đường có dải phân cách',6:'Đường không dải phân cách',7:'Đường nhánh kết nối',9:'Không xác định',12:'Một chiều / nhánh kết nối'},
 'speed_limit': {99:'Không xác định'},
 'casualty_class': {1:'Người điều khiển',2:'Hành khách',3:'Người đi bộ'},
 'sex_of_casualty': {1:'Nam',2:'Nữ',9:'Không xác định'},
 'vehicle_type': {1:'Xe đạp',2:'Mô tô ≤ 50 cc',3:'Mô tô 51–125 cc',4:'Mô tô 126–500 cc',5:'Mô tô > 500 cc',8:'Taxi / xe thuê riêng',9:'Ô tô',10:'Xe khách 8–16 ghế',11:'Xe buýt / khách ≥ 17 ghế',16:'Ngựa có người cưỡi',17:'Xe nông nghiệp',18:'Tàu điện',19:'Xe tải / van ≤ 3,5 t',20:'Xe tải > 3,5 đến < 7,5 t',21:'Xe tải ≥ 7,5 t',22:'Xe hỗ trợ di chuyển',23:'Mô tô điện',33:'Phương tiện điện cá nhân',90:'Phương tiện khác',97:'Mô tô chưa rõ dung tích',98:'Xe tải chưa rõ khối lượng',99:'Không xác định',103:'Scooter (mã lịch sử)',104:'Mô tô (mã lịch sử)',105:'Mô tô ba bánh (mã lịch sử)',106:'Mô tô > 125 cc (mã lịch sử)',108:'Taxi (mã lịch sử)',109:'Ô tô (mã lịch sử)',110:'Minibus / xe lưu trú (mã lịch sử)',113:'Xe tải > 3,5 t (mã lịch sử)'}
}

if __name__ == '__main__':
    guide = pd.read_excel(ROOT / 'road_safety/assets/dft-data-guide.xlsx', sheet_name='2024_code_list')
    fields = {}
    for field in [*VI, 'police_force']:
        entries = {}
        for _, row in guide[guide['field name'].eq(field)].iterrows():
            try:
                code = int(row['code/format'])
            except (ValueError, TypeError):
                continue
            english = str(row['label'])
            vietnamese = 'Không xác định' if code == -1 else VI.get(field, {}).get(code, english)
            entries[str(code)] = {'en': english, 'vi': vietnamese}
        fields[field] = entries
    out = {'source': 'https://www.gov.uk/government/statistical-data-sets/road-safety-open-data',
           'workbook': 'dft-data-guide.xlsx', 'sheet': '2024_code_list',
           'retrieved': '2026-10-19', 'license': 'Open Government Licence v3.0', 'fields': fields}
    (ROOT / 'road_safety/assets/lookups.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Saved verified code lists for', len(fields), 'fields.')
