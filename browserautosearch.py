from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException

class BrowserAutoSearch:
    def __init__(self):
        self.browser = self._initialize_browser()

    def _initialize_browser(self):
        browsers = {
            "edge": {
                "manager": EdgeChromiumDriverManager,
                "service": EdgeService,
                "options": webdriver.EdgeOptions(),
                "driver": webdriver.Edge
            },
            "chrome": {
                "manager": ChromeDriverManager,
                "service": ChromeService,
                "options": webdriver.ChromeOptions(),
                "driver": webdriver.Chrome
            },
            "firefox": {
                "manager": GeckoDriverManager,
                "service": FirefoxService,
                "options": webdriver.FirefoxOptions(),
                "driver": webdriver.Firefox
            }
        }
        # Inicializamos los navegadores
        for browser_name, browser_info in browsers.items():
            try:
                return browser_info["driver"](service=browser_info["service"](browser_info["manager"]().install()),
                                              options=browser_info["options"])
            except Exception as e:
                print(f"Error al iniciar el navegador {browser_name}: {e}")      

        raise Exception("No se pudo iniciar ningún navegador. Por favor, verifica que tengas firefox, chrome o edge instalados.")     
    
    def accept_cookies(self, button_selector):
        """Acepta el anuncio de cookies de un buscador"""
        try:
            accept_button =  WebDriverWait(self.browser, 2).until( # Edita el tiempo de espera si es necesario
                EC.element_to_be_clickable((By.ID, button_selector))
            )
            accept_button.click()
        except Exception as e:
            print(f"Error al encontrar o hacer click en el boton de aceptar cockies: {e}")

    def search_google(self, query):
        """Esta función realiza una búsqueda en Google"""
        self.browser.get("https://www.google.com")
        self.accept_cookies(button_selector="L2AGLb")

        # Encuentra el cuadro de búsqueda y envía la cadena de texto
        search_box = self.browser.find_element(By.NAME, "q")
        search_box.send_keys(query + Keys.ENTER)
        time.sleep(3)
        try:
            self.browser.find_element(By.ID, "recaptcha")
            print("¡CAPTCHA detectado! Requiere intervención.")
            input("Por favor, resuelve el CAPTCHA y presiona Enter para continuar...")
        except NoSuchElementException:
            print("No hay CAPTCHA, seguimos.")


    def google_search_results(self):
        """Extrae los resultadosd de una consulta en Google"""
        try:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.MjjYud'))
            )
        except Exception as e:
            print(f"No se cargaron los resultados a tiempo: {e}")
            return []

        results = self.browser.find_elements(By.CSS_SELECTOR, 'div.MjjYud')
        custom_results = []

        for result in results:
            try:
                cresult = {}
                cresult["title"] = result.find_element(By.CSS_SELECTOR, 'h3').text
                cresult["link"] = result.find_element(By.TAG_NAME, 'a').get_attribute('href')
                cresult["description"] = result.find_element(By.CSS_SELECTOR, 'div.VwiC3b').text 
                custom_results.append(cresult)
            except Exception as e:
                print(f"Un elemento no pudo ser extraido: {e}")
                continue         
        return custom_results

    def quit(self):
        """Cierra el navegador"""
        self.browser.quit()       
