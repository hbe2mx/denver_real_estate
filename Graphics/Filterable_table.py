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
        SELECT original.*, pred.predictions_price AS model_predicted_price, pred2.predictions AS rank
        FROM denver_active_listings AS original
        LEFT JOIN denver_prediction_values_price AS pred
        ON original.address = pred.address
        LEFT JOIN denver_prediction_values AS pred2
        ON original.address = pred2.address
    ''', cursor)
cursor.close()

cols = ['address', 'addressCity', 'county', 'zip', 'beds', 'rank',
        'baths', 'area', 'unformattedPrice', 'model_predicted_price',
        'date_stamp']

df = df[cols]

df['price_difference'] = [float(i) for i in df['unformattedPrice']] - df['model_predicted_price']

df = df.sort_values('price_difference')

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
        {'name': 'Model_Predicted_Price', 'id': 'model_predicted_price', 'type': 'numeric'},
        {'name': 'Price_Difference', 'id': 'price_difference', 'type': 'numeric'},
        {'name': 'Rank', 'id': 'rank', 'type': 'numeric'}
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