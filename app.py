"""Streamlit entrypoint for the approved RoadLens dashboard."""
import os
from pathlib import Path

import streamlit as st

from road_safety.analytics import filter_bundle
from road_safety.data import DEFAULT_SOURCE, load_data
from road_safety.ui import DashboardContext, methodology, render_filters, render_header

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='RoadLens · Great Britain 2024',page_icon=':material/route:',layout='wide')
st.html((ROOT / 'road_safety/assets/theme.css').read_text(encoding='utf-8').join(['<style>','</style>']))

pages=[st.Page('views/overview.py',title='Tổng quan',icon=':material/dashboard:',default=True),
       st.Page('views/temporal.py',title='Thời gian',icon=':material/schedule:',url_path='thoi-gian'),
       st.Page('views/spatial.py',title='Không gian',icon=':material/map:',url_path='khong-gian'),
       st.Page('views/severity.py',title='Mức độ nghiêm trọng',icon=':material/health_and_safety:',url_path='muc-do'),
       st.Page('views/people_vehicles.py',title='Người & phương tiện',icon=':material/groups:',url_path='nguoi-phuong-tien'),
       st.Page('views/conditions.py',title='Điều kiện xảy ra',icon=':material/cloud:',url_path='dieu-kien')]
current=st.navigation(pages,position='hidden')
with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">↗</div><div><div class="brand-name">RoadLens</div><div class="brand-sub">GREAT BRITAIN · 2024</div></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">PHÂN TÍCH</div>',unsafe_allow_html=True)
    for page in pages:
        st.page_link(page)
    st.divider()

source=Path(os.environ.get('ROADLENS_DATA',str(DEFAULT_SOURCE)))
try:
    stat=source.stat()
    with st.spinner('Đang chuẩn bị dữ liệu Great Britain 2024…'):
        data=load_data(source,stat.st_mtime_ns,stat.st_size)
except (OSError,ValueError) as error:
    st.error(f'Không thể nạp dữ liệu: {error}')
    st.caption('Đặt CSV đã chuẩn bị cạnh app.py. Xem README để cấu hình vị trí khác.')
    st.stop()

with st.sidebar:
    filters=render_filters(data)
if filters is None:
    st.info('Chọn đủ ngày bắt đầu và ngày kết thúc để xem kết quả.')
    st.stop()
context=DashboardContext(filter_bundle(data,filters),filters,source)
st.session_state['_dashboard_context']=context
render_header(context)
if context.data.collisions.empty:
    st.info('Không có dữ liệu phù hợp với bộ lọc. Hãy thay đổi lựa chọn hoặc đặt lại bộ lọc bên trái.')
else:
    current.run()
st.divider()
methodology()
