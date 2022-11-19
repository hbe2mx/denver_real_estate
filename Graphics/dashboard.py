import dash
from dash import dcc, html, dash_table
import pandas as pd
import numpy as np
import sqlite3
exec(open('ETL\\config.py').read())

### Gather Dataframe
cursor = sqlite3.connect("denver_real_estate.db")
df = pd.read_sql_query(
    f'''
        SELECT *
        FROM denver_active_listings
    ''', cursor)
cursor.close()

cols = ['address', 'addressCity', 'county', 'zip', 'beds',
        'baths', 'area', 'unformattedPrice', 'average_home_value',
        'date_stamp']
app = dash.Dash(__name__)

### App Layout

app.layout = dash_table.DataTable(
    columns=[
        {'name': 'date_stamp', 'id': 'date_stamp', 'type': 'datetime'},
        {'name': 'Address', 'id': 'address', 'type': 'text'},
        {'name': 'City', 'id': 'addressCity', 'type': 'text'},
        {'name': 'County', 'id': 'county', 'type': 'text'},
        {'name': 'Zip', 'id': 'zip', 'type': 'text'},
        {'name': 'Beds', 'id': 'beds', 'type': 'text'},
        {'name': 'Baths', 'id': 'baths', 'type': 'text'},
        {'name': 'Area', 'id': 'area', 'type': 'text'},
        {'name': 'Price', 'id': 'unformattedPrice', 'type': 'numeric'},
        {'name': 'Avg_Home_Value', 'id': 'average_home_value', 'type': 'numeric'} 
    ],
    data=df.to_dict('records'),
    filter_action='native',

    style_table={
        'height': 400,
    },
    style_data={
        'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    }
)

### Open Connection to Dashboard
if __name__ == "__main__":
    app.run_server(debug=True)