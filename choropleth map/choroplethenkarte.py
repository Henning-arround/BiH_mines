import os
import geopandas as gpd
import pandas as pd
import folium
from folium import plugins

# Überprüfen des aktuellen Arbeitsverzeichnisses
print("Current working directory:", os.getcwd())

# Ändern des Arbeitsverzeichnisses auf das Verzeichnis der Datei
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("New working directory:", os.getcwd())

# Schritt 1: Laden der Geodaten
bosnia_gdf = gpd.read_file('geoBoundaries-BIH-ADM2.shp')
print(bosnia_gdf.head())

# Schritt 2: Laden der Landminen-Daten (vermintete Flächen pro Region)
mines_data = pd.read_csv('landmine_areas.csv')

# Schritt 3: Verknüpfung der Landminen-Daten mit den Geodaten
# Annahme: Die Spalte mit den Regionsnamen in beiden Datensätzen heißt 'shapeName'
bosnia_gdf = bosnia_gdf.merge(mines_data, on='shapeName')

# Schritt 4: Choroplethenkarte erstellen
# Erstellen einer Grundkarte
m = folium.Map(location=[43.9159, 17.6791], zoom_start=8)

# Hinzufügen von ethnischen Mehrheiten und Anpassen der Opazität
for idx, row in bosnia_gdf.iterrows():
    # Bestimmen der Farbe basierend auf der ethnischen Mehrheit
    if row['ethnicMajority'] == 'Bosniaken':
        fill_color = 'green'
    elif row['ethnicMajority'] == 'Serben':
        fill_color = 'red'
    elif row['ethnicMajority'] == 'Kroaten':
        fill_color = 'blue'
    else:
        fill_color = 'gray'  # Für den Fall, dass keine ethnische Mehrheit angegeben ist, sollte nicht vorkommen

    # Bestimmen der Opazität basierend auf der Landminenverteilung
    if pd.isna(row['landmine_percentage']):
        fill_opacity = 0.2  # Niedrige Opazität für fehlende Landminendaten, sollte nicht vorkommen 
    else:
        fill_opacity = row['landmine_percentage'] / bosnia_gdf['landmine_percentage'].max()

    # Opazität erhöhen
    fill_opacity += 0.1  # Zum Beispiel um 0.1 erhöhen

    # Begrenzen der Opazität auf maximal 1
    fill_opacity = min(fill_opacity, 1)

    # Stil der Region definieren
    style_function = lambda x, color=fill_color, opacity=fill_opacity: {'fillColor': color, 'color': color, 'fillOpacity': opacity, 'weight': 2}

    # Region zur Karte hinzufügen
    folium.GeoJson(data=row.geometry.__geo_interface__, style_function=style_function).add_to(m)

    # Popup-Informationen hinzufügen
    if row.geometry.geom_type == 'MultiPolygon':
        for polygon in row.geometry.geoms:
            centroid = polygon.representative_point()
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>{row['shapeName']}</b>: {row['Area_Square_Kilometers']} km² verminte Fläche, {row['landmine_percentage']}% der Gesamtfläche",
                icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  # Größere Symbole
            ).add_to(m)
    else:
        centroid = row.geometry.representative_point()
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=f"<b>{row['shapeName']}</b>: {row['Area_Square_Kilometers']} km² verminte Fläche, {row['landmine_percentage']}% der Gesamtfläche",
            icon=folium.Icon(icon='info-sign', prefix='glyphicon', icon_size=(40, 40))  # Größere Symbole
        ).add_to(m)

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

# Dynamische Legende erstellen
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

m.get_root().html.add_child(folium.Element(legend_html))

# Karte speichern
m.save('landminen_ethnische_mehrheiten.html')
