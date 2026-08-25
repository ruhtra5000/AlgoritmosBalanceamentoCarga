import statistics

# Metricas independentes do docker
def calcular_metricas(resultados, tempo_total):
    total = len(resultados)

    erros = [
        resultado
        for resultado in resultados
        if resultado["erro"]
    ]

    sucessos = [
        resultado
        for resultado in resultados
        if not resultado["erro"]
    ]

    latencias = [
        resultado["latencia"]
        for resultado in sucessos
    ]

    # Throughput
    throughput = total / tempo_total

    # Latência média
    latencia_media = statistics.mean(latencias)

    # Percentis
    latencias_ordenadas = sorted(latencias)

    p50 = calcular_percentil(latencias_ordenadas, 50)
    p95 = calcular_percentil(latencias_ordenadas, 95)
    p99 = calcular_percentil(latencias_ordenadas, 99)

    # Taxa de erro
    taxa_erro = len(erros) / total

    # Distribuição
    distribuicao = {}

    for resultado in sucessos:

        servidor = resultado["servidor"]

        distribuicao[servidor] = (
            distribuicao.get(servidor, 0) + 1
        )

    return {
        "total_requisicoes": total,
        "sucessos": len(sucessos),
        "erros": len(erros),
        "throughput": throughput,
        "latencia_media": latencia_media,
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "taxa_erro": taxa_erro,
        "distribuicao": distribuicao
    }

def calcular_percentil(valores, percentil):
    if not valores:
        return 0

    indice = (len(valores) - 1) * percentil / 100

    inferior = int(indice)
    superior = inferior + 1

    if superior >= len(valores):
        return valores[inferior]

    peso = indice - inferior

    return (
        valores[inferior]
        + peso * (
            valores[superior] - valores[inferior]
        )
    )

# Metricas dependentes do docker
def calcular_uso_medio(amostras):
    cpu_por_servidor = {}
    memoria_por_servidor = {}

    for amostra in amostras:
        servidor = amostra["Name"]

        cpu = converter_cpu(amostra["CPUPerc"])

        memoria = converter_memoria(amostra["MemUsage"])

        cpu_por_servidor.setdefault(servidor, []).append(cpu)

        memoria_por_servidor.setdefault(servidor, []).append(memoria)

    resultado = {}

    for servidor in cpu_por_servidor:

        resultado[servidor] = {
            "cpu_media": statistics.mean(
                cpu_por_servidor[servidor]
            ),

            "memoria_media": statistics.mean(
                memoria_por_servidor[servidor]
            )
        }

    return resultado

def converter_cpu(valor):
    return float(
        valor.replace("%", "")
    )

def converter_memoria(valor):
    memoria = valor.split("/")[0].strip()

    if memoria.endswith("KiB"):
        numero = float(memoria[:-3])
        return numero / 1024

    if memoria.endswith("MiB"):
        numero = float(memoria[:-3])
        return numero

    if memoria.endswith("GiB"):
        numero = float(memoria[:-3])
        return numero * 1024

    if memoria.endswith("B"):
        numero = float(memoria[:-1])
        return numero / (1024 * 1024)

    return float(memoria)