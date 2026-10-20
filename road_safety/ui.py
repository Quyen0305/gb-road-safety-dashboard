from dataclasses import dataclass
from datetime import date
from pathlib import Path
import html

import pandas as pd
import streamlit as st

from .analytics import FilterSpec, csv_bytes, headline_metrics
from .data import DataBundle
from .labels import category_label


@dataclass
class DashboardContext:
    data: DataBundle
    filters: FilterSpec
    source_path: Path


def get_context() -> DashboardContext:
    return st.session_state['_dashboard_context']


def number(value: int) -> str:
    return f'{value:,}'.replace(',','.')


def render_filters(bundle: DataBundle) -> FilterSpec | None:
    c = bundle.collisions
    start, end = c.date.min().date(), c.date.max().date()
    defaults = dict(f_dates=(start,end), f_quick='Cả năm', f_country=sorted(c.country.unique()),
                     f_severity=sorted(c.collision_severity.unique().tolist()),
                     f_urban=sorted(c.urban_or_rural_area.unique().tolist()),
                     f_police=sorted(c.police_force.unique().tolist()))
    for key,value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    def reset():
        for key,value in defaults.items():
            st.session_state[key] = value

    def quick_dates():
        selected=st.session_state.f_quick
        if selected == 'Cả năm':
            st.session_state.f_dates=(start,end)
        elif selected.startswith('Quý'):
            q=int(selected[-1]); month=3*q-2
            lo=date(start.year,month,1)
            hi=(pd.Timestamp(lo)+pd.offsets.QuarterEnd()).date()
            if hi < start or lo > end:
                st.session_state.f_dates=(start,end)
                st.session_state.f_quick='Cả năm'
            else:
                st.session_state.f_dates=(max(start,lo),min(end,hi))

    def custom_dates():
        st.session_state.f_quick='Tùy chỉnh'

    st.markdown('<div class="eyebrow">BỘ LỌC DỮ LIỆU</div>',unsafe_allow_html=True)
    st.selectbox('Chọn nhanh thời gian',['Cả năm','Quý 1','Quý 2','Quý 3','Quý 4','Tùy chỉnh'],key='f_quick',on_change=quick_dates)
    selected_dates=st.date_input('Khoảng ngày',key='f_dates',min_value=start,max_value=end,format='DD/MM/YYYY',on_change=custom_dates)
    countries=st.multiselect('Quốc gia',defaults['f_country'],key='f_country')
    severities=st.multiselect('Mức độ của vụ tai nạn',defaults['f_severity'],key='f_severity',format_func=lambda code:category_label('collision_severity',code))
    urban=st.multiselect('Đô thị / nông thôn',defaults['f_urban'],key='f_urban',format_func=lambda code:category_label('urban_or_rural_area',code))
    with st.expander('Lọc chi tiết'):
        police=st.multiselect('Khu vực cảnh sát',defaults['f_police'],key='f_police',format_func=lambda code:category_label('police_force',code))
    st.button('Đặt lại bộ lọc',key='reset_filters',on_click=reset,width='stretch',icon=':material/restart_alt:')
    st.caption('Bộ lọc áp dụng theo vụ tai nạn và giữ nguyên khi chuyển trang.')
    st.caption('Nguồn: DfT · STATS19 · 2024')
    if len(selected_dates) != 2:
        return None
    return FilterSpec(*selected_dates,tuple(countries),tuple(severities),tuple(urban),tuple(police))


def render_header(context: DashboardContext) -> None:
    f=context.filters
    countries=', '.join(f.countries) if f.countries else 'Chưa chọn quốc gia'
    subtitle=f'{f.start:%d/%m/%Y} — {f.end:%d/%m/%Y} · {countries}'
    st.markdown(
                '<h1 class="hero-title">Tai nạn giao thông tại Great Britain</h1>'
                f'<div class="hero-sub">{html.escape(subtitle)}</div>',unsafe_allow_html=True)
    metrics=headline_metrics(context.data)
    labels=[('collisions','Vụ tai nạn','Số vụ duy nhất sau khi lọc.'),
            ('casualties','Người thương vong','Tổng số người bị thương hoặc tử vong.'),
            ('fatalities','Người tử vong','Số người tử vong, khác số vụ có tử vong.'),
            ('vehicles','Phương tiện liên quan','Mỗi phương tiện trong một vụ được đếm một lần.')]
    with st.container(key='headline_metrics'):
        for column,(key,label,help_text) in zip(st.columns(4,gap='medium'),labels):
            column.metric(label,number(metrics[key]),help=help_text)


def page_intro(title: str, subtitle: str) -> None:
    st.subheader(title)
    st.caption(subtitle)


def render_table_download(table: pd.DataFrame, name: str) -> None:
    names={'group':'Nhóm','count':'Số lượng','severity':'Mức độ vụ','group_total':'Tổng số vụ của nhóm',
           'percentage':'Tỷ trọng (%)','month':'Tháng','day_type':'Loại ngày','collisions':'Số vụ',
           'calendar_days':'Số ngày lịch','per_day':'Bình quân vụ/ngày','longitude':'Kinh độ',
           'latitude':'Vĩ độ','severity_label':'Mức độ vụ','serious_share':'Tỷ trọng tử vong/nghiêm trọng (%)'}
    display=table.rename(columns=names)
    with st.expander('Bảng số liệu · Tải CSV'):
        st.dataframe(display,hide_index=True,width='stretch')
        st.download_button('Tải bảng CSV',data=csv_bytes(display),file_name=f'roadlens_{name}.csv',
                           mime='text/csv',key='download_'+name,icon=':material/download:')


def show_chart(figure, table: pd.DataFrame, name: str) -> None:
    st.plotly_chart(figure,width='stretch',config={'displayModeBar':False},key='chart_'+name)
    render_table_download(table,name)


def methodology() -> None:
    with st.expander('Nguồn dữ liệu & cách đọc dashboard',icon=':material/info:'):
        st.markdown('''Dữ liệu **Great Britain 2024** gồm các vụ tai nạn gây thương vong trên đường công cộng được cảnh sát ghi nhận, từ [DfT / STATS19](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data).

Mỗi vụ, phương tiện và người thương vong được đếm bằng khóa riêng để tránh lặp từ bảng ghép. Bộ lọc chung chọn **vụ tai nạn**, sau đó lấy người và phương tiện thuộc những vụ này. Số người tử vong có thể khác số vụ có tử vong.

Mức độ nghiêm trọng dùng **số ghi nhận gốc, chưa hiệu chỉnh**. Tỷ trọng = số vụ thuộc mức độ / toàn bộ số vụ của nhóm sau bộ lọc. Nhóm thiếu hoặc chưa xác định vẫn được giữ. Ngày thường/cuối tuần tính bình quân trên mọi ngày lịch trong khoảng chọn, kể cả ngày không có vụ.

Số vụ thể hiện quy mô ghi nhận; chưa có lưu lượng giao thông để tính rủi ro. Các mối liên hệ không chứng minh nguyên nhân. Giới hạn tốc độ (mph) là giới hạn của đường, không phải tốc độ xe khi xảy ra tai nạn. Dữ liệu chỉ có năm 2024 nên không so sánh với năm trước.

Bản đồ dùng tất cả vụ có tọa độ trong vùng kiểm tra −9°…3° kinh độ, 49°…61° vĩ độ. Lớp mật độ cộng số vụ theo ô 0,08°; diện tích ô thay đổi theo vĩ độ, không phải mật độ trên km². Đường bờ đơn giản từ Natural Earth (public domain); dữ liệu Great Britain không bao gồm Northern Ireland.''')
