import subprocess
import json

def coletar_hardware_base():
    try:
        resultado = subprocess.run(
            ['sudo', 'lshw', '-class', 'system', '-class', 'processor', '-class', 'memory', '-json'],
            capture_output=True,
            text=True,
            check=True
        )

        dados_raw = json.loads(resultado.stdout)

        hardware_base = {
            "fabricante": "Desconhecido",
            "modelo": "Desconhecido",
            "processador": "Nao encontrado",
            "ram_capacidade": "Nao encontrada"
        }

        sistema_principal = dados_raw[0] if dados_raw else {}
        hardware_base['fabricante'] = sistema_principal.get('vendor', 'Desconhecido')
        hardware_base['modelo'] = sistema_principal.get('product', 'Desconhecido')

        for item in dados_raw:
            classe = item.get('class')
            item_id = item.get('id', '')

            if classe == 'processor':
                hardware_base['processador'] = item.get('product', 'Desconhecido')

            elif classe == 'memory' and item_id == 'memory':
                tamanho_bytes = item.get('size', 0)
                if tamanho_bytes:
                    hardware_base['ram_capacidade'] = f"{round(tamanho_bytes / (1024**3), 2)} GB"

        return hardware_base

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar lshw: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print("Erro ao fazer parse do JSON retornado pelo lshw.")
        return None
    except (IndexError, KeyError) as e:
        print(f"Erro ao navegar na estrutura do JSON: {e}")
        return None

if __name__ == "__main__":
    dados = coletar_hardware_base()
    print(json.dumps(dados, indent=4))