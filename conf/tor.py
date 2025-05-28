import requests

def get_tor_ip():
  try:
    response = requests.get(
      "http://httpbin.org/ip",
      proxies={'http': 'socks5h://localhost:9050', 'https': 'socks5h://localhost:9050'},
      timeout=10
    )
    return response.json()['origin']
  except Exception as e:
    print(f"Error obteniendo IP Tor: {str(e)}")
    return None

print("IP actual de Tor:", get_tor_ip())