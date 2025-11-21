from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys


URL = "https://infoms.saude.gov.br/extensions/SEIDIGI_DEMAS_PFPB_ENDERECOS/index.html#"
DOWNLOAD_DIR = os.path.join(os.getcwd(), "farmacia_popular_downloads")
FILTER_STEPS = [

    ("filtro_02", "SP", "UF"),
    ("filtro_03", "Mogi das Cruzes/SP", "Município")
]



def setup_driver():
    """Configura e retorna o driver do Chrome com opções de download."""
    if not os.path.isdir(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    chrome_options = Options()
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True 
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = webdriver.ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1400, 1000) # Otimização para Anti-Interceptação
    return driver


def wait_for_ready(driver, wait):
    """Espera o carregamento inicial da página e a estabilização do Qlik/Overlays."""
    print("-> Aguardando carregamento inicial e estabilização do Qlik...")
    wait.until(EC.presence_of_element_located((By.ID, "filterBar")))
    

    for selector in ["body_load", ".qv-throbber"]:
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selector)))
        except Exception:
            pass
    time.sleep(2) 


def select_filter_with_retry(driver, wait, container_id, target_text, timeout=15):
    """(Mantido como está para evitar a StaleElementReferenceException)"""
    xpath_selector = f"//div[@id='{container_id}']//select"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            select_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector))
            )
            select_obj = Select(select_element)
            select_obj.select_by_visible_text(target_text) 
            
            print(f"   -> Seleção em '{container_id}' concluída: '{target_text}'")
            return True
        
        except StaleElementReferenceException:
            print(f"   -> Aviso: Stale element for '{container_id}'. Tentando novamente...")
            time.sleep(1) 
            continue
        
        except (TimeoutException, NoSuchElementException) as e:
            print(f"   -> Erro: Falha ao encontrar ou interagir com o filtro {container_id}: {e.__class__.__name__}")
            return False
            
        except Exception as e:
            print(f"   -> Erro inesperado ao selecionar o filtro {container_id}: {e}")
            return False

    return False 


def apply_filters(driver, wait):
    """Aplica todos os filtros definidos na lista FILTER_STEPS."""
    for container_id, value, name in FILTER_STEPS:
        print(f"-> Tentando selecionar filtro: {name} ({container_id})...")
        if not select_filter_with_retry(driver, wait, container_id, value, timeout=20):
            return False
        
    
        wait_for_ready(driver, wait)
        time.sleep(1) 
    
    return True


def click_download_button(driver, wait):
    """Localiza o botão, garante que ele esteja visível e clica usando ActionChains com fallback JS."""
    download_button_id = "exportar_dados_tabela_01"
    
    
    download_button = wait.until(
        EC.presence_of_element_located((By.ID, download_button_id))
    )
    
    
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
    time.sleep(1) 
    
    
    try:
        ActionChains(driver).move_to_element(download_button).click().perform()
        print("-> Download acionado via ActionChains.")
    except ElementClickInterceptedException:
    
        driver.execute_script("arguments[0].click();", download_button)
        print("-> Download acionado via JavaScript (Fallback).")
    except Exception as e:
        print(f"-> Erro fatal ao tentar clicar no botão de download: {e.__class__.__name__}")
        return False
        
    return True


def monitor_download():
    """Monitora o diretório de download até que o arquivo .crdownload desapareça."""
    time.sleep(5) 
    timeout_seconds = 60
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        if not any(f.endswith(".crdownload") for f in os.listdir(DOWNLOAD_DIR)):
            return True
        time.sleep(2)
            
    return False


def run_automation():
    print(f"Iniciando automação. O arquivo será salvo em: {DOWNLOAD_DIR}")
    driver = None
    try:
        driver = setup_driver()
        driver.get(URL)
        wait = WebDriverWait(driver, 45) 
        
        
        wait_for_ready(driver, wait)

        
        if not apply_filters(driver, wait):
            print("-> Automação interrompida devido a falha na aplicação de filtros.")
            return

        
        wait_for_ready(driver, wait) 
        if not click_download_button(driver, wait):
            print("-> Automação interrompida devido a falha no clique de download.")
            return
        
        
        if monitor_download():
            print("-> Download concluído com sucesso.")
        else:
            print("-> Aviso: Download excedeu o tempo limite de monitoramento.")

    except Exception as e:
        print(f"\n-> Ocorreu um erro crítico durante a automação: {e.__class__.__name__}: {e}")
        
    finally:
        if driver:
            driver.quit()
        print("Automação finalizada.")

if __name__ == "__main__":
    run_automation()