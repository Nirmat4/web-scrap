from webScraping import init_browser, extract_informacion, insert_auto, insert_data, get_aseguradoras
from rich import print
from rich.status import Status
from commons import buscar_archivos, obtener_nombre_unisex, formatear_fecha
from tabulate import tabulate

generos={
  "FEMENINO": "Mujer",
  "MASCULINO": "Hombre"
}
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

# -- Flujo principal --
print("[bold cornflower_blue]                __                                     _             [bold deep_pink2]   _____             __                  __         \n[bold cornflower_blue] _      _____  / /_        ___________________ _____  (_)___  ____ _ [bold deep_pink2]  / ___/____ _____  / /_____ _____  ____/ /__  _____\n[bold cornflower_blue]| | /| / / _ \/ __ \______/ ___/ ___/ ___/ __ `/ __ \/ / __ \/ __ `/ [bold deep_pink2]  \__ \/ __ `/ __ \/ __/ __ `/ __ \/ __  / _ \/ ___/\n[bold cornflower_blue]| |/ |/ /  __/ /_/ /_____(__  ) /__/ /  / /_/ / /_/ / / / / / /_/ /  [bold deep_pink2] ___/ / /_/ / / / / /_/ /_/ / / / / /_/ /  __/ /    \n[bold cornflower_blue]|__/|__/\___/_.___/     /____/\___/_/   \__,_/ .___/_/_/ /_/\__, /   [bold deep_pink2]/____/\__,_/_/ /_/\__/\__,_/_/ /_/\__,_/\___/_/     \n[bold cornflower_blue]                                            /_/            /____/    [bold deep_pink2]                                                    \n[/]")
print("[bold cornflower_blue]¡Bienvenido al sistema de web-scraping para autocompara de [bold deep_pink2]santander[bold cornflower_blue]![/]")
print("[bold cornflower_blue]Este es un script para poder extraer toda la informacion de los diferentes seguros para un data-set establecido[/]\n")
print("[bold orange1]Asegurate de tener tu archivo \".xlsx\" de tu dataset y adicionalmente un archivo \".xlsx\" con proxys\n¡Todo al mismo nivel que este script! Si tienes errores de formato revisa los requerimentos del excel con \"d\"\n")
print("[bold light_steel_blue]Selecciona una opcion:\na) Tomar todos los datos del excel\nb) Tomar \"n\" elementos del excel\nc) Toma solo el primer elemento del excel\nd) Revisar estructura del excel\ns) Salir")
menu=""
while (menu!="s"):
  option=input(">> ")
  if option.strip().lower()=="s":
    break
  
  if option.strip().lower()=="a":
    total_data=[]
    with Status("[bold bright_green]procesando todos los datos[/]", spinner="dots") as status:
      for idx, row in dataset_df.iterrows():
        modelo=row["Versión Autocompara "]
        ano=int(row["Año Mod"])
        genero=generos[row["Género"]]
        nacimiento=formatear_fecha(str(row["Fecha Nacimiento"]))
        nombre=obtener_nombre_unisex()
        cp=str(row["CP"])
        email="foyagev912@ofular.com"
        telefono="524385654784"

        driver=init_browser("")
        insert_auto(driver, ano, modelo)
        insert_data(driver, genero, nacimiento, nombre, cp, email, telefono)
        aseguradoras=get_aseguradoras(driver)
        id_data, data=extract_informacion(driver, aseguradoras)
        total_data.append(data)

    break

  if option.strip().lower()=="b":
    total_data=[]
    n=input("Rango de alcanze (numero entero)")
    df_slice=dataset_df.head(n)
    with Status(f"[bold bright_green]procesando los {n} datos[/]", spinner="dots") as status:
      for idx, row in df_slice.iterrows():
        modelo=row["Versión Autocompara "]
        ano=int(row["Año Mod"])
        genero=generos[row["Género"]]
        nacimiento=formatear_fecha(str(row["Fecha Nacimiento"]))
        nombre=obtener_nombre_unisex()
        cp=str(row["CP"])
        email="foyagev912@ofular.com"
        telefono="524385654784"

        driver=init_browser("")
        insert_auto(driver, ano, modelo)
        insert_data(driver, genero, nacimiento, nombre, cp, email, telefono)
        aseguradoras=get_aseguradoras(driver)
        id_data, data=extract_informacion(driver, aseguradoras)
        total_data.append(data)

    break

  if option.strip().lower()=="c":
    data=dataset_df.iloc[0]
    print(f"[bold cyan]{data}[/]")
    modelo=data["Versión Autocompara "]
    ano=int(data["Año Mod"])
    genero=generos[data["Género"]]
    nacimiento=formatear_fecha(str(data["Fecha Nacimiento"]))
    nombre=obtener_nombre_unisex()
    cp=str(data["CP"])
    email="foyagev912@ofular.com"
    telefono="524385654784"

    driver=init_browser("")
    insert_auto(driver, ano, modelo)
    insert_data(driver, genero, nacimiento, nombre, cp, email, telefono)
    aseguradoras=get_aseguradoras(driver)
    id_data, data=extract_informacion(driver, aseguradoras)
    print(data)

    break

  if option.strip().lower()=="d":
    print("[bold light_steel_blue]Este apartado es una pequeña documentacion para poder estar informado sobre la estructura del data set[/]")
    print("[bold light_steel_blue]para metodos practicos tu data-set debe tener minimamente estas columnas y bajo la misma estructura:[/]")
    print(f"[bold light_sky_blue1]{tabulate(dataset_cols, headers=['Campo', 'Descripción'], tablefmt='fancy_grid', stralign='center')}[/]")
    print()
    print("[bold light_steel_blue]Para el excel de proxys (opcional pero super util)")
    print(f"[bold light_sky_blue1]{tabulate(proxy_cols, headers=['Campo', 'Descripción'], tablefmt='fancy_grid', stralign='center')}[/]")