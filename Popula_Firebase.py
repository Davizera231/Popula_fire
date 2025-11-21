import firebase_admin
from firebase_admin import credentials, firestore
from Converter import LerCsv

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

print("Firebase conectado com sucesso!")

data_base = firestore.client()

def carregar_dados_firebase():

    df = LerCsv()

    for index, row in df.iterrows():
        cnpj = str(row['CNPJ']).strip()


        doc_ref = data_base.collection('farmacias').document(cnpj)
        doc = doc_ref.get()

        if not doc.exists:
            
            dados_dict = row.to_dict()

            doc_ref.set(dados_dict)
            print(f"Documento com CNPJ {cnpj} adicionado ao Firebase.")
        else:
            print(f"Documento com CNPJ {cnpj} já existe no Firebase. Ignoranado...")


if __name__ == "__main__":
    carregar_dados_firebase()