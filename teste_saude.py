import subprocess
import json

def extrair_temperatura_sensor(bloco_sensor):
    for chave, valor in bloco_sensor.items():
        if chave.endswith('_input'):
            return valor
    return None

def coletar_temperaturas_sistema():
    temperaturas = {}
    try:
        res_sensors = subprocess.run(['sensors', '-j'], capture_output=True, text=True, check=True)
        dados_sensores = json.loads(res_sensors.stdout)

        for chip, conteudo_chip in dados_sensores.items():
            for nome_sub_sensor, bloco in conteudo_chip.items():
                if nome_sub_sensor == "Adapter":
                    continue
                if isinstance(bloco, dict):
                    temp = extrair_temperatura_sensor(bloco)
                    if temp is not None:
                        chave_final = f"{chip}::{nome_sub_sensor}"
                        temperaturas[chave_final] = temp

    except subprocess.CalledProcessError as e:
        print(f"Erro ao ler sensores térmicos: {e.stderr}")
    except json.JSONDecodeError:
        print("Erro ao fazer parse do JSON do lm-sensors.")

    return temperaturas

def descobrir_discos():
    try:
        resultado = subprocess.run(
            ['lsblk', '-d', '-n', '-e', '7,11', '-o', 'NAME'],
            capture_output=True, text=True, check=True
        )
        linhas = resultado.stdout.strip().split('\n')
        return [linha.strip() for linha in linhas if linha.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Erro ao descobrir discos: {e}")
        return []

def extrair_temperatura_ata(dados_smart):
    tabela_atributos = dados_smart.get('ata_smart_attributes', {}).get('table', [])
    for atributo in tabela_atributos:
        if atributo.get('id') == 194:
            return atributo.get('raw', {}).get('value', 'Desconhecida')
    return 'Desconhecida'

def coletar_saude_disco(nome_disco):
    try:
        cmd_smart = ['sudo', 'smartctl', '-a', '--json', f'/dev/{nome_disco}']
        res_smart = subprocess.run(cmd_smart, capture_output=True, text=True)
        dados_smart = json.loads(res_smart.stdout)

        tipo_disco = dados_smart.get('device', {}).get('type', 'desconhecido')

        if tipo_disco == 'nvme':
            temperatura = dados_smart.get(
                'nvme_smart_health_information_log', {}
            ).get('temperature', 'Desconhecida')
        elif tipo_disco in ('ata', 'sat', 'scsi'):
            temperatura = extrair_temperatura_ata(dados_smart)
        else:
            temperatura = 'Desconhecida'

        return {
            "tipo": tipo_disco,
            "modelo": dados_smart.get("model_name", "Desconhecido"),
            "status_saude": dados_smart.get("smart_status", {}).get("passed", "Desconhecido"),
            "temperatura_celsius": temperatura
        }

    except Exception as e:
        return {"erro": str(e)}

def coletar_saude_passiva():
    saude = {
        "temperaturas": coletar_temperaturas_sistema(),
        "armazenamento": {}
    }

    discos = descobrir_discos()
    for disco in discos:
        saude['armazenamento'][disco] = coletar_saude_disco(disco)

    return saude

if __name__ == "__main__":
    dados = coletar_saude_passiva()
    print(json.dumps(dados, indent=4))