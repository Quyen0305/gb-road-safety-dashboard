import streamlit as st

from road_safety.analytics import count_by, severity_by
from road_safety.charts import bar_chart, donut_chart, line_chart, severity_chart
from road_safety.labels import SEVERITIES
from road_safety.ui import get_context, number, page_intro, show_chart

ctx=get_context(); c=ctx.data.collisions
page_intro('Tổng quan','Bức tranh chung về thời gian, không gian và mức độ nghiêm trọng của tai nạn.')
months=count_by(c,'month',list(range(ctx.filters.start.month,ctx.filters.end.month+1)))
months['group']=months.group.map(lambda m:f'T{m}')
severity=count_by(c,'severity_label',list(SEVERITIES.values()))
countries=count_by(c,'country')
urban=severity_by(c,'urban_or_rural_area_label')
left,right=st.columns([1.7,1],gap='medium')
with left,st.container(border=True):
    show_chart(line_chart(months,'group','count','Xu hướng số vụ theo tháng'),months,'overview_months')
with right,st.container(border=True):
    show_chart(donut_chart(severity,'Cơ cấu mức độ của vụ tai nạn'),severity,'overview_severity')
left,right=st.columns(2,gap='medium')
with left,st.container(border=True):
    show_chart(bar_chart(countries,'count','group','Tai nạn theo quốc gia',True),countries,'overview_countries')
with right,st.container(border=True):
    figure=severity_chart(urban,False)
    figure.update_layout(title_text='Tai nạn tại đô thị và nông thôn')
    show_chart(figure,urban,'overview_urban')
peak=months[months['count'].eq(months['count'].max())]
top=countries[countries['count'].eq(countries['count'].max())]
st.info(f"Trong phạm vi đang chọn, {', '.join(peak.group)} có số vụ cao nhất ({number(int(peak['count'].max()))} vụ). "
        f"Quốc gia có số vụ cao nhất: {', '.join(top.group)} ({number(int(top['count'].max()))} vụ).",icon=':material/lightbulb:')
