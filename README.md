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

## Requerimientos
Para la ejecución de este script hay que tenere una serie de requerimientos minimos para poder tener un funcionamiento correcto:
 - Sistema operativo Linux (Debian/Ubuntu)
    - Aun no se analiza la posibilidad de despliegue en Windows
 - Python (de manera recomendable la version 3.11.12)
 - Chromiun (es necesario este para un mejor control del driver)

## Actualizaciones
En las proximas actualziaciones se planea un analizador automatico que entregue un PDF con analisis de la informacion, como los seguros mas costosos, los que tienen mas coberturas, o los que abarcan mas automoviles, incluso le papel que tiene el codigo postal (donde vivies) y el genero en los precios y coberturas de un seguro de auto.

De la parte tecnica se anexara la funcionalidad de proxys ya que actualemnte dada la lista de proxys (no sirven) no se ha incluido la funcion la cual divide los drivers y evita el rastreo.

Ademas de anexar fucniones para evitar errores y continuar con los procesos.