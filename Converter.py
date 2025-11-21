import pandas as pd
import time
from tqdm import tqdm 
import os

XLSX_FILE = r"C:\Users\dsand\OneDrive\Área de Trabalho\Populate_Firebase\CSV\Dados.xlsx"
CSV_FILE = r"C:\Users\dsand\OneDrive\Área de Trabalho\Populate_Firebase\CSV\Dados.csv"

def LerCsv():
    print("Iniciando conversão e leitura...")

    inicio = time.perf_counter()

    
    df = pd.read_excel(XLSX_FILE, dtype=str)
    time.sleep(0.3)
    tqdm(total = 100).update(100)

    
    print("Convertendo para CSV...")
    for i in tqdm(range(100)):
        time.sleep(0.005)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8")

    

    df_csv = pd.read_csv(CSV_FILE, dtype=str)
    for i in tqdm(range(100)):
        time.sleep(0.005)

    fim = time.perf_counter()

    print(f"Processo concluído em {fim - inicio:.4f} segundos.")

    return df_csv
