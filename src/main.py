from webScraping import init_browser, extract_informacion, insert_auto, insert_data, get_aseguradoras, json_to_excel
from rich import print
from rich.status import Status
from commons import buscar_archivos, obtener_nombre_unisex, formatear_fecha, procesamiento_paralelo, generos
from tabulate import tabulate
import multiprocessing
import json
from selenium.webdriver.support.ui import WebDriverWait
import time

# -- Datos para tablas de estructura --
dataset_cols=[
    ["Versión Autocompara", "Modelo exacto como aparece en Autocompara"],
    ["Año Mod", "Año del modelo del auto"],
    ["Género", "Género del usuario (simulado o no)"],
    ["Fecha Nacimiento", "Fecha de nacimiento del usuario (simulado o no)"],
    ["CP", "Código postal (dato real)"],
]
proxy_cols=[
    ["ip", "Dirección IP"],
    ["port", "Puerto"],
]


# -- Alistamos las configuraciones --
dataset_df, proxy_df=buscar_archivos()

#╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
#║ El sigueinte script es un sistema que recupera un par de archivos (un data-set y una lista de proxys) para entrar ║
#║ a la pagina de autocompara de santander y obtener las cotizaciones de diferentes modelos de autos y poder generar ║
#║ un analisis profundo de la data y de las diferentes condiciones que dispara ciertos precios.                      ║
#║                                                                                                                   ║
#║ El sistema tiene diversas fucniones, para tratar todos los datos al mismo timepo (dado tu numero de procesos) o   ║
#║ tu dandole un numero exacto de elementos a procesar (igual usara division por procesos) o simplemente procesar el ║
#║ el primer elemento para saber como funciona el sistema                                                            ║
#║                                                                                                                   ║
#║ Los formatos de salida son JSON para un mejor manejo ya que los datos involucran coberturas y sulen se dispares   ║
#║ para meter en un csv.                                                                                             ║
#╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
print("[bold cornflower_blue]                __                                     _             [bold deep_pink2]   _____             __                  __         \n[bold cornflower_blue] _      _____  / /_        ___________________ _____  (_)___  ____ _ [bold deep_pink2]  / ___/____ _____  / /_____ _____  ____/ /__  _____\n[bold cornflower_blue]| | /| / / _ \/ __ \______/ ___/ ___/ ___/ __ `/ __ \/ / __ \/ __ `/ [bold deep_pink2]  \__ \/ __ `/ __ \/ __/ __ `/ __ \/ __  / _ \/ ___/\n[bold cornflower_blue]| |/ |/ /  __/ /_/ /_____(__  ) /__/ /  / /_/ / /_/ / / / / / /_/ /  [bold deep_pink2] ___/ / /_/ / / / / /_/ /_/ / / / / /_/ /  __/ /    \n[bold cornflower_blue]|__/|__/\___/_.___/     /____/\___/_/   \__,_/ .___/_/_/ /_/\__, /   [bold deep_pink2]/____/\__,_/_/ /_/\__/\__,_/_/ /_/\__,_/\___/_/     \n[bold cornflower_blue]                                            /_/            /____/    [bold deep_pink2]                                                    \n[/]")
print("[bold cornflower_blue]¡Bienvenido al sistema de web-scraping para autocompara de [bold deep_pink2]santander[bold cornflower_blue]![/]")
print("[bold cornflower_blue]Este es un script para poder extraer toda la informacion de los diferentes seguros para un data-set establecido[/]\n")
print("[bold orange1]Asegurate de tener tu archivo \".xlsx\" de tu dataset y adicionalmente un archivo \".xlsx\" con proxys\n¡Todo al mismo nivel que este script! Si tienes errores de formato revisa los requerimentos del excel con \"d\"\n")
print("[bold light_steel_blue]Selecciona una opcion:\na) Tomar todos los datos del excel\nb) Tomar \"n\" elementos del excel\nc) Toma solo el primer elemento del excel\nd) Revisar estructura del excel\ns) Salir")
menu=""
while (menu!="s"):
  # -- Recoleccion de opciones --
  option=input(">> ")
  # -- Salida del sistema --
  if option.strip().lower()=="s":
    break

  # -- Procesamiento total de los elementos --
  if option.strip().lower()=="a":
    n_procesos=multiprocessing.cpu_count()
    with Status("[bold bright_green]Procesando datos en paralelo...", spinner="dots") as status:
        resultado_final=procesamiento_paralelo(dataset_df, n_procesos)

    print(f"[bold bright_green]Total de registros procesados: {len(resultado_final)}")
    # -- Escritura de datos --
    with open(f"./assets/total_elementos.json", "w") as file:
      json.dump(resultado_final, file, indent=2, ensure_ascii=False)
    print(f"[bold bright_green]guardados en ./assets/total_elementos.json")

    break

  # -- Procesamiento parcial de los elementos --
  if option.strip().lower()=="b":
    total_data=[]
    n=input("Rango de alcanze (numero entero)\n")
    df_slice=dataset_df.head(int(n))
    n_procesos=multiprocessing.cpu_count()
    with Status("[bold bright_green]Procesando datos en paralelo...", spinner="dots") as status:
        resultado_final=procesamiento_paralelo(df_slice, n_procesos)

    print(f"[bold bright_green]Total de registros procesados: {len(resultado_final)}")
    # -- Escritura de datos --
    with open(f"./assets/{n}_elementos.json", "w") as file:
      json.dump(resultado_final, file, indent=2, ensure_ascii=False)
    print(f"[bold bright_green]guardados en ./assets/{n}_elementos.json")
    break

  # -- Procesamiento de un unico dato --
  if option.strip().lower()=="c":
    start_time=time.perf_counter()
    row=dataset_df.iloc[0]
    print(f"[bold cyan]{row}[/]")
    modelo=row["Versión Autocompara "]
    ano=int(row["Año Mod"])
    genero=generos[row["Género"]]
    nacimiento=formatear_fecha(str(row["Fecha Nacimiento"]))
    nombre=obtener_nombre_unisex()
    cp=str(row["CP"])
    email="foyagev912@ofular.com"
    telefono="524385654784"

    # -- Inicio de parametros en navegador y recuperacion de informacion --
    driver=init_browser()
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
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    driver.quit()
    # -- Escritura de datos --
    with open(f"./assets/{id_data}.json", "w") as file:
      json.dump(combinado, file, indent=2, ensure_ascii=False)
    print(combinado)
    archivo_excel = json_to_excel(combinado, "./assets/reporte_seguros.xlsx")
    print(f"[bold green]Archivo Excel generado: {archivo_excel}[/]")

    # -- Escritura de tiempo
    end_time=time.perf_counter()
    elapsed=end_time - start_time
    minutes=int(elapsed // 60)
    seconds=elapsed % 60
    print(f"\n[bold green]Tiempo total de ejecución: {minutes} min {seconds:.2f} seg[/]")

    break

  # -- Procesamiento de un unico dato --
  if option.strip().lower()=="x":
    start_time=time.perf_counter()
    total_data=[]
    # 1) Arrancamos el navegador UNA vez
    driver = init_browser()
    try:
      for i in range(len(dataset_df)):
        row = dataset_df.iloc[i]
        print(f"[bold cyan]Procesando fila {i+1}/{len(dataset_df)}: {row.to_dict()}[/]")

        # 2) Navegar al punto de partida (por ejemplo, la página de cotización)
        driver.get("https://www.autocompara.com")  
        WebDriverWait(driver, 20).until_not(
            lambda d: any(kw in d.title.lower() for kw in ["cloudflare","security","captcha"])
        )

        # 3) Extraer parámetros de la fila
        modelo    = row["Versión Autocompara "]
        ano       = int(row["Año Mod"])
        genero    = generos[row["Género"]]
        nacimiento= formatear_fecha(str(row["Fecha Nacimiento"]))
        nombre    = obtener_nombre_unisex()
        cp        = str(row["CP"])
        email     = "foyagev912@ofular.com"
        telefono  = "524385654784"

        # 4) Ejecutar tu flujo de inserción y extracción
        insert_auto(driver, ano, modelo)
        insert_data(driver, genero, nacimiento, nombre, cp, email, telefono)
        aseguradoras    = get_aseguradoras(driver)
        id_data, data   = extract_informacion(driver, aseguradoras)
        row_dict        = row.to_dict()

        combinado = {
          id_data: {
            **row_dict,
            **data
          }
        }
        total_data.append(combinado)

        # 5) Limpiar sólo el estado de la página, SIN cerrar el navegador
        driver.execute_script("localStorage.clear(); sessionStorage.clear();")
        driver.delete_all_cookies()

        # 6) Pausa entre iteraciones para no saturar
        time.sleep(60)

    finally:
      # 7) Al acabar todas las filas, cerramos el navegador
      driver.quit()

    # 8) Guardar resultados
    for registro in total_data:
      for id_data, contenido in registro.items():
        with open(f"./assets/{id_data}.json", "w") as f:
          json.dump(contenido, f, indent=2, ensure_ascii=False)

    # (si quieres un sólo Excel con todo:)
    archivo_excel = json_to_excel(total_data, "./assets/reporte_seguros.xlsx")
    print(f"[bold green]Archivo Excel generado: {archivo_excel}[/]")

    # 9) Informe de tiempo
    end_time = time.perf_counter()
    elapsed  = end_time - start_time
    minutes  = int(elapsed // 60)
    seconds  = elapsed % 60
    print(f"\n[bold green]Tiempo total de ejecución: {minutes} min {seconds:.2f} seg[/]")

    break

  if option.strip().lower()=="d":
    # -- Documentacion sobre la estrucutra del excel --
    print("[bold light_steel_blue]Este apartado es una pequeña documentacion para poder estar informado sobre la estructura del data set[/]")
    print("[bold light_steel_blue]para metodos practicos tu data-set debe tener minimamente estas columnas y bajo la misma estructura:[/]")
    print(f"[bold light_sky_blue1]{tabulate(dataset_cols, headers=['Campo', 'Descripción'], tablefmt='fancy_grid')}[/]")
    print()
    print("[bold light_steel_blue]Para el excel de proxys (opcional pero super util)")
    print(f"[bold light_sky_blue1]{tabulate(proxy_cols, headers=['Campo', 'Descripción'], tablefmt='fancy_grid')}[/]")
    print("[bold orange1]Si tienes mas dudas revisa el README.md[/]")