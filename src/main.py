#╔══════════════════════════╗ 
#║ Importacion de librerias ║ 
#╚══════════════════════════╝ 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
import random
import re
import time
from rich import print
import requests

#╔══════════════════════════════════╗ 
#║ Funciones y datos de uso general ║ 
#╚══════════════════════════════════╝ 
chrome_driver_path="/usr/local/bin/chromedriver"
def test_proxy(proxy_ip):
  # -- Verifica funcionalidad del proxy --
  try:
    response = requests.get(
      "http://httpbin.org/ip",
      proxies={"http": proxy_ip, "https": proxy_ip},
      timeout=10
    )
    return response.ok
  except:
    return False

#╔════════════════════════════════════════════════════════╗
#║ Funcion para inicio de sesion en el navegador          ║
#║  ° Inicia el navegador y su driver como controlador    ║
#║  ° Navegamos a la pagina de "autocompara" de santander ║
#║  ° Elimina el "div" de seguridad con id "sec-overlay"  ║
#╚════════════════════════════════════════════════════════╝
def init_web(ip: str):
  options = Options()
  
  # -- User-Agent actualizado (Chrome 120+) --
  user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  options.add_argument(f"user-agent={user_agent}")
  
  # -- Configuración esencial --
  options.add_argument("--disable-blink-features=AutomationControlled")
  options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--window-size=1366,768")

  # -- Proxy (solo si pasa test) --
  if ip and test_proxy(ip):
    options.add_argument(f"--proxy-server={ip}")
    print(f"[green]proxy activo: {ip}[/]")
  else:
    print("[yellow]sin proxy[/]")

  service=Service(executable_path=chrome_driver_path)
  driver=webdriver.Chrome(service=service, options=options)
  
  # -- Ocultar WebDriver --
  driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
      Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
      window.chrome = {runtime: {}};
    """
  })

  try:
    driver.get("https://www.autocompara.com")
    # -- Esperar hasta que el título NO contenga palabras clave de bloqueo --
    WebDriverWait(driver, 20).until_not(lambda d: any(kw in d.title.lower() for kw in ["cloudflare", "security", "captcha"]))
      
  except Exception as e:
    print(f"[red]error navegación: {str(e)}[/]")
    driver.quit()
    return None

  try:
    # -- eliminacion de overlay
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "sec-overlay")))
    driver.execute_script("document.getElementById('sec-overlay').remove()")
  except:
    pass

  return driver

#╔════════════════════════════════════════════════════════╗
#║ Funcion para insertar el año del auto                  ║
#║  ° Posicionamiento del driver en el input              ║
#║  ° Digitamos el año del modelo (caracter por caracter) ║
#╚════════════════════════════════════════════════════════╝
def insert_year(driver, año: int):
  try:
    input_year=WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "year")))

    # -- Simulamos una espera de tiempo natural --
    time.sleep(0.5)

    # -- Limpiamos los valores default --
    input_year.clear()

    # -- Introducimos el año caracter a caracter --
    for char in str(año):
      input_year.send_keys(char)
      # -- Pausa entre caracteres --
      time.sleep(0.1)

    print(f"[bold cyan]año {año} insertado correctamente[/]")
    return True
  except TimeoutException:
    print("[bold red]tiempo de espera agotado, no se encontro el elemento con id 'year'[/]")
    return False
  except NoSuchElementException:
    print("[bold red]el elemento con id 'year' no existe en la pagina[/]")
    return False
  except Exception as e:
    print(f"[bold red]error inesperado: {str(e)}[/]")
    return False

#╔════════════════════════════════════════════════════════╗
#║ Funcion para busqueda de modelo                        ║
#║  ° Posicionamiento del driver en el input              ║
#║  ° Digitamos el año del modelo (caracter por caracter) ║
#╚════════════════════════════════════════════════════════╝
def insert_model(driver, texto: str):
  try:
    input_container=WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ng-input")))

    # -- Centrado de elemento para evitar sobre ajuste --
    driver.execute_script(
      """arguments[0].scrollIntoView({
        behavior: 'auto',
        block: 'center',
        inline: 'center'
      });""",
      input_container
    )
    time.sleep(0.5)

    # -- Hacemos click en el elemento --
    driver.execute_script("arguments[0].click();", input_container)

    # -- Localizamos el input --
    input_field=WebDriverWait(driver, 5).until(
      EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ng-input input"))
    )

    # -- Escritura con validacion de estado y formato --
    value=texto.upper() 
    for char in texto:
      input_field.send_keys(char)
      time.sleep(random.uniform(0.1, 0.25))
      current_value = input_field.get_attribute("value").upper()
      if char not in current_value:
        raise ValueError(f"Carácter '{char}' no detectado. Valor actual: {current_value}")
      
    WebDriverWait(driver, 10).until(lambda d: texto in d.find_element(By.CSS_SELECTOR, "div.ng-input input").get_attribute("value").upper())

    print(f"[bold cyan]busqueda exitosa para: {value}[/]")
    return True
  
  except Exception as e:
    print(f"[bold red]fallo en busqueda: {str(e)}")
    try:
      driver.execute_script("""
        document.querySelector('ng-select#search').click();
        document.querySelector('ng-select#search input').value = arguments[0];
        document.querySelector('ng-select#search input').dispatchEvent(new Event('input'));
      """, texto)
      print(f"[bold yellow]usando fallback JS para: {texto}[/]")
      return True
    except:
      return False
    
#╔════════════════════════════════════════════════════════╗
#║ Funcion para la seleccion del modelo de auto           ║
#║  ° Posicionamiento del driver en el select             ║
#║  ° Compara el texto del modelo con la opcion           ║
#║  ° Selecciona la opcion si llega a coincidir           ║
#╚════════════════════════════════════════════════════════╝
def select_model(driver, texto: str):
  try:
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ng-dropdown-panel[id^='a']")))

    # -- Localizamos el contenedor scrollable --
    options = driver.find_elements(By.CSS_SELECTOR, "div.ng-option-child:not(.ng-optgroup)")

    # -- Buscamos la opcion deseada con scroll --
    find=False
    for option in options:
      try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
        # -- Optenemos el texto ignorando elementos hijos --
        texto_option=option.find_element(By.CSS_SELECTOR, "div.vehicle-data-home").get_attribute("textContent").strip()
        if texto_option.lower()==texto.lower():
          # -- Click para evitar problemas de overlay --
          driver.execute_script("arguments[0].click();", option)
          print(f"[bold cyan]opcion seleccionada: {texto_option}[/]")
          find=True
          break
      except Exception as e:
        print(f"[bold red]error durante iteracion de opciones: {str(e)}[/]")
        continue
    if not find:
      # -- Usamos una opcion default
      print("[bold yellow]Opción no encontrada, usando alternativa...[/]")
      options[0].click()
    return True
  except Exception as e:
    print(f"[bold red]error general: {str(e)}[/]")
    return False
  
#╔════════════════════════════════════════════════════════╗
#║ Funcion para la seleccion del modelo de auto default   ║
#║  ° Posicionamiento del driver en el select             ║
#║  ° Selecciona la opcion                                ║
#╚════════════════════════════════════════════════════════╝
def seleccionar_opcion_alternativa(driver, texto: str):
  try:
    option=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
      By.XPATH,
      f"//div[contains(@class, 'ng-option') and not(contains(@class, 'ng-optgroup'))]//div[contains(@class, 'vehicle-data-home') and normalize-space()='{texto}']/ancestor::div[contains(@class, 'ng-option')]"
    )))

    # -- Scroll a elemento y click --
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", option)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", option)
    return True
  except Exception as e:
    print(f"[bold red]error en metodo alternativo: {str(e)}[/]")
    return False
  
#╔════════════════════════════════════════════════════════╗
#║ Funcion de uso unico para click de boton "continuar "  ║
#║  ° Posicionamiento del driver en el botton             ║
#║  ° Click                                               ║
#╚════════════════════════════════════════════════════════╝
def click_continuar(driver):
  try:
    boton=WebDriverWait(driver, 15).until(EC.element_to_be_clickable((
      By.XPATH, 
      "//button[contains(@class, 'btn-gradient') and .//text()[contains(., 'Continuar')]]"
    )))

    # -- Scroll al bton para asegurar visibilidad --
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
    driver.execute_script("arguments[0].click();", boton)

    print("[bold cyan]boton continuar clickeado exitosamente[/]")
    return True
  except Exception as e:
    print(f"[bold red]error al hacer clic en continuar: {str(e)}[/]")
    return False
  

#############################################################
# LAS SIGUIENTES FUNCIONES CORRESPONDEN AL LLENADO DE DATOS #
# DE LOS FORMULARIOS DE DATOS PERSONALES                    #
#############################################################

#╔════════════════════════════════════════════════════════╗
#║ Funcion de uso unico para seleccion de genero          ║
#║  ° Posicionamiento del driver en el botton             ║
#║  ° Click                                               ║
#╚════════════════════════════════════════════════════════╝
def select_gender(driver, genero: str):
  try:
    selectores={
      "Hombre": {
        "xpath": "//label[contains(@class, 'male') and normalize-space()='Hombre']",
        "css": "label.male"
      },
      "Mujer": {
        "xpath": "//label[contains(@class, 'female') and normalize-space()='Mujer']",
        "css": "label.female"
      }
    }
    if genero not in selectores:
      raise ValueError(f"[bold purple]opcion invalida: {genero}. Use 'Hombre' o 'Mujer'[/]")
    
    # -- Localizacion de elemento --
    elemento=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
      By.XPATH, 
      selectores[genero]["xpath"]
    )))

    # -- Scroll y Click para evitar problemas de overlay
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)
    driver.execute_script("arguments[0].click();", elemento)

    # -- Verificar selecion --
    input_radio=elemento.find_element(By.TAG_NAME, "input")
    if input_radio.is_selected():
      print(f"[bold cyan]genero seleccionado correctamente {genero}[/]")
      return True
    else:
      print(f"[bold red]error, el radio button no se marco[/]")
      return False
  except Exception as e:
    print(f"[bold red]error seleccionando genero: {str(e)}[/]")
    # -- Buscamos el boton por css --
    try:
      elemento=driver.find_element(By.CSS_SELECTOR, selectores[genero]["css"])
      elemento.click()
      return True
    except:
      print("[bold red]error con el selector en css[/]")
      return False
    
#╔════════════════════════════════════════════════════════╗
#║ Funcion de ingreso de fecha de nacimiento              ║
#║  ° Posicionamiento del driver en el input              ║
#║  ° Digitamos la fecha de nacimiento por caracter       ║
#║  * NOTA: Importante reformatear la fecha               ║
#╚════════════════════════════════════════════════════════╝
def insert_date(driver, fecha: str):
  try:
    campo_fecha=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "date")))

    # -- Limpieza de campo de valores basura --
    driver.execute_script("arguments[0].value = '';", campo_fecha)
    campo_fecha.clear()
    time.sleep(0.5)

    for i, char in enumerate(fecha):
      campo_fecha.send_keys(char)
      current_value=campo_fecha.get_attribute("value")
      # -- Validamos el formato mientras se escribe
      if i in [2, 5]:
        if len(current_value) <= i or current_value[i] != "/":
          driver.save_screenshot(f"error_formato_{i}.png")
          raise ValueError(f"[bold red]Formato inválido en posición {i+1}")
      time.sleep(0.1)

    WebDriverWait(driver, 5).until(lambda d: d.find_element(By.ID, "date").get_attribute("value").replace("/", "") == fecha.replace("/", ""))

    print(f"[bold cyan]fecha ingresada correctamente {fecha}[/]")
    return True
  except ElementNotInteractableException:
    # -- El plan B es usar JavaScript para forzar la entrada --
    driver.execute_script(
      """
      const input = document.getElementById('date');
      input.value = arguments[0];
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      """,
      fecha 
    )
    print(f"[bold purple]fecha ingresada mediante JavaScript[/]")
    return True
  except Exception as e:
    print(f"[bold red]error ingresando fecha: {str(e)}")
    driver.save_screenshot("error_fecha.png")
    return False
  
#╔════════════════════════════════════════════════════════╗
#║ Funcion de llenado de datos personales                 ║
#║  ° Posicionamiento del driver en el form               ║
#║  ° Digitamos nombre, cp, correo y numero por caracter  ║
#╚════════════════════════════════════════════════════════╝
def insert_personal_data(driver, nombre: str, codigo_p: str, email: str, telefono: str):
  try:
    campos={
      "name": {
        "valor": nombre,
        "validacion": lambda x: len(x.split()) >= 1
      },
      "cp": {
        "valor": codigo_p,
        "validacion": lambda x: x.isdigit() and len(x) == 5
      },
      "email": {
        "valor": email,
        "validacion": lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x)
      },
      "phone": {
        "valor": telefono,
        "validacion": lambda x: x.isdigit() and len(x) in [10, 12]
      }
    }

    # -- Llenado de cada campo caracter a caracter --
    for campo_id, config in campos.items():
      # -- Validacion de formato --
      if not config["validacion"](config["valor"]):
        raise ValueError(f"[bold red]formato invalido para {campo_id}: {config['valor']}")
      # -- Limpieza de campo
      elemento=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, campo_id)))
      elemento.clear()

      # -- Simulacion de escritura humana --
      for char in config["valor"]:
        elemento.send_keys(char)
        time.sleep(0.05)

    print("[bold cyan]todos los campos llenados correctamente")
    return True
  except Exception as e:
    print(f"[bold red]error en llenado de datos: {str(e)}")
    driver.save_screenshot("error_datos_personales.png")
    return False
  
#╔════════════════════════════════════════════════════════╗
#║ Funcion de uso unico para click de cotizacion          ║
#║  ° Posicionamiento del driver en el botton             ║
#║  ° Click para la generacion de la cotizacion           ║
#╚════════════════════════════════════════════════════════╝
def click_cotizar(driver):
  try:
    boton=WebDriverWait(driver, 25).until(EC.element_to_be_clickable((
      By.XPATH, 
      "//button[contains(@class, 'btn-gradient') and contains(., 'Cotizar')]"
    )))

    # -- Simulacion de uso Humano --
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", boton)
    time.sleep(random.uniform(0.5, 1.5))

    # -- Click con Java script para evitar interceptaciones --
    driver.execute_script("arguments[0].click();", boton)
    print("[bold cyan]click en cotizar realizado[/]")

    # -- Esperamos la carga prolongada (conbinacion de enfoques)
    try:
      WebDriverWait(driver, 40).until(lambda d: any([
        len(d.find_element(By.CSS_SELECTOR, "div.resultado-cotizacion"))>0,
        "resultado" in d.current_url,
        d.execute_script("return document.readyState")=="complete"
      ]))
    except:
      # -- Espera de respaldo --
      time.sleep(10)
      if "cotizacion" not in driver.current_url:
        raise TimeoutError("[bold red] la pagina no termino de cargar[/]")
    
    print("[bold cyan]pagina de resultados cargada exitosamente")
    return True
  except Exception as e:
    print(f"[bold red]error final: {str(e)}[/]")
    # -- Diagnostico de error --
    print("[bold purple]estado actual:[/]")
    print(f"[bold purple]- URL: {driver.current_url}[/]")
    print(f"[bold purple]- titulo: {driver.title}[/]")
    print(f"[bold purple]- ReadyState: {driver.execute_script('return document.readyState')}[/]")
    driver.save_screenshot("error_final.png")
    return False
  
#╔════════════════════════════════════════════════════════╗
#║ Funcion para apertura de modal y observar informacion  ║
#║  ° Posicionamiento del driver en el label              ║
#║  ° Click para la apertura del modal                    ║
#╚════════════════════════════════════════════════════════╝
def open_modal(driver):
  try:
    WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")

    # -- Localizamos el boton para el despliegue del modal --
    boton_selector=("button.btn.btn-lnk.details[acgtmevent][category='compara_y_elige'][action='informacion_seguros']")

    # -- Scroll al boton (por seguridad) --
    boton=WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, boton_selector)))
    driver.execute_script(
      "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});"
      "window.scrollBy(0, -window.innerHeight * 0.1);", 
      boton
    )
    time.sleep(random.uniform(0.3, 0.7))

    # -- click con metodos de respaldo --
    try:
      ActionChains(driver)\
        .move_to_element_with_offset(boton, 5, 5)\
        .pause(random.uniform(0.1, 0.3))\
        .click()\
        .perform()
    except:
      # -- Fallback con JavaScript --
      driver.execute_script("arguments[0].click();", boton)
    
    # -- Espera del modal --
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal-content")))
    WebDriverWait(driver, 10).until(lambda d: "coberturas" in d.page_source.lower())

    print("[bold cyan]modal de coberturas abierto correctamente[/]")
    return True
  except TimeoutException:
    print("[bold red]error tiempo de espera execido para el modal[/]")
    driver.save_screenshot("error_modal_timeout.png")
    return False
  except Exception as e:
    print(f"[bold red]error al abrir el modal: {str(e)}[/]")
    driver.save_screenshot("error_modal_general.png")

    # -- intentar cerrar overlays inesperados --
    try:
      driver.execute_script("""
        const modals = document.querySelectorAll('div.modal-backdrop');
        modals.forEach(modal => modal.remove());
        document.body.classList.remove('modal-open');
      """)
    except:
      pass

    return False

"""
Ejemplo de ejecución
ip="51.81.245.3:17981"
driver=init_web(ip)
insert_year(driver, 2015)
insert_model(driver, "AVEO LS A STD 1.6L 4CIL 4PTAS")
select_model(driver, "AVEO LS A STD 1.6L 4CIL 4PTAS")
click_continuar(driver)
select_gender(driver,"Hombre")
insert_date(driver, "16072002")
insert_personal_data(driver, "Emilio", "52977", "foyagev912@ofular.com", "524385654784")
click_cotizar(driver)
open_modal(driver)
"""

#############################################################
# LAS SIGUIENTES FUNCIONES CORRESPONDEN A LA EXTRACCION DE  #
# LA INFORMACION DE LA CONTIZACION.                         #
#############################################################

#╔═══════════════════════════════════════════════════════════╗
#║ Funcion para interactuar con el componente ng-select para ║
#║ desplegar sus opciones.                                   ║
#║  ° Toma intentos para la interaccion y poscionamiento     ║
#║  ° Despliega las opciones de seguros                      ║
#╚═══════════════════════════════════════════════════════════╝
def drop_options(driver, intentos=3):
  try:
    selector_ng_select="ng-select[name='insuaranse'].custom"
    ng_select=WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector_ng_select)))

    # -- Localizamos el area clickable --
    trigger_selector="div.ng-input[role='combobox']"
    trigger=ng_select.find_element(By.CSS_SELECTOR, trigger_selector)

    # -- Scroll preciso y seguro (evitar rastreo) --
    driver.execute_script("""
      const element = arguments[0];
      const header = document.querySelector('header') || { offsetHeight: 0 };
      const yOffset = -header.offsetHeight * 0.15;
      
      element.scrollIntoView({
          behavior: 'auto',
          block: 'center',
          inline: 'nearest'
      });
      
      window.scrollBy(0, yOffset);
    """, trigger)

    # -- Secuencia de iteracion robusta
    for intento in range(intentos):
      try:
        # -- Click con Actions para maxima precision --
        ActionChains(driver)\
          .move_to_element_with_offset(trigger, 5, 5)\
          .pause(0.25)\
          .click()\
          .pause(0.5)\
          .perform()
        
        # -- Verificar apertura --
        if trigger.get_attribute("aria-expanded") == "true":
          print("[bold cyan]dropdown desplegado[/]")
          return True
        
        # -- Fellback verificar clase de estado abierto --
        if "ng-select-opened" in ng_select.get_attribute("class"):
          print("[bold cyan]dropdown abierto (verificacion por clase)[/]")
          return True
        
        print(f"[bold yellow]intento {intento+1} - drop no abierto[/]")
      except StaleElementReferenceException:
        print("[bold yellow]elemento obsoleto, reintentando...[/]")
        trigger=ng_select.find_element(By.CSS_SELECTOR, trigger_selector)
        continue
    
    # -- Verificacion final del panel --
    panel_selector="ng-dropdown-panel.custom"
    if EC.visibility_of_element_located((By.CSS_SELECTOR, panel_selector))(driver):
      print("[bold cyan]panel detectado post-intentos[/]")
      return True
    
    raise Exception("[bold red]no se pudo desplegar el dropdown")
  except Exception as e:
    print(f"[bold red]error critico: {str(e)}")
    driver.save_screenshot("error_ng_select.png")
    return False

#╔══════════════════════════════════════════════════════════╗
#║ Funcion para obtener las aseguradoras (id y nombre)      ║
#║  ° Recupera todos los ids disponibles junto al nombre    ║
#╚══════════════════════════════════════════════════════════╝
def get_options(driver):
  try:
    panel_selector="ng-dropdown-panel.custom"
    panel=WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, panel_selector)))

    # -- Obtener todos los elementos --
    options=panel.find_elements(By.CSS_SELECTOR, "div.ng-option[id]")

    # -- Procesamiento de opciones --
    options_data=[]
    for option in options:
      try:
        option_id=option.get_attribute("id")
        name=option.find_element(By.CSS_SELECTOR, "span.ng-option-label").text.strip()

        # -- Validamos y agregamos --
        if option_id and "-" in option_id and name:
          options_data.append((option_id, name))

      except Exception as e:
        print(f"[bold yellow]error en la opcion: {str(e)}[/]")
        continue
    print(f"[bold cyan]{len(options_data)} opciones encontradas")

    return options_data
  except Exception as e:
    print(f"[bold red]error general: {str(e)}[/]")
    driver.save_screenshot("error_opciones_completas.png")
    return []
  
#╔═══════════════════════════════════════════════════════════╗
#║ Funcion para cambiar de aseguradora por medio de un id    ║
#║  ° Toma el id de entrada y se posciona sobre el elemento  ║
#║  ° Selecciona el elemento siempre y cuando el id coincida ║
#╚═══════════════════════════════════════════════════════════╝
def change_option(driver, option_id: str):
  try:
    partial_id=option_id.split("-")[-1]

    # -- Verificacion del dropdown --
    panel_selector="ng-dropdown-panel.custom"
    for _ in range(2):
      # -- Verificacion por intentos --
      try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, panel_selector)))
        break
      except:
        print("[bold yellow]reabriendo dropdown...[/]")
        if not drop_options(driver):
          raise Exception("[bold red]no se pudo abrir el dropdown[/]")
    
    # -- Busqueda por xpath para navegadores que si lo soporten --
    xpath_selector=f"//div[@role='option' and substring(@id, string-length(@id) - {len(partial_id)} + 1) = '{partial_id}']"
    option=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_selector)))

    # -- Scroll al elemento --
    ActionChains(driver)\
      .move_to_element(option)\
      .perform()
    time.sleep(0.2)

    # -- Reintentos --
    for intento in range(3):
      try:
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded()", option)
        option.click()

        # -- Verificacion alternativa --
        WebDriverWait(driver, 2).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, panel_selector)))
        print(f"[bold cyan]seleccion confirmada {option_id}[/]")
        return True
      except StaleElementReferenceException:
        print(f"[bold yellow]reintento {intento+1} - actualizando referencia...[/]")
        option=WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath_selector)))
      except Exception as e:
        print(f"[bold yellow]error en el intento {intento+1}: {str(e)}[/]")
        # -- intento por medio de JavaScript --
        driver.execute_script("arguments[0].click()", option)
    raise Exception("[bold red]maximo de intentos alcanzado[/]")
  except Exception as e:
    print(f"[bold red]fallo en {option_id}: {str(e)}[/]")
    driver.save_screenshot(f"error_{option_id.replace('-', '_')}.png")
    return False

#╔═══════════════════════════════════════════════════════════╗
#║ Funcion para la optencion del precio anual                ║
#║  ° Posicionamiento sobre elementos <p> sin hijos          ║
#║  ° Excluimos elementos ValueB                             ║
#║  ° Recuperamos el precio del seguro                       ║
#╚═══════════════════════════════════════════════════════════╝
def get_price(driver) -> str:
  try:
    xpath_selector=(
      ".//p[contains(@class, 'value') "
      # -- Excluimos elementos con hijos --
      "and not(*[not(self::text())]) "
      "and contains(., '$')]"
    )

    # -- Esperamos que los elementos cumplan con los criterior --
    precios=WebDriverWait(driver, 15).until(
      lambda d: [
        p for p in d.find_elements(By.XPATH, xpath_selector)
        if p.is_displayed() 
        and not {'valueB'}.intersection(p.get_attribute("class").split())
        and re.search(r"\$\s*\d", p.text)
      ]
    )

    # -- Priorizacion --
    elemento_correcto=None
    for p in precios:
      classes=p.get_attribute("class").split()

      # -- Primera evaluacion --
      if "valueA" in classes:
        elemento_correcto=p
        break
      if "value" in classes and not {"valueA", "valueB"}.intersection(classes):
        elemento_correcto=p
        break

    # -- Fallback controlado --
    if not elemento_correcto:
      elemento_correcto=precios[0] if precios else None
      print("[bold yellow]usando fallback de precio[/]")

    # -- Validacion final de estrcutura --
    if not elemento_correcto or elemento_correcto.find_elements(By.XPATH, "./*"):
      raise ValueError("[bold red]estrcutra de precio invalida[/]")
    
    # -- Extraccion por medio de regex --
    precio_texto=elemento_correcto.text
    match=re.search(
      r"""
      \$
      \s*
      (
          \d{1,3}
          (?:,\d{3})*
          (?:\.\d{2})?
      )
      """, 
      precio_texto, 
      re.VERBOSE
    )
    if not match:
      raise ValueError(f"[bold red]formato numerico invalido. {precio_texto}[/]")
    
    # -- Convertimos a float --
    precio_limpio=match.group(1).replace(",", "")
    precio_final=float(precio_limpio)

    return f"{precio_final:.2f}"
  except Exception as e:
    print(f"[bold red]error critico: {str(e)}[/]")
    driver.save_screenshot("error_precio_estricto.png")
    return None

#╔═══════════════════════════════════════════════════════════╗
#║ Funcion para acceder a todos los drops de informacion     ║
#║  ° Extraccion individual del elemento                     ║
#║  ° Pausas entre cada interaccion con los elementos        ║
#║  ° Iteracion e unteraccion por cada elemento              ║
#╚═══════════════════════════════════════════════════════════╝
def expand_all(driver, timeout=20, pause_between=0.5, retry_attempts=3):
  xpath_icono=(
    "//div[contains(@class, 'row-down-propertie')]"
    "//em[contains(@class, 'icon-angle-down-af')]"
    "/ancestor::div[contains(@class, 'row-down-propertie')]"
  )
  try:
    elementos=WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, xpath_icono)))
  except TimeoutException:
    print("[bold yellow]no se encontraron elementos para expandir[/]")
    return False
  
  total=len(elementos)
  print(f"[bold cyan]encontrados {total} elementos colapsados[/]")

  for index in range(total):
    for attempt in range(1, retry_attempts+1):
      try:
        # -- Re-localizar elementos por indice --
        elementos=driver.find_elements(By.XPATH, xpath_icono)
        if index>=len(elementos):
          print(f"[bold yellow]elemento {index+1} ya no existe")
          break
        boton=elementos[index]

        # -- Scroll y compensacion header --
        driver.execute_script(
          "const header = document.querySelector('header') || { offsetHeight: 0 };"
          "arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});"
          "window.scrollBy(0, -header.offsetHeight);",
          boton
        )
        
        # --Esperar a ser clickeable y clicar
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath_icono)))
        ActionChains(driver).move_to_element(boton).pause(pause_between).click().perform()

        time.sleep(pause_between)
        break
      except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException) as e:
        if attempt<retry_attempts:
          print(f"[bold yellow]reintentando elemento {index+1}, intento {attempt}/{retry_attempts}...[/]")
          time.sleep(pause_between)
          continue
        else:
          print("[bold red]no se pudo expandir el elemento {index+1} tras {retry_attempts} intentos: {e}[/]")
  
  print(f"[bold cyan]proceso completado: {total} intentos realizados[/]")
  return True

#╔═══════════════════════════════════════════════════════════╗
#║ Funcion para extraer informacion de daños materiales      ║
#║  ° Extraccion individual de la informacion                ║
#╚═══════════════════════════════════════════════════════════╝
def get_daños_materiales(driver):
  try:
    contenedor_principal=WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "card-1")))

    # -- Encontramos la seccion de "Coberturas"
    seccion_coberturas=WebDriverWait(contenedor_principal, 10).until(
      lambda d: d.find_element(
        By.XPATH,
        ".//p[@class='subtitle mb-0' and contains(text(), 'Coberturas')]/ancestor::div[contains(@class, 'cont-servicios')]"
      )
    )

    # -- Extraemos todos los elementos de la descripcion --
    coberturas=seccion_coberturas.find_elements(By.XPATH, ".//div[contains(@class, 'centrado')]/p[@class='description']")

    # -- Procesamos los resultados --
    lista_coberturas=[]
    for elemento in coberturas:
      texto=elemento.text.strip()
      if texto and texto not in lista_coberturas:
        lista_coberturas.append(texto)

    return lista_coberturas
  except Exception as e:
    print(f"[bold red]error extrayendo coberturas: {str(e)}[/]")
    driver.save_screenshot("error_coberturas.png")
    return []
  
#╔═══════════════════════════════════════════════════════════╗
#║ Funcion para extraer informacion de daños por auto        ║
#║  ° Extraccion individual de la informacion                ║
#╚═══════════════════════════════════════════════════════════╝
import uuid
def extract_informacion(driver, aseguradoras):
  id_data=str(uuid.uuid4())
  total_data={}
  for i, elemento in enumerate(aseguradoras):
    if i!=0:
      drop_options(driver)
      select_gender(driver, elemento[0])
    precio=get_price(driver)
    expand_all(driver)
    data=get_daños_materiales(driver)
    total_data[elemento[1]]={
      "precio": precio,
      "daños_materiales": data,
    }
  return id_data, {f"{id_data}": total_data}

"""
Ejemplo de uso
id_data, data=extract_informacion(driver, aseguradoras)
"""