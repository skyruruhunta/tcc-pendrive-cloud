import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

caminho_da_chave = "pendrive-cloud-tcc-firebase-adminsdk-fbsvc-1b25ef1c10.json"

try:
    print("Iniciando credenciais...")    
    cred = credentials.Certificate(caminho_da_chave)
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    dados_teste = {
        "id_maquina": "PC-TCC-MOCK-001",
        "cpu_status": "Aprovado",
        "ram_status": "Aprovado",
        "temperatura_pico_celsius": 72,
        "rede_status": "ONLINE",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    print("Tentando enviar o pacote de diagnóstico para a nuvem...")

    db.collection("diagnosticos").add(dados_teste)

    print("\n SUCESSO ABSOLUTO! Os dados foram gravados no seu Firestore.")

except Exception as e:
    print(f"\n ERRO NA CONEXÃO: {e}")