import time
import json
import logging
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



load_dotenv() 

logging.basicConfig(
    filename="cortes_aysa.log",   
    filemode="a",        
    encoding="utf-8",        
    level=logging.INFO,     
    format="%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"                          
)

def get_aysa_status(client_number: int):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
 
    try:
        driver.get("https://aysa.com.ar/usuarios/interrupcion_servicio/cortes_de_servicio_de_agua")
 
        time.sleep(5)
        campo_cuenta = driver.find_element(By.XPATH, "//input[@id='cuenta']")
        campo_cuenta.send_keys(client_number)
 
        time.sleep(4)
        boton_buscar = driver.find_element(By.XPATH, "//button[@id='btnSearch']")
        boton_buscar.click()
 
        time.sleep(10)
 
        logs = driver.get_log("performance")
        request_ids = set()
 
        for entry in logs:
            message = json.loads(entry["message"])["message"]
            if message.get("method") == "Network.responseReceived":
                params = message["params"]
                url = params["response"]["url"]
                if "aysaCuentaEnCorte" in url:
                    request_ids.add(params["requestId"])
                    print(f"URL detectada: {url}")
 
        for request_id in request_ids:
            try:
                response = driver.execute_cdp_cmd(
                    "Network.getResponseBody", {"requestId": request_id}
                )
                json_body = json.loads(response["body"])
                
                with open("aysa_results.json", "w") as f:
                    f.write(str(json_body))
            except Exception as e:
                logging.error(f"No se pudo obtener el body del request {request_id}: {e}")
 
    finally:
        logging.info("Finished execution of check")
        driver.quit()


if __name__ == "__main__":
    client_id = os.getenv("CLIENT_ID")
    logging.info(f"Starting with client {client_id}")
    get_aysa_status(client_id)


