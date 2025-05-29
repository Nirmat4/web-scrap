import requests

def test_rotation():
    proxy = "http://brd-customer-hl_dbcb7806-zone-test_scrap:gk1x6bsjm4x9@brd.superproxy.io:33335"
    for _ in range(2):
        res = requests.get("https://lumtest.com/myip.json", proxies={"https": proxy})
        print(f"IP actual: {res.json()['ip']}")

test_rotation()