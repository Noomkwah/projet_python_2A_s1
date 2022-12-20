#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import urllib.request
import urllib.error

import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

###------------------Scrapping--------------------------------------------------------

def extraction(latitude,longitude, startyear, endyear):
    """Extraction de la base de données pour les paramètres de longitudes, latitudes et de périodes
    à partir de l'api de la comission européenne https://re.jrc.ec.europa.eu"""
    
    req = "https://re.jrc.ec.europa.eu/api/seriescalc?lat="+str(latitude)+"&lon="+str(longitude)+"&startyear="+str(startyear)+"&endyear="+str(endyear)+"&month=0&showtemperatures=1&outputformat=csv&browser=1"
    url = urllib.request.urlopen(req) 
    return url

def normalisation(url, latitude,longitude):
    """On standardise les données récupérées pour les rendre comparables entre elles"""
    
    df_norm = pd.read_csv(url,skiprows=(8),skipfooter=9,engine='python') #On se débarasse des informations superflues
    
    df_norm['annee'] = df_norm['time'].str[:4] #On extrait la variable d'année à partir de la variable temps
    df_norm = df_norm.groupby(['annee'])['G(i)', 'WS10m'].mean() #On calcule la moyenne annuelle de la variable ensoleillement et de la variable vitesse du vent
    df_norm['latitude'] = latitude #On rajoute les paramètres de latitude et de longitude
    df_norm["longitude"] = longitude

    return df_norm


def creation_df_zone(latitude_1,latitude_2,longitude_1, longitude_2, precision,startyear,endyear):
    """Cette fonction sert à créer une base de données des moyennes d'ensoleillement et de vitesses du vent par an
        sur une zone géographique définie par ses paramètres de latitude et de longitude. 
        La variables précision donne la precision du quadrillage réalisé, type = int, > 0.
        Les variables startyear et endyear permettent de définir l'intervalle de temps considéré (2005-2016).
        Exemple : zone(1,2,-1,1,2,2010,2012)"""

    ls_df = [] #création d'une liste vide qui servira a réunir les bases de données années par années
    for longitude in range(longitude_1, (longitude_2+1), 1): #On parcourt un à un les longitude comprises entre longitude_1 et longitude_2
        for latitude in range(latitude_1*precision,(latitude_2+1)*precision,1): #On parcourt les latitudes selon le meme principe en affinant le  quadrillage à l'aide de la variable précision
            latitude = latitude/precision 
            
            try :  #try permet de ne pas considérer les coordonnées manquantes (ex : océan). 
                url = extraction(latitude, longitude, startyear, endyear)#Récupération de la base de données brute
                df_norm = normalisation(url, latitude, longitude)#Standardisation de la base de données
                ls_df.append(df_norm)#Ajout de la base de données à la liste 
                
                
            except urllib.error.HTTPError:     #au cas où l'on tombe sur des lieux sans mesures, ignorer
                pass    
                
            
    df_final = pd.concat(ls_df, axis=0, ignore_index=False) #Concaténation des différents df (un par coordonnées)
    df_final.reset_index(level=0, inplace=True) #On enleve l'indexation par année
    
    
    
    
    df_final.to_csv('BaseDonneesEnsoleilementPythonDS.csv')  #Mettre le chemin d'accès et le nom du fichier avant le .csv    
    return df_final



###-----------------Création d'une carte intéractive-----------------------

def carte_interactive(df,parametre):
    """Création d'une carte intéractive avec plotly, permet de visualiser les données
        Paramètre = "G(i)" [ensoleillement] ou "WS10m" [vitesse du vent]
        Il est nécessaire d'avoir construit le df d'abord au moyen de la fonction creation_df_zone
        
        Exemple : carte_interactive(df, "G(i)")
        """
    df["size"] = pd.Series([50 for x in range(len(df.index))])  #Création d'une variable de taille pour les 
    
    fig = px.scatter_mapbox(df.dropna(), #On se débarasse des valeurs manquantes
                        lat="latitude", #On donne les variables de coordonnées 
                        lon="longitude", 
                        color=str(parametre), #La couleur vient du parametre regardé : "G(i)" ou "WS10m"
                        size ="size", #La taille de chaque point
                        mapbox_style="carto-positron", #Le fond de carte
                        
                        #On joue avec les paramètres de légende pour les rendre cohérent avec les paramètres étudiés et consistants à travers le temps
                        color_continuous_scale=[[0, 'blue'], [0.15, 'green'],[0.30, "yellow"], [0.45, 'orange'], [0.60, 'pink'], [0.75, 'crimson'] ,[1.0, 'red']],
                        color_continuous_midpoint = df[parametre].mean(),
                        range_color=([df[parametre].min(),df[parametre].max()]),
                        
                        #On anime le tout en fonction de l'année
                        animation_frame = 'annee')
    
    fig.show()



###--------Exécution du code--------------------------

df = creation_df_zone(40,60,-2,8,2,2013,2016)
carte_interactive(df,"G(i)")


