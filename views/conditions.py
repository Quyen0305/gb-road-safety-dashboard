import streamlit as st

from road_safety.analytics import count_by, severity_by
from road_safety.charts import bar_chart, severity_chart
from road_safety.labels import CONDITIONS
from road_safety.ui import get_context, page_intro, show_chart

ctx=get_context(); c=ctx.data.collisions
page_intro('Điều kiện xảy ra','Quan sát số vụ và mức độ nghiêm trọng trong từng điều kiện đường sá và môi trường.')
field=st.selectbox('Điều kiện phân tích',list(CONDITIONS),format_func=lambda x:CONDITIONS[x],key='condition')
label=field+'_label'
counts=count_by(c,label)
severity=severity_by(c,label)
left,right=st.columns([1.1,1.3])
with left,st.container(border=True):
    fig=bar_chart(counts,'count','group',f'Số vụ theo {CONDITIONS[field].lower()}',True)
    fig.update_layout(height=410)
    show_chart(fig,counts,'condition_counts')
with right,st.container(border=True):
    fig=severity_chart(severity,True)
    fig.update_layout(height=410)
    fig.update_xaxes(tickangle=-25)
    show_chart(fig,severity,'condition_severity')
st.caption('Tỷ trọng tính trên tổng số vụ của từng điều kiện sau bộ lọc. Hover hoặc mở bảng để xem số quan sát; nhóm chưa xác định được giữ nguyên.')
if field=='speed_limit':
    st.info('Giới hạn tốc độ được ghi theo mph; đây là giới hạn của đường, không phải tốc độ thực tế của xe.',icon=':material/speed:')
else:
    st.info('Những so sánh này mô tả mối liên hệ trong dữ liệu. Chưa có số chuyến đi hoặc lưu lượng tương ứng để kết luận điều kiện nào gây rủi ro cao hơn.',icon=':material/info:')
