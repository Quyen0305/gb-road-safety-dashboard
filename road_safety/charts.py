import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from .analytics import map_cells
from .labels import SEVERITY_COLORS, WEEKDAYS

BLUE = '#2563EB'
PALETTE = ['#2563EB', '#0F9F92', '#F59E0B', '#7C6FE6', '#E05D6F']
TEXT = '#172033'
MUTED = '#64748B'
GRID = '#E8EDF3'
FONT = 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'


def polish(fig: go.Figure, title: str, height: int = 320) -> go.Figure:
    fig.update_layout(title=dict(text=title, font=dict(size=17, color=TEXT, weight=600), x=0, xanchor='left'),
                      height=height, margin=dict(l=16,r=22,t=58,b=46),
                      paper_bgcolor='white', plot_bgcolor='white', font=dict(family=FONT,size=13,color=MUTED),
                      separators=',.', hoverlabel=dict(bgcolor='white',bordercolor='#CBD5E1',font_size=13,font_family=FONT,font_color=TEXT),
                      legend=dict(orientation='h',y=-.22,x=0,title_text='',font_size=12),
                      hovermode='closest')
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor='#CBD5E1', title_font_size=12, tickfont_size=12, tickfont_color=MUTED)
    fig.update_yaxes(gridcolor=GRID, gridwidth=1, zeroline=False, linecolor='#CBD5E1', title_font_size=12, tickfont_size=12, tickfont_color=MUTED)
    return fig


def line_chart(table: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = go.Figure(go.Scatter(x=table[x], y=table[y], mode='lines+markers',
                               line=dict(color=BLUE,width=3), marker=dict(size=7,color='white',line=dict(color=BLUE,width=2.5)),
                               fill='tozeroy', fillcolor='rgba(37,99,235,.08)',
                               hovertemplate='%{x}<br>%{y:,.0f} vụ<extra></extra>'))
    polish(fig,title)
    fig.update_yaxes(title_text='Số vụ', rangemode='tozero')
    return fig


def bar_chart(table: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False,
              show_values: bool = False) -> go.Figure:
    fig = px.bar(table, x=x, y=y, orientation='h' if horizontal else 'v',
                 color_discrete_sequence=[BLUE])
    polish(fig,title)
    if horizontal:
        fig.update_yaxes(autorange='reversed',title_text=None,showgrid=False)
        fig.update_xaxes(title_text='Số vụ',showgrid=True,gridcolor=GRID,rangemode='tozero')
        fig.update_traces(hovertemplate='%{y}<br>%{x:,.0f}<extra></extra>')
        if show_values:
            fig.update_traces(texttemplate='%{x:,.0f}',textposition='outside',cliponaxis=False,
                              textfont=dict(size=12,color=TEXT))
            maximum=pd.to_numeric(table[x],errors='coerce').max()
            if pd.notna(maximum) and maximum > 0:
                fig.update_xaxes(range=[0,float(maximum)*1.16])
    else:
        fig.update_xaxes(title_text=None)
        fig.update_yaxes(title_text='Số vụ',rangemode='tozero')
        fig.update_traces(hovertemplate='%{x}<br>%{y:,.2f}<extra></extra>')
    return fig


def severity_chart(table: pd.DataFrame, percentage: bool, show_totals: bool = False) -> go.Figure:
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
    elif show_totals and not table.empty:
        totals=table[['group','group_total']].drop_duplicates('group')
        for row in totals.to_dict('records'):
            fig.add_annotation(x=row['group'],y=row['group_total'],text=f"{int(row['group_total']):,}".replace(',','.'),
                               showarrow=False,yshift=12,font=dict(size=12,color=TEXT),bgcolor='rgba(255,255,255,.82)')
        maximum=totals.group_total.max()
        if pd.notna(maximum) and maximum > 0:
            fig.update_yaxes(range=[0,float(maximum)*1.14])
    return fig


def donut_chart(table: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure(go.Pie(labels=table.group, values=table['count'], hole=.7,sort=False,
                           marker=dict(colors=[SEVERITY_COLORS.get(g,'#94a3b8') for g in table.group],line=dict(color='white',width=3)),
                           textinfo='percent', textposition='outside',textfont=dict(size=13,color=TEXT),
                           hovertemplate='%{label}<br>%{value:,.0f} vụ · %{percent}<extra></extra>'))
    polish(fig,title)
    fig.update_layout(annotations=[dict(text=f'<b>{int(table["count"].sum()):,}</b><br>vụ tai nạn'.replace(',','.'),
                                        x=.5,y=.5,showarrow=False,font=dict(size=17,color=TEXT))],
                      margin=dict(l=24,r=24,t=58,b=52))
    return fig


def heatmap_chart(table: pd.DataFrame) -> go.Figure:
    fig=go.Figure(go.Heatmap(z=table.values,x=list(range(24)),y=WEEKDAYS,
                            colorscale=[[0,'#EFF6FF'],[.45,'#93C5FD'],[1,'#1D4ED8']],
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
                              'style':{'backgroundColor':TEXT,'color':'white','fontFamily':FONT}},height=560)
