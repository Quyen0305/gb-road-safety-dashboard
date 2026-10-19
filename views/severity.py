import plotly.express as px
import streamlit as st

from road_safety.analytics import count_by, severity_by
from road_safety.charts import donut_chart, polish, severity_chart
from road_safety.labels import SEVERITIES
from road_safety.ui import get_context, page_intro, show_chart

ctx=get_context(); c=ctx.data.collisions
page_intro('Mức độ nghiêm trọng','Phân biệt quy mô số vụ với tỷ trọng vụ có tử vong hoặc nghiêm trọng.')
left,right=st.columns([1,1.6])
with left,st.container(border=True):
    counts=count_by(c,'severity_label',list(SEVERITIES.values()))
    show_chart(donut_chart(counts,'Cơ cấu mức độ — đơn vị: vụ'),counts,'severity_total')
with right,st.container(border=True):
    dimension=st.radio('Phân bố theo',['Tháng','Giờ'],horizontal=True,key='severity_time')
    field='month' if dimension=='Tháng' else 'hour'
    table=severity_by(c[c[field].notna()],field).sort_values('group',kind='stable')
    table['group']=table.group.map(lambda x:f'T{int(x)}' if field=='month' else f'{int(x):02d}h')
    show_chart(severity_chart(table,True),table,'severity_time')
    st.caption(f'Mẫu số: toàn bộ vụ trong từng {dimension.lower()} sau bộ lọc. Số quan sát hiện trong tooltip và bảng. {int(c[field].isna().sum())} vụ thiếu {dimension.lower()}.')
with st.container(border=True):
    group=st.selectbox('So sánh khu vực',['country','urban_or_rural_area_label','police_force_label'],
                       format_func=lambda x:{'country':'Quốc gia','urban_or_rural_area_label':'Đô thị / nông thôn','police_force_label':'Khu vực cảnh sát'}[x],key='severity_region')
    table=count_by(c,group)
    serious=c[c.collision_severity.isin([1,2])].groupby(group).size()
    table['serious_share']=table.group.map(serious).fillna(0)/table['count']*100
    fig=px.scatter(table,x='count',y='serious_share',hover_name='group',size='count',size_max=42,
                    text='group' if len(table)<=5 else None,color_discrete_sequence=['#eea34a'])
    polish(fig,'Quy mô và tỷ trọng vụ tử vong / nghiêm trọng',360)
    fig.update_traces(textposition='top center',hovertemplate='<b>%{hovertext}</b><br>%{x:,.0f} vụ<br>%{y:.1f}% tử vong / nghiêm trọng<extra></extra>')
    fig.update_xaxes(title_text='Tổng số vụ trong khu vực',rangemode='tozero')
    fig.update_yaxes(title_text='Tỷ trọng vụ tử vong / nghiêm trọng (%)',range=[0,min(105,max(10,table.serious_share.max()*1.25))])
    show_chart(fig,table,'severity_regions')
    st.caption('Tỷ trọng = số vụ có mức độ tử vong hoặc nghiêm trọng / tổng số vụ trong khu vực sau bộ lọc. Tỷ trọng ở nhóm ít quan sát cần được đọc cùng số vụ.')
