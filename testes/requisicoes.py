import asyncio
import time
import httpx

URL = "http://localhost:8080/"
CONCORRENCIA = 100

async def enviar_requisicao(
    cliente: httpx.AsyncClient,
    semaforo: asyncio.Semaphore,
    numero: int
):
    async with semaforo:
        inicio = time.perf_counter()

        try:
            resposta = await cliente.get(URL)
            fim = time.perf_counter()
            dados = resposta.json()

            return {
                "numero": numero,
                "status": resposta.status_code,
                "latencia": fim - inicio,
                "servidor": dados.get("servidor"),
                "tempo_simulado": dados.get("tempo_simulado"),
                "erro": False
            }

        except Exception as erro:
            fim = time.perf_counter()

            return {
                "numero": numero,
                "status": None,
                "latencia": fim - inicio,
                "servidor": None,
                "tempo_simulado": None,
                "erro": True,
                "mensagem_erro": str(erro)
            }


async def executar_carga(total_requisicoes: int):
    semaforo = asyncio.Semaphore(CONCORRENCIA)

    inicio_total = time.perf_counter()

    async with httpx.AsyncClient() as cliente:
        tarefas = [
            enviar_requisicao(cliente, semaforo, i)
            for i in range(1, total_requisicoes + 1)
        ]

        resultados = await asyncio.gather(*tarefas)

    fim_total = time.perf_counter()

    tempo_total = fim_total - inicio_total

    print(f"Requisições: {total_requisicoes}")
    print(f"Concorrência: {CONCORRENCIA}")
    print(f"Tempo total: {tempo_total:.2f}s")

    return resultados, tempo_total