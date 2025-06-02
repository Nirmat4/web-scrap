import requests
import re

# Configuración del proxy de Bright Data
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335  # Puerto HTTPS
PROXY_USER = "brd-customer-hl_dbcb7806-zone-test_scrap"
PROXY_PASS = "gk1x6bsjm4x9"

# Configurar proxy en formato adecuado
proxies = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
}

# URL para obtener información de IP
IP_CHECK_URL = "https://api.ipify.org?format=json"

try:
    # Realizar solicitud a través del proxy
    response = requests.get(IP_CHECK_URL, proxies=proxies, timeout=10)
    
    if response.status_code == 200:
        # Extraer IP de la respuesta
        ip_data = response.json()
        proxy_ip = ip_data.get("ip", "No encontrada")
        
        # Mostrar resultados
        print("✅ Proxy funcionando correctamente")
        print("=" * 40)
        print(f"IP del proxy: {proxy_ip}")
        print(f"Puerto usado: {PROXY_PORT}")
        print(f"Host del proxy: {PROXY_HOST}")
        print("=" * 40)
        print(f"Configuración completa: {proxy_ip}:{PROXY_PORT}")
    else:
        print(f"❌ Error en la respuesta: Código {response.status_code}")
        print(f"Detalles: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {str(e)}")
    print("Verifica:")
    print("1. Tu conexión a internet")
    print("2. Las credenciales del proxy")
    print("3. Que el puerto sea el correcto (33335 para HTTPS)")