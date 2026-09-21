from zipfile import ZipFile
from geopandas import read_file as read_file_gpd
from os import path, makedirs, scandir
from csv import DictReader
from folium import Map, Marker, DivIcon
from  shutil import rmtree
import webbrowser
from time import time

# Clase para procesar archivo KMZ
class fileReader():

    # Constructor
    def __init__(self, path):

        self.path, self.mapa = path, None

    # Metodo para converir KMZ a csv
    def kmzToCsv(self):
        
        # Obtengo la carpeta y nombre del archivo
        dir, file = path.split(self.path)

        # Construir la ruta exacta uniendo la raíz con 'input' y el nombre del archivo
        ruta_correcta = path.join(path.dirname(path.dirname(path.abspath(__file__))), dir, file)
        
        # Nombre de directorio temporal
        extract_dir = 'temp_kml'

        # Creo un directorio temporal donde extraigo el contenido del archivo KMZ
        makedirs(extract_dir, exist_ok=True)

        # Descomprimo el contenido
        with ZipFile(ruta_correcta, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Variable inicializada como nula
        kml_files = next((f.name for f in scandir(extract_dir) if f.is_file() and f.name.endswith('.kml')), None)
        
        # Si obtengo un valor
        if kml_files:

            # Ruta del archivo kml
            kml_path = path.join(extract_dir, kml_files)

            # Leer el archivo KML usando GeoPandas
            gdf = read_file_gpd(kml_path, layer="PTZ")

            # Obtengo la latitud y la longitud
            gdf["long"], gdf["lat"] = gdf["geometry"].x, gdf["geometry"].y

            # Guardo el archivo en un csv
            gdf.iloc[:, [13, 14, 1]].to_csv(r"..\input\resultado.csv", sep = ";", index=False)

        # Caso donde no encuentro el KML
        else:

            print("Archivo .kml no encontrado ...")

        # Si la carpeta existe la elimino
        if path.isdir(extract_dir):

            rmtree(extract_dir)

    # Metodo que devuelve un iterador de nombre, longitud y latitud
    def csvReader(self, path):

        with open(path, mode='r', encoding='utf-8') as archivo:

            # Usamos DictReader y especificamos que el separador es ';'
            lector = DictReader(archivo, delimiter=';')

            # Itero sobre cada una de las lineas
            for fila in lector:

                try:

                    long, lat, name = float(fila["long"]), float(fila["lat"]), fila["Name"]

                    yield long, lat, name

                except (ValueError, KeyError):
                    
                    continue

    # Guardo puntos en el objeto de tipo mapa
    def saveInfo(self, counter, long, lat, name):

        # Centro el mapa
        if counter == 0:

            # Inicializo el mapa
            self.mapa = Map(location=[lat, long], zoom_start = 16)

        # Obtengo el nombre y la describción
        nom, describ = name.split("-", maxsplit=1)

        # Verifico el largo del nombre 
        ubicacion_procesada = f"{describ[:20]}<br>{describ[20:]}" if len(describ) > 20 else describ

        # Añado un nuevo punto
        Marker(location=[lat, long], radius=10, color='blue', fill=True, fill_color='cyan', fill_opacity=0.7, tooltip=nom, draggable=True).add_to(self.mapa)

        # Añado una nueva nota
        Marker(location=[lat, long],draggable=True,
            icon=DivIcon(
                html = f"""<div style="font-family: sans-serif; font-size: 7px; 
                            white-space: nowrap; margin-left: 19px; margin-top: -15px;
                            border-radius: 7px; border: 2.5px solid blue;
                            color: #FFD700; 
                            background-color: #000000; 
                            width: 80px; 
                            height: 30px; 
                            padding: 4px 6px; 
                            box-sizing: border-box;
                            line-height: 1.1;">
                    <b>{nom}</b><br>{ubicacion_procesada}
                </div>"""
            )).add_to(self.mapa)

    # Metodo para crar el mapa a partir de la lectura de un CSV
    def mapCSV(self):

        # Obtengo el generador previo a la iteración
        generator_cam = self.csvReader(r"..\input\resultado.csv")

        # Itero con list comprenhensión ya que es más rápidos que un for normal
        [self.saveInfo(counter, long, lat, name) for counter, (long, lat, name) in enumerate(generator_cam)]

        self.mapa.save(r"..\output\mapear.html")

if __name__ == "__main__":

    start = time()
    
    # Se puede selecionar el archivo que se quiera siempre y cuando sea de extensión kmz
    lector = fileReader(r"KMZ PME Full ACTUALIZADO 13 de agosto 2026.kmz")
    lector.kmzToCsv()
    lector.mapCSV()
    end = time()

    result = end - start

    print(f"Total de tiempo {result:.6f} segundos")

    
    # Verifico la existencia de la carpeta output y que exista el archivo mapear.html
    if path.isdir(r"..\output") and path.isfile(r"..\output\mapear.html"):

        webbrowser.open_new_tab(r"..\output\mapear.html")