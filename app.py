from flask import Flask,render_template,request,redirect
import os
import datetime

app = Flask(__name__)
########
# should be 3

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
# STATICFILES_DIRS = (
#     os.path.join(os.path.dirname(BASE_DIR), 'static'),
# )

def roundTime(dt=None, roundTo=60):
    if dt == None : dt = datetime.datetime.now()
    seconds = (dt - dt.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def transform_citibike_api_df(citibike_api_df,time_now_rounded):
    #df = pd.DataFrame(columns=['month','dayofweek','hour','minute','temp','humidity','windspeed','visibility','rain','snow'])
    month = time_now_rounded.month
    dayofweek = time_now_rounded.weekday()
    hour = time_now_rounded.hour
    minute = time_now_rounded.minute

    # get weather data
    import requests
    import re
    url = ('http://api.wunderground.com/api/%s/geolookup/conditions/q/NY/New_York_City.json')% 'e7cb14d1c7eeaf3f'
    r = requests.get(url)
    r.text
    r.json()
    r.json().keys()
    temp = r.json()['current_observation']['temp_f']
    humidity = float(r.json()['current_observation']['relative_humidity'].replace('%',''))
    windspeed = r.json()['current_observation']['wind_mph']
    visibility = float(r.json()['current_observation']['visibility_mi'])
    rain = 1 if re.search(r'[rR]ain',r.json()['current_observation']['weather']) else 0
    snow = 1 if re.search(r'[sS]now',r.json()['current_observation']['weather']) else 0

    df = pd.DataFrame()
    df = df.append({'month':month,'dayofweek':dayofweek,'hour':hour,'minute':minute,\
                    'temp':temp,'humidity':humidity,'windspeed':windspeed,'visibility':visibility\
                    ,'rain':rain,'snow':snow},ignore_index=True)
    return df

def helper_function(s,df):
    try:
        with open('station_model_' +str(s) +'.cPickle', 'r') as f:
            station_model = cPickle.load(f)
        return station_model.predict(df)[0]
    except:
        return 0

# get citiBike_API_df and return a df with predictions for each station
def get_predictions(citibike_api_df):
    import datetime
    time_now = datetime.datetime.now()
    time_now_rounded = roundTime(time_now, roundTo=30*60)

    df = transform_citibike_api_df(citibike_api_df,time_now_rounded)
    try:
        citibike_api_df['prediction'] = citibike_api_df['id'].apply(lambda x: helper_function(x, df))
    except:
        print 'passing...'
        citibike_api_df[citibike_api_df['id'] == s]['prediction'] = 0
    return citibike_api_df

import requests
url = 'https://www.citibikenyc.com/stations/json'
r = requests.get(url)
from pandas.io.json import json_normalize
citibike_api_live = json_normalize(r.json()['stationBeanList']) # convert to DF


r = requests.get("http://jerez.cartodb.com/api/v2/sql?q=SELECT * from stations_live &api_key=235b31f3d8a7a8a8ad57ada8dec909a2455b7cd2")
data = r.json()
cartodb_df = json_normalize(data['rows']) # convert to DF

#stations_with_predictions = get_predictions(citibike_api_live)

#import urllib, json

# cartodb_table = 'stations_live'
# col_name1 = 'availableDocks'
# col_name2 = 'availableBikes'
# col_name3 = 'predictions'
# cartodb_account = 'jerez'
# cartodb_key = '235b31f3d8a7a8a8ad57ada8dec909a2455b7cd2'
#
# temp_col = []
# # temp_df = pd.DataFrame(live_scolumns=['availableBikes','availableDocks','id'])
# for station_id in pd.unique(citibike_api_live['id']):
#     print station_id,
#     #sql = "UPDATE %s SET %s=%d WHERE id<%d" % (cartodb_table,col_name,0,3000)
#     sql = "UPDATE %s SET %s = %d WHERE id = %d" % (cartodb_table,col_name1,citibike_api_live[citibike_api_live.id == station_id]['availableDocks'],station_id)
#     url = "http://%s.cartodb.com/api/v2/sql?q=%s&api_key=%s" % (cartodb_account,sql,cartodb_key)
#     u = urllib.urlopen(url)
#     data = u.read()
#     dataJSON = json.loads(data)
#
#     sql = "UPDATE %s SET %s = %d WHERE id = %d" % (cartodb_table,col_name2,citibike_api_live[citibike_api_live.id == station_id]['availableBikes'],station_id)
#     url = "http://%s.cartodb.com/api/v2/sql?q=%s&api_key=%s" % (cartodb_account,sql,cartodb_key)
#     u = urllib.urlopen(url)
#     data = u.read()
#     dataJSON = json.loads(data)
#
#     sql = "UPDATE %s SET %s = %d WHERE id = %d" % (cartodb_table,col_name3,stations_with_predictions[stations_with_predictions.id == station_id]['prediction'],station_id)
#     url = "http://%s.cartodb.com/api/v2/sql?q=%s&api_key=%s" % (cartodb_account,sql,cartodb_key)
#     u = urllib.urlopen(url)
#     data = u.read()
#     dataJSON = json.loads(data)

@app.route('/',methods=['GET','POST'])
def root():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return render_template('userinfo.html')

#####################################
## IMPORTANT: I have separated /next_lulu INTO GET AND POST
## You can also do this in one function, with If and Else
## The attribute that contains GET and POST is: request.method
#####################################

if __name__ == "__main__":
    app.run(debug=True)
