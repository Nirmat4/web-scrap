from rich import print
from rich.status import Status
import pandas as pd
import glob
import time
import random
import multiprocessing
from webScraping import init_browser, extract_informacion, insert_auto, insert_data, get_aseguradoras

#╔═══════════════════════════════════════════════════════════╗
#║ Esta funcion extrae todos los excels que esten en la raiz ║
#║ y seleccionamos uno para el data-set y si existe el de    ║
#║ proxys lo llamamos tambien                                ║
#║  ° Recupera todos los ".xlsx"                             ║
#║  ° Busca el archivo "proxys" y lo retornamos si existe    ║
#╚═══════════════════════════════════════════════════════════╝
def buscar_archivos():
  dataset_df=None
  proxy_df=None
  dataset_file=None
  proxy_file=None

  with Status("[bold bright_green]Buscando archivos Excel en el directorio...[/]", spinner="dots") as status:
    time.sleep(1)
    # -- Buscar todos los archivos .xlsx --
    archivos=glob.glob('*.xlsx')
    
    # -- Clasificar los archivos --
    for archivo in archivos:
      if archivo.lower() == 'proxys.xlsx':
        proxy_file=archivo
        status.update(f"[bold bright_green]Archivo de proxies encontrado: {archivo}[/]")
      else:
        # -- Solo tomamos el primer dataset que encontremos --
        if dataset_file is None:
          dataset_file=archivo
          status.update(f"[bold bright_green]Dataset encontrado: {archivo}[/]")
    
    # -- Cargar los DataFrames si se encontraron archivos --
    if dataset_file:
      try:
        status.update(f"[bold bright_green]Cargando dataset: {dataset_file}[/]")
        dataset_df=pd.read_excel(dataset_file)
        status.update(f"[bold bright_green]Limpiando dataset: {dataset_file}[/]")
        dataset_df=dataset_df[dataset_df['Versión Autocompara ']!='sin homologación']
        dataset_df=dataset_df.drop('Unnamed: 2', axis=1)
      except Exception as e:
        status.update(f"[bold red]Error cargando dataset: {e}[/]")
    
    if proxy_file:
      try:
        status.update(f"[bold bright_green]Cargando proxies: {proxy_file}[/]")
        proxy_df=pd.read_excel(proxy_file)
      except Exception as e:
        status.update(f"[bold red]Error cargando proxies: {e}[/]")
    
    # -- Mostrar resumen de resultados --
    if dataset_df is not None or proxy_df is not None:
      print("[bold bright_green]Busqueda completada![/]")
      if dataset_df is not None:
        print("[bold bright_green]Data-set cargado")
      else:
        print("[bold red]No hay data-set[/]")
      if proxy_df is not None:
        print("[bold bright_green]Proxys cargado")
      else:
        print("[bold yellow]No hay proxys[/]")

    time.sleep(1)
    
    return dataset_df, proxy_df

#╔═══════════════════════════════════════════════════════════════════╗
#║ Esta funcion retorna un nombre aleatoreo para evitar seguimientos ║
#║  ° Devuelve un nombre al azar                                     ║
#╚═══════════════════════════════════════════════════════════════════╝
def obtener_nombre_unisex():
  nombres_unisex=[
    'Alex', 'Taylor', 'Jordan', 'Casey', 'Jamie', 'Morgan', 'Riley', 
    'Quinn', 'Avery', 'Peyton', 'Dakota', 'Skyler', 'Cameron', 'Logan',
    'Hayden', 'Reese', 'Parker', 'Drew', 'Emerson', 'Finley', 'Rowan',
    'Sage', 'Charlie', 'Kai', 'Brook', 'Dylan', 'Blake', 'Ellis', 'Harley',
    'Jesse', 'Kerry', 'Leslie', 'Marion', 'Noel', 'Robin', 'Shiloh', 'Tatum'
  ]
  return random.choice(nombres_unisex)

#╔═══════════════════════════════════════════════════════════════════╗
#║ Esta funcion cambia el formato de fecha "dd/mm/yyyy" a "ddmmmyyyy"║
#║  ° Devuelve la fecha correcta                                     ║
#╚═══════════════════════════════════════════════════════════════════╝
def formatear_fecha(fecha_str):
  # -- Formato "dd/mm/yyyy" --
  if '/' in fecha_str:
    partes=fecha_str.split('/')
    if len(partes) == 3:
      dia=partes[0].zfill(2)
      mes=partes[1].zfill(2)
      anio=partes[2]
      return f"{dia}{mes}{anio}"

  # -- Formato "yyyy-mm-dd hh:mm:ss" --
  fecha_part=fecha_str.split()[0]
  partes=fecha_part.split('-')
  
  if len(partes) == 3:
    # -- Verificamos que el primer elemento sea un año (4 dígitos) --
    if len(partes[0]) == 4:
      anio=partes[0]
      mes=partes[1].zfill(2)
      dia=partes[2].zfill(2)
      return f"{dia}{mes}{anio}"
  
  # -- Si ningún formato coincide, lanzamos error --
  raise ValueError("Formato de fecha no reconocido. Use dd/mm/yyyy o yyyy-mm-dd [hh:mm:ss]")

generos={
  "FEMENINO": "Mujer",
  "MASCULINO": "Hombre"
}

#╔═══════════════════════════════════════════════════════════╗
#║ Esta funcion procesa todos los datos de un chunk de datos ║
#║ y retorna los datos procesados en formato dict            ║
#║  ° Recorremos todas las filas del chunk                   ║
#║  ° Extraemos la informacion de autocompara                ║
#╚═══════════════════════════════════════════════════════════╝
def procesar_parcial(parte_df):
  parcial_data=[]
  # -- Iteramos en todos los elementos --
  for idx, row in parte_df.iterrows():
    modelo=row["Versión Autocompara "]
    ano=int(row["Año Mod"])
    genero=generos[row["Género"]]
    nacimiento=formatear_fecha(str(row["Fecha Nacimiento"]))
    nombre=obtener_nombre_unisex()
    cp=str(row["CP"])
    email="foyagev912@ofular.com"
    telefono="524385654784"

    # -- Hacemos las llamadas a las funciones --
    driver=init_browser()
    try:
      # -- Inicio de parametros en navegador y recuperacion de informacion --
      insert_auto(driver, ano, modelo)
      insert_data(driver, genero, nacimiento, nombre, cp, email, telefono)
      aseguradoras=get_aseguradoras(driver)
      id_data, data=extract_informacion(driver, aseguradoras)

      row_dict=row.to_dict()

      # -- Formacion final de los datos --
      combinado={
        id_data: {
          **row_dict,
          **data
        }
      }

      parcial_data.append(combinado)

    finally:
      driver.execute_script("localStorage.clear(); sessionStorage.clear();")
      # -- Cerramos el navegador --
      driver.quit()
  
  return parcial_data

#╔══════════════════════════════════════════════════════════════════╗
#║ Esta funcion recibe el data set y lo separa de forma automatica  ║
#║ envia cada uno a un proceso diferente y ejecuta "n" solicitudes  ║
#║ al mismo tiempo                                                  ║
#║  ° Leemos el total de datos y segmentamos                        ║
#║  ° Apilamos los impares o fuera de los chunks para tratarlos de  ║
#║    forma secuencial                                              ║
#║  ° Hacemos un marge de todos los datos procesados y los enviamos ║
#╚══════════════════════════════════════════════════════════════════╝
def procesamiento_paralelo(dataset_df, n_procesos):
  total_size=len(dataset_df)
  residuo=total_size % n_procesos
  limite=total_size - residuo

  # -- Dataset sin residuo --
  dataset_limpio=dataset_df.iloc[:limite]
  dataset_residuo=dataset_df.iloc[limite:]

  # -- Dividir en partes iguales --
  tamanio_parte=limite // n_procesos
  particiones=[dataset_limpio.iloc[i*tamanio_parte:(i+1)*tamanio_parte] for i in range(n_procesos)]

  with multiprocessing.Pool(processes=n_procesos) as pool:
    resultados_parciales=pool.map(procesar_parcial, particiones)

  # -- Aplanar los resultados --
  total_data=[dato for sublista in resultados_parciales for dato in sublista]

  # -- Procesar residuo secuencialmente --
  if not dataset_residuo.empty:
    resultado_residuo=procesar_parcial(dataset_residuo)
    total_data.extend(resultado_residuo)

  return total_data