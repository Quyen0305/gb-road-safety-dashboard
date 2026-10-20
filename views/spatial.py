import streamlit as st

from road_safety.analytics import count_by, locality_summary, map_cells, severity_by
from road_safety.charts import bar_chart, collision_map, severity_chart
from road_safety.geography import COUNTRY_COLORS, LOCALITY_COLOR_BINS, ZERO_COLOR, load_boundaries
from road_safety.ui import get_context, number, page_intro, render_table_download, show_chart

ctx=get_context(); c=ctx.data.collisions
page_intro('Không gian','Nhận biết địa phương có nhiều tai nạn và khám phá các vị trí cụ thể trên bản đồ.')
places=locality_summary(c)
with st.container(border=True):
    with st.container(key='map_toolbar'):
        layers,search,basemap,labels=st.columns([2.6,3.2,2.1,1.7],gap='small',vertical_alignment='bottom')
        with layers:
            mode=st.selectbox('Lớp dữ liệu',['Tô màu địa phương','Tô màu quốc gia','Theo địa phương','Mật độ theo ô','Điểm theo mức độ'],key='map_mode')
        with search:
            place_names=places.set_index('area_code')['group'].to_dict()
            focus=st.selectbox('Tìm thành phố / địa phương',[None,*places.area_code.tolist()],
                format_func=lambda code:'Toàn Great Britain' if code is None else f'{place_names[code]} ({code})',
                key='map_focus')
        with basemap:
            online=st.toggle('Nền đường trực tuyến',value=False,key='map_online',help='Cần kết nối Internet đến CARTO. Tắt để dùng đường bờ được lưu tại máy.')
        with labels:
            show_names=st.toggle('Hiện tên và số vụ',value=True,key='map_names')
    fill_level={'Tô màu địa phương':'locality','Tô màu quốc gia':'country'}.get(mode)
    if fill_level:
        items=([(name,color) for name,color in COUNTRY_COLORS.items()] if fill_level=='country'
               else [(label+' vụ',color) for _,label,color in LOCALITY_COLOR_BINS])
        items.append(('0 vụ sau bộ lọc',ZERO_COLOR))
        swatches=''.join(f'<span class="map-legend-item"><i style="background:rgb({color[0]},{color[1]},{color[2]})"></i>{label}</span>'
                        for label,color in items)
        st.markdown(f'<div class="map-legend">{swatches}</div>',unsafe_allow_html=True)
    st.pydeck_chart(collision_map(c,mode,online=online,places=places,show_names=show_names,focus_code=focus),height=560,key='collision_map')
    valid=int(c.valid_coordinates.sum())
    if fill_level:
        st.caption(f'Tổng hợp {number(len(c))} vụ theo mã hành chính, kể cả vụ thiếu tọa độ. Rê chuột lên vùng để xem tên và số vụ; số liệu cập nhật theo bộ lọc.')
        if fill_level=='locality':
            boundary_codes={feature['properties']['code'] for feature in load_boundaries('locality')['features']}
            missing=places.loc[~places.area_code.isin(boundary_codes)]
            if not missing.empty:
                located_missing=missing.dropna(subset=['longitude','latitude'])
                st.caption(f'{number(missing["count"].sum())} vụ thuộc địa phương chưa có ranh giới riêng (ví dụ Heathrow); '
                           f'{number(located_missing["count"].sum())} vụ được giữ bằng điểm màu tím. Bảng số liệu vẫn giữ đầy đủ.')
            st.caption('Màu đậm hơn là nhiều vụ hơn; các ngưỡng màu cố định khi đổi bộ lọc. Đây là số vụ, không phải tỷ lệ rủi ro hay mật độ trên km².')
        else:
            st.caption('Mỗi quốc gia có một màu riêng để phân biệt; màu không biểu thị thứ hạng. Nhãn hiển thị tên quốc gia và tổng số vụ, cùng địa phương đang tìm kiếm.')
        st.caption('Ranh giới ONS 2024 được lưu tại máy và giản lược để tải nhanh. © Crown copyright / OS / ONS · Open Government Licence v3.0.')
    else:
        st.caption(f'Hiển thị {number(valid)} / {number(len(c))} vụ · {number(len(c)-valid)} vụ có tọa độ thiếu hoặc ngoài vùng kiểm tra. Không lấy mẫu dữ liệu.')
    if fill_level!='country':
        st.caption('Nhãn hiển thị hạng, tên và số vụ của 10 địa phương nhiều vụ nhất; địa phương được tìm kiếm cũng có nhãn. Đường nối chỉ vị trí của nhãn được dịch ra để dễ đọc. Thứ hạng và số vụ cập nhật theo bộ lọc; phóng to nếu thu nhỏ làm nhãn sát nhau.')
    if mode=='Theo địa phương':
        st.caption('Vòng tròn lớn hơn thể hiện nhiều vụ hơn. Vị trí vòng tròn là trung bình tọa độ tai nạn hợp lệ của địa phương, không phải ranh giới hay tâm thành phố.')
    elif mode=='Mật độ theo ô':
        st.caption('Kích thước vòng tròn biểu thị số vụ trong ô 0,08°; không phải số vụ trên km².')
    elif mode=='Điểm theo mức độ':
        st.caption('🔴 Có tử vong · 🟠 Nghiêm trọng · 🔵 Nhẹ. Các điểm có thể chồng lên nhau; phóng to để xem chi tiết.')
    if online:
        st.caption('Nền đường: CARTO / OpenStreetMap, cần mạng. Nếu nền không tải, tắt công tắc để dùng đường bờ ngoại tuyến.')
    elif not fill_level:
        st.caption('Đường bờ đơn giản lưu tại máy · Natural Earth. Dùng chuột để phóng to và di chuyển bản đồ.')
    if fill_level=='country':
        render_table_download(count_by(c,'country'),'spatial_countries')
    elif mode=='Theo địa phương' or fill_level=='locality':
        render_table_download(places,'spatial_localities')
    else:
        render_table_download(map_cells(c,.08),'spatial_cells')
with st.container(border=True):
    fig=bar_chart(places.head(10),'count','group','10 địa phương có nhiều vụ tai nạn nhất',True,show_values=True)
    fig.update_layout(height=410)
    show_chart(fig,places,'spatial_ranking')
    st.caption('Tên tra từ bảng mã DfT 2024 (local_authority_ons_district). Đơn vị hành chính có thể bao gồm vùng ngoài thành phố; không quy số vụ của một tỉnh/huyện thành số vụ riêng của thành phố. Bảng đầy đủ giữ cả địa phương chưa có tọa độ hợp lệ.')
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
