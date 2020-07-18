# Load data from MySQL to perform exploratory data analysis
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import nltk
import re
import settings
import mysql.connector
import pandas as pd
import time
import itertools
import math

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
# %matplotlib inline
import plotly.express as px
import datetime
from IPython.display import clear_output

import plotly.offline as py
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# from datetime import datetime

# now = datetime.now()


# nltk.download('punkt')
# nltk.download('stopwords')

# Filter constants for states in US
# STATES = ['Alabama', 'AL', 'Alaska', 'AK', 'American Samoa', 'AS', 'Arizona', 'AZ', 'Arkansas',
#           'AR', 'California', 'CA', 'Colorado', 'CO', 'Connecticut', 'CT', 'Delaware', 'DE',
#           'District of Columbia', 'DC', 'Federated States of Micronesia', 'FM', 'Florida', 'FL', 'Georgia', 'GA', 'Guam', 'GU', 'Hawaii', 'HI', 'Idaho', 'ID', 'Illinois', 'IL', 'Indiana', 'IN', 'Iowa', 'IA', 'Kansas', 'KS', 'Kentucky', 'KY', 'Louisiana', 'LA', 'Maine', 'ME', 'Marshall Islands', 'MH', 'Maryland', 'MD', 'Massachusetts', 'MA', 'Michigan', 'MI', 'Minnesota', 'MN', 'Mississippi', 'MS', 'Missouri',
#           'MO', 'Montana', 'MT', 'Nebraska', 'NE', 'Nevada', 'NV', 'New Hampshire',
#           'NH', 'New Jersey', 'NJ', 'New Mexico', 'NM', 'New York', 'NY', 'North Carolina',
#           'NC', 'North Dakota', 'ND', 'Northern Mariana Islands', 'MP', 'Ohio', 'OH',
#           'Oklahoma', 'OK', 'Oregon', 'OR', 'Palau', 'PW', 'Pennsylvania', 'PA', 'Puerto Rico', 'PR', 'Rhode Island',
#           'RI', 'South Carolina', 'SC', 'South Dakota', 'SD', 'Tennessee', 'TN',
#           'Texas', 'TX', 'Utah', 'UT', 'Vermont', 'VT', 'Virgin Islands', 'VI',
#           'Virginia', 'VA', 'Washington', 'WA', 'West Virginia', 'WV', 'Wisconsin',
#           'WI', 'Wyoming', 'WY', 'India', 'Delhi', 'New Delhi', 'Bangalore',
#           'Delhi', 'Karnataka', 'Maharashtra', 'Gujrat', 'Tamilnadu', 'Assam', 'Bihar', 'Madhya Pradesh',
#           'Uttar Pradesh']

STATES = ['India', 'USA', 'US', 'China',
          'Germany', 'UK', 'Italy', 'Korea', 'America', 'India', 'Pakistan', 'China', 'Bangladesh',
          'Alabama', 'AL', 'Alaska', 'AK', 'American Samoa', 'AS', 'Arizona', 'AZ', 'Arkansas',
          'AR', 'California', 'CA', 'Colorado', 'CO', 'Connecticut', 'CT', 'Delaware', 'DE',
          'District of Columbia', 'DC', 'Federated States of Micronesia', 'FM', 'Florida', 'FL', 'Georgia', 'GA', 'Guam', 'GU', 'Hawaii', 'HI', 'Idaho', 'ID', 'Illinois', 'IL', 'Indiana', 'IN', 'Iowa', 'IA', 'Kansas', 'KS', 'Kentucky', 'KY', 'Louisiana', 'LA', 'Maine', 'ME', 'Marshall Islands', 'MH', 'Maryland', 'MD', 'Massachusetts', 'MA', 'Michigan', 'MI', 'Minnesota', 'MN', 'Mississippi', 'MS', 'Missouri',
          'MO', 'Montana', 'MT', 'Nebraska', 'NE', 'Nevada', 'NV', 'New Hampshire',
          'NH', 'New Jersey', 'NJ', 'New Mexico', 'NM', 'New York', 'NY', 'North Carolina',
          'NC', 'North Dakota', 'ND', 'Northern Mariana Islands', 'MP', 'Ohio', 'OH',
          'Oklahoma', 'OK', 'Oregon', 'OR', 'Palau', 'PW', 'Pennsylvania', 'PA', 'Puerto Rico', 'PR', 'Rhode Island',
          'RI', 'South Carolina', 'SC', 'South Dakota', 'SD', 'Tennessee', 'TN',
          'Texas', 'TX', 'Utah', 'UT', 'Vermont', 'VT', 'Virgin Islands', 'VI',
          'Virginia', 'VA', 'Washington', 'WA', 'West Virginia', 'WV', 'Wisconsin',
          'WI', 'Wyoming', 'WY', 'India', 'Delhi', 'New Delhi', 'Bangalore',
          'Delhi', 'Karnataka', 'Maharashtra', 'Gujrat', 'Tamilnadu', 'Assam', 'Bihar', 'Madhya Pradesh',
          'Uttar Pradesh']

STATE_DICT = dict(itertools.zip_longest(*[iter(STATES)] * 2, fillvalue=""))
INV_STATE_DICT = dict((v, k) for k, v in STATE_DICT.items())

'''
This complex plot shows the latest Twitter data within 20 mins and will automatically update.
'''
while True:
    clear_output()
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="twitterdb",
        charset='utf8'
    )
    # Load data from MySQL
    timenow = (datetime.datetime.utcnow() - datetime.timedelta(hours=0,
                                                               minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    query = "SELECT id_str, text, created_at, polarity, user_location FROM {} WHERE created_at >= '{}' " \
        .format(settings.TABLE_NAME, timenow)
    df = pd.read_sql(query, con=db_connection)
    # UTC for date time at default
    df['created_at'] = pd.to_datetime(df['created_at'])

    fig = make_subplots(
        rows=2, cols=2,
        column_widths=[1, 0.4],
        row_heights=[0.6, 0.4],
        specs=[[{"type": "scatter", "rowspan": 2}, {"type": "choropleth"}],
               [None, {"type": "bar"}]]
    )

    '''
    Plot the Line Chart
    '''
    # Clean and transform data to enable time series
    result = df.groupby([pd.Grouper(key='created_at', freq='2s'), 'polarity']).count(
    ).unstack(fill_value=0).stack().reset_index()
    result = result.rename(columns={"id_str": "Num of '{}' mentions".format(
        settings.TRACK_WORDS[0]), "created_at": "Time in UTC"})
    time_series = result["Time in UTC"][result['polarity']
                                        == 0].reset_index(drop=True)
    fig.add_trace(go.Scatter(
        x=time_series,
        y=result["Num of '{}' mentions".format(
            settings.TRACK_WORDS[0])][result['polarity'] == 0].reset_index(drop=True),
        name="Neural",
        opacity=0.8), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=time_series,
        y=result["Num of '{}' mentions".format(
            settings.TRACK_WORDS[0])][result['polarity'] == -1].reset_index(drop=True),
        name="Negative",
        opacity=0.8), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=time_series,
        y=result["Num of '{}' mentions".format(
            settings.TRACK_WORDS[0])][result['polarity'] == 1].reset_index(drop=True),
        name="Positive",
        opacity=0.8), row=1, col=1)

    '''
    Plot the Bar Chart
    '''
    content = ' '.join(df["text"])
    content = re.sub(r"http\S+", "", content)
    content = content.replace('RT ', ' ').replace('&amp;', 'and')
    content = re.sub('[^A-Za-z0-9]+', ' ', content)
    content = content.lower()

    tokenized_word = word_tokenize(content)
    stop_words = set(stopwords.words("english"))
    filtered_sent = []
    for w in tokenized_word:
        if w not in stop_words:
            filtered_sent.append(w)
    fdist = FreqDist(filtered_sent)
    fd = pd.DataFrame(fdist.most_common(10), columns=[
                      "Word", "Frequency"]).drop([0]).reindex()

    # Plot Bar chart
    fig.add_trace(
        go.Bar(x=fd["Word"], y=fd["Frequency"], name="Freq Dist"), row=2, col=2)
    # 59, 89, 152
    fig.update_traces(marker_color='rgb(59, 89, 152)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=0.5, opacity=0.7, row=2, col=2)

    '''
    Plot the Geo-Distribution
    '''
    is_in_US = []
    geo = df[['user_location']]
    df = df.fillna(" ")
    for x in df['user_location']:
        check = False
        for s in STATES:
            if s in x:
                is_in_US.append(STATE_DICT[s] if s in STATE_DICT else s)
                check = True
                break
        if not check:
            is_in_US.append(None)

    geo_dist = pd.DataFrame(is_in_US, columns=['State']).dropna().reset_index()
    geo_dist = geo_dist.groupby('State').count().rename(columns={"index": "Number"}) \
        .sort_values(by=['Number'], ascending=False).reset_index()
    geo_dist["Log Num"] = geo_dist["Number"].apply(lambda x: math.log(x, 2))

    geo_dist['Full State Name'] = geo_dist['State'].apply(
        lambda x: INV_STATE_DICT[x])
    geo_dist['text'] = geo_dist['Full State Name'] + \
        '<br>' + 'Num: ' + geo_dist['Number'].astype(str)
    fig.add_trace(go.Choropleth(
        locations=geo_dist['State'],  # Spatial coordinates
        z=geo_dist['Log Num'].astype(float),  # Data to be color-coded
        # set of locations match entries in `locations`
        locationmode='country names',
        colorscale="Blues",
        text=geo_dist['text'],  # hover text
        showscale=False,
        geo='geo'
    ),
        row=1, col=2)
# ['ISO-3', 'USA-states', 'country names', 'geojson-id']
    fig.update_layout(
        title_text="Real-time tracking '{}' mentions on Twitter {} UTC".format(
            settings.TRACK_WORDS[0], datetime.datetime.utcnow().strftime('%m-%d %H:%M')),
        geo=dict(
            scope='usa',
        ),
        template="plotly_dark",
        margin=dict(r=20, t=50, b=50, l=20),
        annotations=[
            go.layout.Annotation(
                text="Source: Twitter",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0,
                y=0)
        ],
        showlegend=False,
        xaxis_rangeslider_visible=True
    )

    fig.show()

    time.sleep(60)
