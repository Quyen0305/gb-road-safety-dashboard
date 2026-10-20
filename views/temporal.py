import streamlit as st

from road_safety.analytics import count_by, day_type_summary, time_heatmap
from road_safety.charts import bar_chart, heatmap_chart, line_chart
from road_safety.labels import WEEKDAYS
from road_safety.ui import get_context, page_intro, show_chart

ctx=get_context(); c=ctx.data.collisions
page_intro('Thời gian','Tai nạn tập trung vào tháng nào, giờ nào và những ngày nào trong tuần?')
months=count_by(c,'month',list(range(ctx.filters.start.month,ctx.filters.end.month+1)))
months['group']=months.group.map(lambda m:f'T{m}')
hours=count_by(c[c.hour.notna()],'hour',list(range(24)))
left,right=st.columns(2,gap='medium')
with left,st.container(border=True):
    show_chart(line_chart(months,'group','count','Số vụ theo tháng'),months,'time_months')
with right,st.container(border=True):
    fig=bar_chart(hours,'group','count','Số vụ theo giờ trong ngày')
    fig.update_xaxes(title_text='Giờ',dtick=3)
    show_chart(fig,hours,'time_hours')
left,right=st.columns([1.65,1],gap='medium')
with left,st.container(border=True):
    heat=time_heatmap(c)
    exported=heat.rename(index=dict(enumerate(WEEKDAYS)),columns=lambda hour:f'{hour:02d}:00').rename_axis('Thứ').reset_index()
    show_chart(heatmap_chart(heat),exported,'time_heatmap')
    st.caption(f'{int(c.hour.isna().sum())} vụ thiếu giờ, không hiển thị trên hai biểu đồ theo giờ.')
with right,st.container(border=True):
    mode=st.radio('Thước đo',['Bình quân / ngày','Tổng số vụ'],horizontal=True,key='day_measure')
    days=day_type_summary(c,ctx.filters.start,ctx.filters.end)
    fig=bar_chart(days,'day_type','per_day' if mode=='Bình quân / ngày' else 'collisions','Ngày thường và cuối tuần')
    fig.update_yaxes(title_text='Vụ / ngày' if mode=='Bình quân / ngày' else 'Số vụ')
    show_chart(fig,days,'time_daytype')
    st.caption('Bình quân tính trên mọi ngày lịch trong khoảng chọn, kể cả ngày không có vụ. Không có ngày thuộc nhóm: để trống.')
