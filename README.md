# web-scrap
El siguiente proyecto es un proyecto de web-scraping para extraer las cotizaciones de los diferentes seguros que se publican en la aplicacion de autocompara de sntander. Estas cotizaciones son anexadas a una serie de datos que fungieron como datos de entrada.

El script es un sistema que recupera un par de archivos (un data-set y una lista de proxys) para entrar a la pagina de autocompara de santander y obtener las cotizaciones de diferentes modelos de autos y poder generar un analisis profundo de la data y de las diferentes condiciones que dispara ciertos precios.

El sistema tiene diversas fucniones, para tratar todos los datos al mismo timepo (dado tu numero de procesos) o tu dandole un numero exacto de elementos a procesar (igual usara division por procesos) o simplemente procesar el el primer elemento para saber como funciona el sistema.

Los formatos de salida son JSON para un mejor manejo ya que los datos involucran coberturas y sulen se dispares para meter en un csv.

## Tecnologías
El sistema hace uso de librerias de alto nivel como selenium o pandas, ademas de algunas librerias para poder darle foramto a la vista en terminal

## Instalacion
Para instalar el programa debes seguir el siguiente proceso.
```bash
git clone https://github.com/star-lord-mix/web-scrap.git
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd src/
python main.py
```