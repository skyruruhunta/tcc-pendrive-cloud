import firebase_admin
from firebase_admin import credentials, firestore
import platform
import socket
import psutil

cred = credentials.Certificate("pendrive-cloud-tcc-firebase-adminsdk-fbsvc-1b25ef1c10.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

ram_info = psutil.virtual_memory()
ram_total_gb = round(ram_info.total / (1024 ** 3), 2)

disco_info = psutil.disk_usage('C:\\')
disco_total_gb = round(disco_info.total / (1024 ** 3), 2)
disco_livre_gb = round(disco_info.free / (1024 ** 3), 2)

dados_hardware = {
    'nome_da_maquina': socket.gethostname(),
    'sistema_operacional': platform.system(),
    'versao_os': platform.release(),
    'arquitetura': platform.machine(),
    'processador': platform.processor(),
    'memoria_ram_total_GB': ram_total_gb,
    'disco_C_total_GB': disco_total_gb,
    'disco_C_livre_GB': disco_livre_gb,
    'status_conexao': 'SUCESSO ABSOLUTO - Leitura Profunda'
}

print("Coletando dados avançados do hardware...")
for chave, valor in dados_hardware.items():
    print(f"{chave}: {valor}")

print("\nTentando enviar o pacote de diagnóstico completo para a nuvem...")
doc_ref = db.collection('diagnosticos').document('relatorio_pc')
doc_ref.set(dados_hardware)

print("Dados avançados gravados com sucesso no Firestore!")