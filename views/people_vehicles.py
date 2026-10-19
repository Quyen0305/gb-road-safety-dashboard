import streamlit as st

from road_safety.analytics import count_by
from road_safety.charts import bar_chart
from road_safety.labels import AGE_GROUPS
from road_safety.ui import get_context, page_intro, show_chart

ctx=get_context(); people=ctx.data.casualties; vehicles=ctx.data.vehicles
page_intro('Người & phương tiện','Các biểu đồ về người đếm thương vong; biểu đồ phương tiện đếm xe liên quan tới những vụ đã chọn.')
if people.empty:
    st.info('Không có bản ghi thương vong trong các vụ đã chọn.')
else:
    left,right=st.columns(2)
    with left,st.container(border=True):
        ages=count_by(people,'age_group',AGE_GROUPS)
        fig=bar_chart(ages,'group','count','Thương vong theo nhóm tuổi')
        fig.update_yaxes(title_text='Số người')
        show_chart(fig,ages,'people_age')
    with right,st.container(border=True):
        sexes=count_by(people,'sex_of_casualty_label')
        fig=bar_chart(sexes,'group','count','Thương vong theo giới tính ghi nhận')
        fig.update_yaxes(title_text='Số người')
        show_chart(fig,sexes,'people_sex')
left,right=st.columns(2)
with left,st.container(border=True):
    roles=count_by(people,'casualty_class_label')
    fig=bar_chart(roles,'count','group','Vai trò của người thương vong',True)
    fig.update_xaxes(title_text='Số người')
    show_chart(fig,roles,'people_roles')
with right,st.container(border=True):
    types=count_by(vehicles,'vehicle_type_label')
    fig=bar_chart(types,'count','group','Phương tiện liên quan theo loại',True)
    fig.update_layout(height=max(300,len(types)*25+85))
    fig.update_xaxes(title_text='Số phương tiện')
    show_chart(fig,types,'vehicle_types')
st.caption('Nhóm tuổi không xác định vẫn được giữ. Mỗi phương tiện được đếm một lần trong một vụ, dù có nhiều người thương vong trên phương tiện đó.')
