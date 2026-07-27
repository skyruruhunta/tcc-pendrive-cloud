import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# 1. Substitua pelo nome EXATO do seu arquivo JSON baixado
caminho_da_chave = "pendrive-cloud-tcc-firebase-adminsdk-fbsvc-1b25ef1c10.json"

try:
    print("Iniciando credenciais...")
    # 2. Apresenta a sua "chave" para o Google
    cred = credentials.Certificate(caminho_da_chave)
    firebase_admin.initialize_app(cred)

    # 3. Conecta no seu banco de dados Firestore
    db = firestore.client()

    # 4. Prepara um pacote de dados de teste (um dicionário Python)
    dados_teste = {
        "id_maquina": "PC-TCC-MOCK-001",
        "cpu_status": "Aprovado",
        "ram_status": "Aprovado",
        "temperatura_pico_celsius": 72,
        "rede_status": "ONLINE",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    print("Tentando enviar o pacote de diagnóstico para a nuvem...")

    # 5. O comando mágico: Acessa a coleção e adiciona os dados
    # Equivalente a um "INSERT" no SQL
    db.collection("diagnosticos").add(dados_teste)

    print("\n✅ SUCESSO ABSOLUTO! Os dados foram gravados no seu Firestore.")

except Exception as e:
    print(f"\n❌ ERRO NA CONEXÃO: {e}")