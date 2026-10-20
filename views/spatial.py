import streamlit as st

from road_safety.analytics import count_by, map_cells, severity_by
from road_safety.charts import bar_chart, collision_map, severity_chart
from road_safety.ui import get_context, number, page_intro, render_table_download, show_chart

ctx=get_context(); c=ctx.data.collisions
page_intro('Không gian','Khám phá phân bố vị trí tai nạn và quy mô ghi nhận tại các khu vực.')
with st.container(border=True):
    left,right=st.columns([2,1],gap='medium')
    with left:
        mode=st.radio('Lớp dữ liệu',['Mật độ theo ô','Điểm theo mức độ'],horizontal=True,key='map_mode')
    with right:
        online=st.toggle('Nền đường trực tuyến',value=False,key='map_online',help='Cần kết nối Internet đến CARTO. Tắt để dùng đường bờ được lưu tại máy.')
    st.pydeck_chart(collision_map(c,mode,online=online),height=560,key='collision_map')
    valid=int(c.valid_coordinates.sum())
    st.caption(f'Hiển thị {number(valid)} / {number(len(c))} vụ · {number(len(c)-valid)} vụ có tọa độ thiếu hoặc ngoài vùng kiểm tra. Không lấy mẫu dữ liệu.')
    if mode=='Mật độ theo ô':
        st.caption('Kích thước vòng tròn biểu thị số vụ trong ô 0,08°; không phải số vụ trên km².')
    else:
        st.caption('🔴 Có tử vong · 🟠 Nghiêm trọng · 🔵 Nhẹ. Các điểm có thể chồng lên nhau; phóng to để xem chi tiết.')
    if online:
        st.caption('Nền đường: CARTO / OpenStreetMap, cần mạng. Nếu nền không tải, tắt công tắc để dùng đường bờ ngoại tuyến.')
    else:
        st.caption('Đường bờ đơn giản lưu tại máy · Natural Earth. Dùng chuột để phóng to và di chuyển bản đồ.')
    render_table_download(map_cells(c,.08),'spatial_cells')
left,right=st.columns([1.3,1],gap='medium')
with left,st.container(border=True):
    areas=count_by(c,'police_force_label')
    fig=bar_chart(areas.head(10),'count','group','10 khu vực cảnh sát có nhiều vụ nhất',True)
    fig.update_layout(height=380)
    show_chart(fig,areas,'spatial_police')
with right,st.container(border=True):
    urban=severity_by(c,'urban_or_rural_area_label')
    fig=severity_chart(urban,False)
    fig.update_layout(title_text='Đô thị và nông thôn',height=380)
    show_chart(fig,urban,'spatial_urban')
