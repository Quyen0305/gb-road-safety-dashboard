import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from .analytics import map_cells
from .labels import SEVERITY_COLORS, WEEKDAYS

BLUE = '#3778e9'
PALETTE = ['#3778e9', '#69bdb5', '#eebc69', '#8f91d9', '#e88d95']


def polish(fig: go.Figure, title: str, height: int = 300) -> go.Figure:
    fig.update_layout(title=dict(text=title, font=dict(size=14, color='#26364e'), x=0),
                      height=height, margin=dict(l=12,r=15,t=49,b=36),
                      paper_bgcolor='white', plot_bgcolor='white', font=dict(family='Arial, sans-serif',size=12,color='#758399'),
                      separators=',.', hoverlabel=dict(bgcolor='white',font_size=13),
                      legend=dict(orientation='h',y=-.2,x=0,title_text='',font_size=11),
                      hovermode='closest')
    fig.update_xaxes(showgrid=False, zeroline=False, title_font_size=11, tickfont_size=11)
    fig.update_yaxes(gridcolor='#edf1f6', zeroline=False, title_font_size=11, tickfont_size=11)
    return fig


def line_chart(table: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = go.Figure(go.Scatter(x=table[x], y=table[y], mode='lines+markers',
                               line=dict(color=BLUE,width=2.6), marker=dict(size=6),
                               fill='tozeroy', fillcolor='rgba(55,120,233,.07)',
                               hovertemplate='%{x}<br>%{y:,.0f} vụ<extra></extra>'))
    polish(fig,title)
    fig.update_yaxes(title_text='Số vụ', rangemode='tozero')
    return fig


def bar_chart(table: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False) -> go.Figure:
    fig = px.bar(table, x=x, y=y, orientation='h' if horizontal else 'v',
                 color_discrete_sequence=[BLUE])
    polish(fig,title)
    if horizontal:
        fig.update_yaxes(autorange='reversed',title_text=None,showgrid=False)
        fig.update_xaxes(title_text='Số vụ',showgrid=True,gridcolor='#edf1f6',rangemode='tozero')
        fig.update_traces(hovertemplate='%{y}<br>%{x:,.0f}<extra></extra>')
    else:
        fig.update_xaxes(title_text=None)
        fig.update_yaxes(title_text='Số vụ',rangemode='tozero')
        fig.update_traces(hovertemplate='%{x}<br>%{y:,.2f}<extra></extra>')
    return fig


def severity_chart(table: pd.DataFrame, percentage: bool) -> go.Figure:
    fig = px.bar(table, x='group', y='percentage' if percentage else 'count', color='severity',
                 color_discrete_map=SEVERITY_COLORS,
                 category_orders={'severity':list(SEVERITY_COLORS),'group':table.group.drop_duplicates().tolist()},
                 custom_data=['count','group_total','percentage'])
    polish(fig, 'Tỷ trọng mức độ nghiêm trọng' if percentage else 'Số vụ theo mức độ nghiêm trọng')
    fig.update_layout(barmode='stack')
    fig.update_traces(hovertemplate='%{x}<br>%{customdata[0]:,.0f} / %{customdata[1]:,.0f} vụ<br>%{customdata[2]:.1f}%<extra>%{fullData.name}</extra>')
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text='Tỷ trọng (%)' if percentage else 'Số vụ', rangemode='tozero')
    if percentage:
        fig.update_yaxes(range=[0,100],ticksuffix='%')
    return fig


def donut_chart(table: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure(go.Pie(labels=table.group, values=table['count'], hole=.7,sort=False,
                           marker=dict(colors=[SEVERITY_COLORS.get(g,'#94a3b8') for g in table.group],line=dict(color='white',width=3)),
                           textinfo='percent', textposition='outside',textfont_size=11,
                           hovertemplate='%{label}<br>%{value:,.0f} vụ · %{percent}<extra></extra>'))
    polish(fig,title)
    fig.update_layout(annotations=[dict(text=f'<b>{int(table["count"].sum()):,}</b><br>vụ tai nạn'.replace(',','.'),
                                        x=.5,y=.5,showarrow=False,font=dict(size=16,color='#26364e'))],
                      margin=dict(l=18,r=18,t=46,b=40))
    return fig


def heatmap_chart(table: pd.DataFrame) -> go.Figure:
    fig=go.Figure(go.Heatmap(z=table.values,x=list(range(24)),y=WEEKDAYS,
                            colorscale=[[0,'#edf3ff'],[.45,'#8eb5f7'],[1,'#2456b2']],
                            colorbar=dict(title='Vụ',thickness=10),
                            hovertemplate='%{y}, %{x}:00<br>%{z:,.0f} vụ<extra></extra>'))
    polish(fig,'Phân bố theo thứ và giờ',340)
    fig.update_yaxes(autorange='reversed',showgrid=False)
    fig.update_xaxes(title_text='Giờ trong ngày',dtick=2)
    return fig


def collision_map(collisions: pd.DataFrame, mode: str, online: bool = False) -> pdk.Deck:
    geometry = json.loads((Path(__file__).parent / 'assets/gb-ireland.geojson').read_text(encoding='utf-8'))
    land = pdk.Layer('GeoJsonLayer', data=geometry, stroked=True, filled=True,
                     get_fill_color=[235,240,245,255],get_line_color=[166,181,199,255],line_width_min_pixels=1)
    if mode == 'Mật độ theo ô':
        points = map_cells(collisions, .08).groupby(['longitude','latitude'],as_index=False)['count'].sum()
        points['description'] = 'Tất cả mức độ trong ô 0,08°'
        points['color'] = [[55,120,233,170]] * len(points)
        points['radius'] = np.sqrt(points['count']).clip(2,35) * 300
    else:
        points = collisions.loc[collisions.valid_coordinates].sort_values('collision_severity',ascending=False)[
            ['longitude','latitude','severity_label']].copy()
        points['count'] = 1
        points['description'] = points.severity_label
        def rgba(label):
            color = SEVERITY_COLORS.get(label,'#94a3b8').lstrip('#')
            return [int(color[i:i+2],16) for i in (0,2,4)] + [180]
        points['color'] = points.severity_label.map(rgba)
        points['radius'] = 180
    dots = pdk.Layer('ScatterplotLayer',data=points.to_dict('records'),get_position='[longitude, latitude]',
                     get_radius='radius',get_fill_color='color',radius_min_pixels=2,
                     radius_max_pixels=25,pickable=True,stroked=False)
    # Omit map_style for the offline mode: None asks Streamlit for its online
    # theme, while Pydeck's default with map_provider=None disables the basemap.
    basemap={'map_provider':'carto','map_style':'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json'} if online else {'map_provider':None}
    return pdk.Deck(layers=[dots] if online else [land,dots], initial_view_state=pdk.ViewState(latitude=54.9,longitude=-3.2,zoom=4.7,pitch=0),
                     **basemap,
                     tooltip={'html':'<b>{count} vụ</b><br>{description}',
                              'style':{'backgroundColor':'#17263d','color':'white'}},height=560)
