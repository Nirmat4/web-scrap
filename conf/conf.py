from playwright.async_api import async_playwright
from playwright_stealth import stealth_async  # Necesitas instalar playwright-stealth
import asyncio

BRIGHTDATA_HOST = "proxy_host"
BRIGHTDATA_PORT = 1234
BRIGHTDATA_USER = "user"
BRIGHTDATA_PASS = "pass"

async def init_web():
    async with async_playwright() as p:
        # Lanzar navegador Chromium (similar a Chrome)
        browser = await p.chromium.launch(headless=False)

        # Crear contexto con proxy y user-agent
        context = await browser.new_context(
            proxy={
                "server": f"http://{BRIGHTDATA_HOST}:{BRIGHTDATA_PORT}",
                "username": BRIGHTDATA_USER,
                "password": BRIGHTDATA_PASS
            },
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.5735.199 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )

        # Crear página y aplicar stealth para evitar detección
        page = await context.new_page()
        await stealth_async(page)

        # Inyectar script para redefinir navigator.webdriver y permisos (como en CDP)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: (parameters) => (
                        parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        Promise.resolve({ state: 'denied' })
                    )
                }),
            });
        """)

        # Navegar a la página
        await page.goto("https://www.autocompara.com", timeout=30000)

        # Esperar que título no contenga palabras que indiquen bloqueo
        # Si detectas bloqueo, puedes hacer retry o cerrar.
        for _ in range(10):
            title = await page.title()
            if any(kw in title.lower() for kw in ["cloudflare", "captcha", "error"]):
                print("Página bloqueada o captcha detectado, esperando...")
                await asyncio.sleep(2)
            else:
                break

        # Extraer cookies
        cookies = await context.cookies()
        csrf = None
        for cookie in cookies:
            if cookie['name'] in ('XSRF-TOKEN', 'sec_cpt'):
                csrf = cookie['value']
                break

        print("CSRF token:", csrf)

        # Inyectar headers extra si tienes csrf token
        if csrf:
            await context.set_extra_http_headers({
                "X-XSRF-TOKEN": csrf,
                "Referer": "https://www.autocompara.com/",
            })

        # Intentar eliminar overlay (si existe)
        try:
            await page.wait_for_selector("#sec-overlay", timeout=10000)
            await page.evaluate("document.getElementById('sec-overlay').remove()")
            print("Overlay de seguridad eliminado")
        except Exception as e:
            print(f"No se pudo eliminar overlay: {e}")

        return browser, context, page

# Para correr el async:
if __name__ == "__main__":
    asyncio.run(init_web())
