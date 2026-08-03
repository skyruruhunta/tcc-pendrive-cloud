import subprocess
import json
import time

LIMITE_TEMP_CPU = 75.0
INTERVALO_MONITORAMENTO = 2.0
TEMPO_ESTRESSE = "60s"

def ler_temperatura_cpu():
    try:
        res = subprocess.run(['sensors', '-j'], capture_output=True, text=True)
        dados = json.loads(res.stdout)

        if 'coretemp-isa-0000' in dados:
            for chave, valor in dados['coretemp-isa-0000'].get('Package id 0', {}).items():
                if chave.endswith('_input'):
                    return float(valor)
    except Exception as e:
        print(f"Erro ao ler sensor de temperatura: {e}")
    return None

def abortar_teste(processo, motivo):
    print(f"\n[!!!] ABORTANDO TESTE: {motivo} [!!!]")
    print("[!!!] ACIONANDO KILL-SWITCH (SIGTERM) [!!!]")

    processo.terminate()

    try:
        processo.wait(timeout=2.0)
        print("[Monitor] O processo de estresse foi encerrado via SIGTERM.")
    except subprocess.TimeoutExpired:
        print("[!!!] PROCESSO NÃO RESPONDEU. FORÇANDO SIGKILL [!!!]")
        processo.kill()
        print("[Monitor] O processo de estresse foi obliterado via SIGKILL.")

def iniciar_teste_ativo():
    print(f"INICIANDO TESTE DE ESTRESSE ({TEMPO_ESTRESSE})")
    print(f"Kill-Switch Térmico configurado para: {LIMITE_TEMP_CPU}°C\n")

    comando_stress = ['stress-ng', '--cpu', '0', '--timeout', TEMPO_ESTRESSE]
    processo = subprocess.Popen(comando_stress)

    kill_switch_acionado = False

    while processo.poll() is None:
        temp_atual = ler_temperatura_cpu()

        if temp_atual is not None:
            print(f"[Monitor] Temperatura atual da CPU: {temp_atual}°C")

            if temp_atual >= LIMITE_TEMP_CPU:
                abortar_teste(processo, f"Alerta Térmico Crítico ({temp_atual}°C)")
                kill_switch_acionado = True
                break
        else:
            abortar_teste(processo, "Falha na leitura térmica (Cegueira).")
            kill_switch_acionado = True
            break

        time.sleep(INTERVALO_MONITORAMENTO)

    if kill_switch_acionado:
        print("\nTeste abortado precocemente por segurança (Gatilho Acionado).")
    else:
        print("\nTeste concluído com sucesso. Limites térmicos não foram ultrapassados.")

if __name__ == "__main__":
    iniciar_teste_ativo()
