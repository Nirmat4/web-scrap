from rich import print
from rich.status import Status
import pandas as pd
import glob
import time
import random

# -- Buscar archivos Excel --
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
      if proxy_df is not None:
        print("[bold bright_green]Proxys cargado")
    time.sleep(1)
    
    return dataset_df, proxy_df

def obtener_nombre_unisex():
  nombres_unisex=[
    'Alex', 'Taylor', 'Jordan', 'Casey', 'Jamie', 'Morgan', 'Riley', 
    'Quinn', 'Avery', 'Peyton', 'Dakota', 'Skyler', 'Cameron', 'Logan',
    'Hayden', 'Reese', 'Parker', 'Drew', 'Emerson', 'Finley', 'Rowan',
    'Sage', 'Charlie', 'Kai', 'Brook', 'Dylan', 'Blake', 'Ellis', 'Harley',
    'Jesse', 'Kerry', 'Leslie', 'Marion', 'Noel', 'Robin', 'Shiloh', 'Tatum'
  ]
  return random.choice(nombres_unisex)

def formatear_fecha(fecha_str):
  try:
    partes=fecha_str.split('/')
    
    if len(partes) != 3:
      raise ValueError("Formato de fecha incorrecto")
    
    dia=partes[0].zfill(2)
    mes=partes[1].zfill(2)
    anio=partes[2]
    
    return f"{dia}{mes}{anio}"

  except (ValueError, AttributeError, IndexError) as e:
    print(f"Error formateando fecha '{fecha_str}': {e}")
    return None 