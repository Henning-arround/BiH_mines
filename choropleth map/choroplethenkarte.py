import os
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins


# Ändern des Arbeitsverzeichnisses auf das Verzeichnis der Datei
if '__file__' in globals():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Schritt 1: Laden der Geodaten
try:
    bosnia_map = gpd.read_file('geoBoundaries-BIH-ADM2.shp')
except Exception as e:
    print("Fehler beim Laden der Geodaten:", e)

# Schritt 2: Laden der Landminen-Daten (vermintete Flächen pro Region)
try:
    mines_data = pd.read_csv('landmine_areas.csv')
except Exception as e:
    print("Fehler beim Laden der Landminen-Daten:", e)

# Schritt 3: Verknüpfung der Landminen-Daten mit den Geodaten
try:
    bosnia_map = bosnia_map.merge(mines_data, on='shapeName')
except Exception as e:
    print("Fehler beim Verknüpfen der Daten:", e)

# Schritt 4: Choroplethenkarte erstellen
m = folium.Map(location=[43.9159, 17.6791], zoom_start=8, tiles=None)
base_map = folium.FeatureGroup(name='Basemap', overlay=True, control=False)
folium.TileLayer(tiles='OpenStreetMap').add_to(base_map)
base_map.add_to(m)

# LayerGroup für alle Jahre erstellen
layer_2015 = folium.FeatureGroup(name='2015', overlay=False, show=False) 
layer_2019 = folium.FeatureGroup(name='2019', overlay=False, show=False)  
layer_2022 = folium.FeatureGroup(name='2022', overlay=False)  


# Hinzufügen von ethnischen Mehrheiten
for idx, row in bosnia_map.iterrows():
    if row['ethnicMajority'] == 'Bosniaken':
        fill_color = 'green'
    elif row['ethnicMajority'] == 'Serben':
        fill_color = 'red'
    elif row['ethnicMajority'] == 'Kroaten':
        fill_color = 'blue'
    else:
        fill_color = 'gray'  # Für den Fall, dass keine ethnische Mehrheit angegeben ist, sollte nicht vorkommen
        

    # Berechnung der Opazitäten 
    fill_opacity_2015 = 0.1  # Grundopazität, falls keine Landminendaten vorhanden
    fill_opacity_2019 = 0.1  
    fill_opacity_2022 = 0.1
    landmine_percentage_2015 = round((row['Area_Square_Kilometers_2015'] / row['total_area'] * 100),2)
    fill_opacity_2015 = landmine_percentage_2015 / 10  # Skalierte Opazität für 2015
    landmine_percentage_2019 = round((row['Area_Square_Kilometers_2019'] / row['total_area'] * 100),2)
    fill_opacity_2019 = landmine_percentage_2019 / 10   # Skalierte Opazität für 2019
    landmine_percentage_2022 = round((row['Area_Square_Kilometers_2022'] / row['total_area'] * 100),2)
    fill_opacity_2022 = landmine_percentage_2022 / 10   # Skalierte Opazität für 2022

    # Opazität begrenzen auf maximal 1
    fill_opacity_2015 = min(fill_opacity_2015, 1)
    fill_opacity_2019 = min(fill_opacity_2019, 1)
    fill_opacity_2022 = min(fill_opacity_2022, 1)

    # Stilfunktionen
    style_function_2015 = lambda x, color=fill_color, opacity=fill_opacity_2015: {'fillColor': color, 'color': color, 'fillOpacity': opacity, 'weight': 2}
    style_function_2019 = lambda x, color=fill_color, opacity=fill_opacity_2019: {'fillColor': color, 'color': color, 'fillOpacity': opacity, 'weight': 2}
    style_function_2022 = lambda x, color=fill_color, opacity=fill_opacity_2022: {'fillColor': color, 'color': color, 'fillOpacity': opacity, 'weight': 2}

   # GeoJson hinzufügen 2015
    try:
        folium.GeoJson(data=row.geometry.__geo_interface__, style_function=style_function_2015).add_to(layer_2015)
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Region {row['shapeName']} (2015):", e)

    # GeoJson hinzufügen 2019
    try:
        folium.GeoJson(data=row.geometry.__geo_interface__, style_function=style_function_2019).add_to(layer_2019)
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Region {row['shapeName']} (2019):", e)

    # GeoJson hinzufügen 2022
    try:
        folium.GeoJson(data=row.geometry.__geo_interface__, style_function=style_function_2022).add_to(layer_2022)
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Region {row['shapeName']} (2022):", e)

    # Infopoints 
    if row.geometry.geom_type == 'MultiPolygon':
        for polygon in row.geometry.geoms:
            centroid = polygon.representative_point()
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>{row['shapeName']}</b>:<br><br><b>2015:</b> {row['Area_Square_Kilometers_2015']} km² verminte Fläche<br><br><b>{landmine_percentage_2015}%</b> der Gesamtfläche",
                icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  
            ).add_to(layer_2015)
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>{row['shapeName']}</b>:<br><br><b>2019:</b> {row['Area_Square_Kilometers_2019']} km² verminte Fläche<br><br><b>{landmine_percentage_2019}%</b> der Gesamtfläche",
                icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  
            ).add_to(layer_2019)
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>{row['shapeName']}</b>:<br><br><b>2022:</b> {row['Area_Square_Kilometers_2022']} km² verminte Fläche<br><br><b>{landmine_percentage_2022}%</b> der Gesamtfläche",
                icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))
            ).add_to(layer_2022)
    else:
        centroid = row.geometry.representative_point()
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"<b>{row['shapeName']}</b>:<br><br><b>2015:</b> {row['Area_Square_Kilometers_2015']} km² verminte Fläche<br><br><b>{landmine_percentage_2015}%</b> der Gesamtfläche",
            icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40)) 
        ).add_to(layer_2015)
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"<b>{row['shapeName']}</b>:<br><br><b>2019:</b> {row['Area_Square_Kilometers_2019']} km² verminte Fläche<br><br><b>{landmine_percentage_2019}%</b> der Gesamtfläche",
            icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40)) 
        ).add_to(layer_2019)
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"<b>{row['shapeName']}</b>:<br><br><b>2022:</b> {row['Area_Square_Kilometers_2022']} km² verminte Fläche<br><br><b>{landmine_percentage_2022}%</b> der Gesamtfläche",
            icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  
        ).add_to(layer_2022)

# Layer Groups zur Karte hinzufügen
layer_2015.add_to(m)
layer_2019.add_to(m)
layer_2022.add_to(m)

# Kontrollmenü
folium.LayerControl(collapsed=False, autoZIndex=False, exclusive=True).add_to(m)

# Koordinatenanzeige beim Hovern über der Karte hinzufügen
formatter = "function(num) {return L.Util.formatNum(num, 5) + ' º ';};"
mouse_position = plugins.MousePosition(
    position='topright',
    separator=' | ',
    empty_string='Koordinaten',
    lng_first=True,
    num_digits=20,
    prefix="Koordinaten:",
    lat_formatter=formatter,
    lng_formatter=formatter,
)
m.add_child(mouse_position)

# Legende erstellen
legend_html = '''
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 300px;
    height: auto;
    background-color: white;
    border:2px solid grey;
    z-index:9999;
    font-size:14px;
    padding: 10px;
    ">
    <h5>Anteil Fläche mit aktiven Landminen an Gesamtfläche:</h5>
    <div>
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;">
            <div style="background: linear-gradient(to right, rgba(0, 128, 0, 0.1), rgba(0, 128, 0, 1)); width: 280px; height: 20px;"></div>
            <span>Bosnische Mehrheit</span>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;">
            <div style="background: linear-gradient(to right, rgba(255, 0, 0, 0.1), rgba(255, 0, 0, 1)); width: 280px; height: 20px;"></div>
            <span>Serbische Mehrheit</span>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 10px;">
            <div style="background: linear-gradient(to right, rgba(0, 0, 255, 0.1), rgba(0, 0, 255, 1)); width: 280px; height: 20px;"></div>
            <span>Kroatische Mehrheit</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <span>0%</span>
            <span>5%</span>
            <span>10%</span>
        </div>
    </div>
</div>
'''

# Legende zur Karte hinzufügen
m.get_root().html.add_child(folium.Element(legend_html))  

# Karte anzeigen
m.save('../templates/choro.html')
