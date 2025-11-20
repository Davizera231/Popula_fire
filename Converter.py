import pandas as pd 

CSV_FILE = r"C:\Users\dsand\OneDrive\Área de Trabalho\Populate_Firebase\CSV\Dados.xlsx"

def LerCsv():
    print("Iniciando Leitura do CSV...")
    
    Document = pd.read_excel(CSV_FILE)

    print(f"{(Document.to_string())} Registros encontrados no arquivo Excel.")


if __name__ == "__main__":
    LerCsv()