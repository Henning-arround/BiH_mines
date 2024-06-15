import os
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins

# Überprüfen des aktuellen Arbeitsverzeichnisses
print("Current working directory:", os.getcwd())

# Ändern des Arbeitsverzeichnisses auf das Verzeichnis der Datei
if '__file__' in globals():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("New working directory:", os.getcwd())

# Schritt 1: Laden der Geodaten
try:
    bosnia_gdf = gpd.read_file('geoBoundaries-BIH-ADM2.shp')
    print("Geodaten erfolgreich geladen.")
    print(bosnia_gdf.head())
except Exception as e:
    print("Fehler beim Laden der Geodaten:", e)

# Schritt 2: Laden der Landminen-Daten (vermintete Flächen pro Region)
try:
    mines_data = pd.read_csv('landmine_areas.csv')
    print("Landminen-Daten erfolgreich geladen.")
    print(mines_data.head())
except Exception as e:
    print("Fehler beim Laden der Landminen-Daten:", e)

# Schritt 3: Verknüpfung der Landminen-Daten mit den Geodaten
try:
    bosnia_gdf = bosnia_gdf.merge(mines_data, on='shapeName')
    print("Daten erfolgreich verknüpft.")
except Exception as e:
    print("Fehler beim Verknüpfen der Daten:", e)

# Schritt 4: Berechnung der Differenz zwischen 2019 und 2023 und Runden der Differenz
bosnia_gdf['difference_2019_2023'] = (bosnia_gdf['Area_Square_Kilometers_2019'] - bosnia_gdf['Area_Square_Kilometers_2023']).round(2)

# Schritt 5: Choroplethenkarte erstellen
m = folium.Map(location=[43.9159, 17.6791], zoom_start=8)

# FeatureGroups für 2019 und 2023
layer_2019 = folium.FeatureGroup(name='2019', show=True)
layer_2023 = folium.FeatureGroup(name='2023', show=False)

# Hinzufügen von ethnischen Mehrheiten und Anpassen der Opazität
for idx, row in bosnia_gdf.iterrows():
    if row['ethnicMajority'] == 'Bosniaken':
        fill_color = 'green'
    elif row['ethnicMajority'] == 'Serben':
        fill_color = 'red'
    elif row['ethnicMajority'] == 'Kroaten':
        fill_color = 'blue'
    else:
        fill_color = 'gray'  # Für den Fall, dass keine ethnische Mehrheit angegeben ist, sollte nicht vorkommen

    # Berechnung der Opazitäten für 2019 und 2023
    fill_opacity_2019 = 0.2  # Grundopazität, falls keine Landminendaten vorhanden
    fill_opacity_2023 = 0.2  # Grundopazität, falls keine Landminendaten vorhanden
    if not pd.isna(row['Area_Square_Kilometers_2019']):
        fill_opacity_2019 = row['Area_Square_Kilometers_2019'] / bosnia_gdf['Area_Square_Kilometers_2019'].max()
    if not pd.isna(row['Area_Square_Kilometers_2023']):
        fill_opacity_2023 = row['Area_Square_Kilometers_2023'] / bosnia_gdf['Area_Square_Kilometers_2023'].max()

    fill_opacity_2019 += 0.1  # Opazität erhöhen
    fill_opacity_2023 += 0.1  # Opazität erhöhen
    fill_opacity_2019 = min(fill_opacity_2019, 1)  # Begrenzen der Opazität auf maximal 1
    fill_opacity_2023 = min(fill_opacity_2023, 1)  # Begrenzen der Opazität auf maximal 1

    # Stilfunktion für 2019 und 2023
    style_function_2019 = lambda x, color=fill_color, opacity=fill_opacity_2019: {'fillColor': color, 'color': color, 'fillOpacity': opacity, 'weight': 2}
    style_function_2023 = lambda x, color=fill_color, opacity=fill_opacity_2023: {'fillColor': color, 'color': color, 'fillOpacity': opacity, 'weight': 2}

    # GeoJson hinzufügen für 2019
    try:
        folium.GeoJson(data=row.geometry.__geo_interface__, style_function=style_function_2019).add_to(layer_2019)
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Region {row['shapeName']} (2019):", e)

    # GeoJson hinzufügen für 2023
    try:
        folium.GeoJson(data=row.geometry.__geo_interface__, style_function=style_function_2023).add_to(layer_2023)
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Region {row['shapeName']} (2023):", e)

    # Marker für die Unterschiede
    if row.geometry.geom_type == 'MultiPolygon':
        for polygon in row.geometry.geoms:
            centroid = polygon.representative_point()
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>{row['shapeName']}</b>: 2019: {row['Area_Square_Kilometers_2019']} km² verminte Fläche<br>2023: {row['Area_Square_Kilometers_2023']} km² verminte Fläche<br>Unterschied: {row['difference_2019_2023']} km²",
                icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  # Größere Symbole
            ).add_to(layer_2019)
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>{row['shapeName']}</b>: 2019: {row['Area_Square_Kilometers_2019']} km² verminte Fläche<br>2023: {row['Area_Square_Kilometers_2023']} km² verminte Fläche<br>Unterschied: {row['difference_2019_2023']} km²",
                icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))
            ).add_to(layer_2023)
    else:
        centroid = row.geometry.representative_point()
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"<b>{row['shapeName']}</b>:2019: {row['Area_Square_Kilometers_2019']} km² verminte Fläche<br>2023: {row['Area_Square_Kilometers_2023']} km² verminte Fläche<br>Unterschied: {row['difference_2019_2023']} km²",
            icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  # Größere Symbole
        ).add_to(layer_2019)
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"<b>{row['shapeName']}</b>: 2019: {row['Area_Square_Kilometers_2019']} km² verminte Fläche<br>2023: {row['Area_Square_Kilometers_2023']} km² verminte Fläche<br>Unterschied: {row['difference_2019_2023']} km²",
            icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  # Größere Symbole
        ).add_to(layer_2023)

# Hinzufügen der Layer zur Karte
layer_2019.add_to(m)
layer_2023.add_to(m)

# Layer Control hinzufügen
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

# Dynamische Legenden erstellen
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

# Legenden zur Karte hinzufügen
m.get_root().html.add_child(folium.Element(legend_html))  

# Karte anzeigen
m.save('landminen_vergleich.html')




