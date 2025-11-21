## Popula Firebase – Automação de Importação de Dados para o Firestore 

* Este projeto tem como objetivo automatizar a leitura de um arquivo Excel, convertê-lo para CSV e, em seguida, popular um banco de dados Firebase Firestore, garantindo que nenhum CNPJ seja duplicado. 

#
## Funcões do Sistema

* Leitura de arquivo .xlsx
* Conversão automática para .csv
* Barra de progresso realista utilizando tqdm
* Leitura do CSV já convertido
* Verificação de registros existentes com base no CNPJ
* Inserção automática no Firebase apenas para novos documentos
* Operação segura, rápida e automatiza

#
## Tecnologias Utilizadas

### Linguagem 
* Python 3.10+ 

### Bibliotecas 
* Pandas - manipulação de planilhas e CSV
* firebase-admin - integração com firebase
* tqdm - barra de progresso
* time - medição de tempo
* os - manipulação de arquivos

### Banco de dados 
* Firebase Firestore

#
## Estrutura dos arquivos
```
C:.
│   .gitignore
│   Converter.py
│   Popula_Firebase.py
│   README.md
│   serviceAccount.json
│
├───CSV
│       Dados.xlsx
│
└───__pycache__
        Converter.cpython-314.pyc
```

#
## Pré-requisitos 

* Python 3.10+
* Pip
* Conta Firebase
* Firebase Firestore habilitado
* Arquivo "serviceAccount.json" dentro do projeto

# 
## Instalação das Dependências 

```
pip install pandas firebase-admin tqdm 
```

# 
## Como Rodar o Projeto

* Configure seu arquivo serviceAccount.json
* Coloque seu arquivo Dados.xlsx no caminho configurado
* Execute: 
```
python Popula_Firebase.py 
```

