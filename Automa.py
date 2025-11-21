from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys



def select_filter_with_retry(driver, wait, container_id, target_text, timeout=15):
    """
    Tenta selecionar um valor em um dropdown, repetindo a tentativa 
    em caso de StaleElementReferenceException.
    """
    xpath_selector = f"//div[@id='{container_id}']//select"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # 1. Espera que o elemento <select> esteja visível e clicável (Nova Referência)
            select_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector))
            )
            
            # 2. Tenta interagir (Seleção)
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


def wait_for_qlik_overlay_to_disappear(driver, wait):
    """
    Espera explicitamente que o elemento de carregamento 'body_load' e o throbber do Qlik desapareçam.
    """
    print("   -> Verificando overlays de carregamento...")
    
    # 1. Espera pelo overlay principal ('body_load')
    try:
        wait.until(EC.invisibility_of_element_located((By.ID, "body_load")))
        print("   -> Overlay 'body_load' desapareceu.")
    except Exception:
        pass
    
    # 2. Espera pelo throbber (sinal de carregamento do Qlik)
    THROBBER_SELECTOR = ".qv-throbber"
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, THROBBER_SELECTOR)))
        print("   -> Throbber (carregamento Qlik) desapareceu.")
    except Exception:
        pass
        
    time.sleep(1) # Pequena pausa extra para estabilização da DOM


# --- Fluxo Principal (main) ---
def run_automation():
    # --- Configurações Principais ---
    URL = "https://infoms.saude.gov.br/extensions/SEIDIGI_DEMAS_PFPB_ENDERECOS/index.html#"
    download_dir = os.path.join(os.getcwd(), "farmacia_popular_downloads")
    
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    print(f"O arquivo será salvo em: {download_dir}")

    # Configurar o Chrome Options
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True 
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = None
    try:
        service = webdriver.ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Otimização: Define um tamanho de janela maior para evitar elementos bloqueadores em telas pequenas
        driver.set_window_size(1400, 1000) 
        driver.get(URL)

        wait = WebDriverWait(driver, 45) 
        
        # Espera que a barra de filtros esteja presente
        wait.until(EC.presence_of_element_located((By.ID, "filterBar")))
        
        # Espera inicial por overlays e throbber
        wait_for_qlik_overlay_to_disappear(driver, wait)

        # ------------------------------------------------------------------
        # --- 1. Filtrar UF (filtro_02) ---
        # ------------------------------------------------------------------
        print("Tentando selecionar o filtro UF...")
        if not select_filter_with_retry(driver, wait, "filtro_02", "SP", timeout=20):
            print("Falha ao aplicar o filtro UF. Encerrando o script.")
            return

        # ------------------------------------------------------------------
        # --- 2. Filtrar Município (filtro_03) ---
        # ------------------------------------------------------------------
        # A seleção do UF inicia um carregamento que pode tornar o próximo elemento stale.
        print("Filtro UF aplicado. Aguardando estabilização para o Município...")
        wait_for_qlik_overlay_to_disappear(driver, wait)

        print("Tentando selecionar o filtro Município...")
        if not select_filter_with_retry(driver, wait, "filtro_03", "Mogi das Cruzes/SP", timeout=20):
            print("Falha ao aplicar o filtro Município. Encerrando o script.")
            return

        print("Filtros aplicados. Aguardando atualização final da tabela...")
        wait_for_qlik_overlay_to_disappear(driver, wait)
        time.sleep(3) 
        
        # ------------------------------------------------------------------
        # --- 3. Clicar no Botão de Download (Anti-Interceptação) ---
        # ------------------------------------------------------------------
        
        print("Aguardando o botão de download...")
        download_button = wait.until(
            EC.presence_of_element_located((By.ID, "exportar_dados_tabela_01"))
        )
        
        # Mover o elemento para a vista (scrollIntoView) para garantir que não haja interceptação de rodapé
        print("   -> Rolando a visualização para o botão...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
        time.sleep(1) # Pequena pausa para a rolagem terminar
        
        # Tentativa de clique com ActionChains (mais preciso)
        try:
            ActionChains(driver).move_to_element(download_button).click().perform()
            print("Download acionado via ActionChains.")
        except ElementClickInterceptedException:
            # Tentativa de clique com JavaScript (ignora o elemento interceptor)
            print("   -> Elemento interceptado. Tentando forçar o clique com JavaScript...")
            driver.execute_script("arguments[0].click();", download_button)
            print("Download acionado via JavaScript.")
        except Exception as e:
             print(f"   -> Erro fatal ao tentar clicar no botão de download: {e}")
             return


        # --- 4. Esperar o Download Terminar ---
        
        time.sleep(5) 
        
        timeout_seconds = 60
        start_time = time.time()
        download_finished = False
        
        print("Iniciando verificação de download (máx 60s)...")
        while time.time() - start_time < timeout_seconds:
            # Verifica a ausência do arquivo temporário do Chrome (.crdownload)
            if not any(f.endswith(".crdownload") for f in os.listdir(download_dir)):
                download_finished = True
                break
            time.sleep(2)
                
        if download_finished:
            print(f"Download concluído com sucesso no diretório: {download_dir}")
        else:
            print("Aviso: O download excedeu o tempo limite ou o arquivo temporário não desapareceu.")
        
        print("Automação concluída com sucesso.")

    except Exception as e:
        print(f"\nOcorreu um erro crítico durante a automação: {e.__class__.__name__}: {e}")
        
    finally:
        if driver:
            driver.quit()
        
if __name__ == "__main__":
    run_automation()
    print("Programa finalizado.")