#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"
import plotly.graph_objects as go
import urllib.request
import urllib.error
###------------------Scrapping----------------------
#Le but est de créer une base de données avec toutes les infos nécessaires sur une zone particulière
#ça se décompose en plusieurs étapes
#1) On identifie la zone (latitude et longitude) 
#2) On crée une base de données avec chacun des points dans lesquels on va récolter les données à partir du site
#3) On fait la récolte de données

#1 + 2) identification de la zone

def zone(latitude_1,latitude_2,longitude_1, longitude_2, precision,startyear,endyear):
    """On entre les latitudes et la longitudes qui permettent de définir la zone dans laquelle on récoltera les données
        On renvoie un df avec chacun des points considérés"""

    #time= "20150105:1110"
    
    ls = []
    temp = pd.DataFrame(columns = ["latitude","longitude","G(i)","WS10m"])
    for longitude in range(longitude_1, (longitude_2+1), 1):
        for latitude in range(latitude_1*precision,(latitude_2+1)*precision,1):
        
            latitude = latitude/precision 
            
            try :  
                
                req = "https://re.jrc.ec.europa.eu/api/seriescalc?lat="+str(latitude)+"&lon="+str(longitude)+"&startyear="+str(startyear)+"&endyear="+str(endyear)+"&month=0&showtemperatures=1&outputformat=csv&browser=1"
                url = urllib.request.urlopen(req) 
                pomme = pd.read_csv(url,skiprows=(8),skipfooter=9,engine='python')
                pomme['annee'] = pomme['time'].str[:4]

                pomme = pomme.groupby(['annee'])['G(i)', 'WS10m'].mean()
                pomme['latitude'] = latitude
                pomme["longitude"] = longitude

                ls.append(pomme)
                
                #print("POMME", pomme)
                
            except urllib.error.HTTPError:     
                pomme =[np.nan,np.nan,np.nan,np.nan]
            

            #print(temp)
    df_final = pd.concat(ls, axis=0, ignore_index=False)
            
    return df_final

df = zone(40,50,3,5,2,2013,2016)
df.reset_index(level=0, inplace=True)
df["size"] = pd.Series([50 for x in range(len(df.index))])
import plotly.express as px

# fig = px.density_mapbox(df, lat='latitude', lon='longitude', z='G(i)', radius=30,
#                         center=dict(lat=0, lon=180), zoom=0,
#                         mapbox_style="carto-positron")
# fig.show()
fig = px.scatter_mapbox(df.dropna(), lat="latitude", lon="longitude", color="G(i)", 
                        size ="size",
                        mapbox_style="carto-positron",color_continuous_scale=[[0, 'blue'], [0.15, 'green'],[0.30, "yellow"], [0.45, 'orange'], [0.60, 'pink'], [0.75, 'crimson'] ,[1.0, 'red']],
                        animation_frame = 'annee')
fig.show()

# fig = go.Figure(go.Scattermapbox(
#     fill = "toself",
#     lon = df["longitude"] , lat = df["latitude"],
#     marker = { 'size': 30, 'color': df["G(i)"] }))
# fig.show()



