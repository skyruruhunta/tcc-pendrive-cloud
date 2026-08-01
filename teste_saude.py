import subprocess
import json

def extrair_temperatura(bloco_sensor):
    for chave, valor in bloco_sensor.items():
        if chave.endswith('_input'):
            return valor
    return None

def coletar_saude_passiva(disco_alvo="nvme0n1"):
    saude = {
        "temperaturas": {},
        "armazenamento": {}
    }

    try:
        res_sensors = subprocess.run(['sensors', '-j'], capture_output=True, text=True, check=True)
        dados_sensores = json.loads(res_sensors.stdout)

        for chip, conteudo_chip in dados_sensores.items():
            for nome_sub_sensor, bloco in conteudo_chip.items():
                if nome_sub_sensor == "Adapter":
                    continue
                if isinstance(bloco, dict):
                    temp = extrair_temperatura(bloco)
                    if temp is not None:
                        chave_final = f"{chip}::{nome_sub_sensor}"
                        saude['temperaturas'][chave_final] = temp

    except subprocess.CalledProcessError as e:
        print(f"Erro ao ler sensores térmicos: {e.stderr}")
    except json.JSONDecodeError:
        print("Erro ao fazer parse do JSON do lm-sensors.")

    try:
        cmd_smart = ['sudo', 'smartctl', '--info', '--health', '--json', f'/dev/{disco_alvo}']
        res_smart = subprocess.run(cmd_smart, capture_output=True, text=True)

        dados_smart = json.loads(res_smart.stdout)

        saude['armazenamento'][disco_alvo] = {
            "modelo": dados_smart.get("model_name", "Desconhecido"),
            "status_saude": dados_smart.get("smart_status", {}).get("passed", "Desconhecido"),
            "temperatura_celsius": dados_smart.get("temperature", {}).get("current", "Desconhecida")
        }
    except Exception as e:
        print(f"Erro na leitura SMART do disco {disco_alvo}: {e}")

    return saude

if __name__ == "__main__":
    dados = coletar_saude_passiva()
    print(json.dumps(dados, indent=4))
