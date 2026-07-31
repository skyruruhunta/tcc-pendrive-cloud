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

        dados_raw = json.loads(resultado.stdout)[0]

        hardware_base = {
            "fabricante": dados_raw.get('vendor', 'Desconhecido'),
            "modelo": dados_raw.get('product', 'Desconhecido'),
            "processador": "Nao encontrado",
            "ram_capacidade": "Nao encontrada"
        }

        if 'children' in dados_raw:
            for node in dados_raw['children']:
                if node.get('id') == 'core' and 'children' in node:
                    for subnode in node['children']:
                        if subnode.get('class') == 'processor':
                            hardware_base['processador'] = subnode.get('product', 'Desconhecido')
                        elif subnode.get('class') == 'memory' and subnode.get('id') == 'memory':
                            tamanho_bytes = subnode.get('size', 0)
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