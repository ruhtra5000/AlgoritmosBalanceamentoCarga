import argparse
import asyncio
import subprocess
import httpx

from requisicoes import executar_carga
from metricas import calcular_metricas, calcular_uso_medio
from monitorarDocker import monitorar_docker

# Obtenção de argumentos 
parser = argparse.ArgumentParser(
    description="Executa um experimento de balanceamento de carga."
)

# Arg. 1: Qtde de servidores
parser.add_argument(
    "--servidores",
    type=int,
    default=1,
    choices=[1, 3, 6],
    help="Quantidade de servidores: 1, 3 ou 6"
)

# Arg. 2: Algoritmo de balanceamento
parser.add_argument(
    "--algoritmo",
    default="round_robin",
    choices=["round_robin", "least_conn", "ip_hash"],
    help="Algoritmo de balanceamento"
)

# Arg. 3: Qtde de requisições
parser.add_argument(
    "--requisicoes",
    type=int,
    default=10000,
    choices=[10000, 100000],
    help="Quantidade de requisicoes: 10 mil ou 100 mil"
)

args = parser.parse_args()

# Geração do upstream usado pelo NGINX 
# (indicando qtde de servidores e o algoritmo de balanceamento)
def gerar_upstream(qtde_servidores, algoritmo):
    linhas = ["upstream servidores {"]

    if algoritmo == "least_conn":
        linhas.append("    least_conn;")

    elif algoritmo == "ip_hash":
        linhas.append("    ip_hash;")

    for i in range(1, qtde_servidores + 1):
        linhas.append(f"    server servidor{i}:8000;")

    linhas.append("}")

    return "\n".join(linhas)

# Geração completa do arquivo de configuração do NGINX (com o upstream atualizado)
def gerar_nginx_conf(qtde_servidores, algoritmo):
    upstream = gerar_upstream(qtde_servidores, algoritmo)

    return f"""
events {{
}}

http {{

    {upstream}

    server {{
        listen 80;

        location / {{
            proxy_pass http://servidores;
        }}
    }}
}}
"""

# Sobrescrever arquivo nginx.conf
def salvar_nginx_conf(conteudo):
    caminho = "nginx/conf/nginx.conf"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)

# Inicia conteiners docker
def iniciar_docker():
    servicos = [
        f"servidor{i}"
        for i in range(1, args.servidores + 1)
    ]

    comando = ["docker", "compose", "up", "-d", "--build", *servicos, "nginx"]

    subprocess.run(comando, check=True)

# Aguarda o conteiner do nginx ficar disponível
async def esperar_nginx():
    url = "http://localhost:8080/"

    while True:
        try:
            async with httpx.AsyncClient() as cliente:
                resposta = await cliente.get(
                    url,
                    timeout=1
                )

                if resposta.status_code == 200:
                    print("Nginx está pronto!")
                    return

        except httpx.RequestError:
            pass

        print("Aguardando Nginx...")
        await asyncio.sleep(1)

# Para os conteiners docker
def parar_docker():
    subprocess.run(["docker", "compose", "down"], check=True)

# Imprime todas as métricas coletadas
def imprimir_metricas(metricas, uso_medio):
    print("\n================================")
    print("            RESULTADOS")
    print("================================")

    print(f"Throughput: " f"{metricas['throughput']:.2f} req/s")

    print(f"Latência média: " f"{metricas['latencia_media'] * 1000:.2f} ms")

    print(f"P50: " f"{metricas['p50'] * 1000:.2f} ms")

    print(f"P95: " f"{metricas['p95'] * 1000:.2f} ms")

    print(f"P99: " f"{metricas['p99'] * 1000:.2f} ms")

    print(f"Taxa de erro: " f"{metricas['taxa_erro'] * 100:.2f}%")

    print("\nDistribuição:")
    for servidor, quantidade in metricas["distribuicao"].items():
        print(
            f"  {servidor}: "
            f"{quantidade} requisições"
        )

    print("\nUso de CPU e Mem. por servidor:")
    for servidor, dados in uso_medio.items():
        print(
            f"{servidor}: "
            f"CPU média = {dados['cpu_media']:.2f}%, "
            f"Memória média = {dados['memoria_media']:.2f} MiB"
        )

# Main
async def main():
    print("================================")
    print("           EXPERIMENTO")
    print("================================")

    print(f"Servidores: {args.servidores}")
    print(f"Algoritmo: {args.algoritmo}")
    print(f"Requisições: {args.requisicoes}")

    amostras_docker = []

    # 1. Configurar NGINX
    conteudo = gerar_nginx_conf(args.servidores, args.algoritmo)
    salvar_nginx_conf(conteudo)

    print("Configuração do Nginx gerada.")

    # 2. Iniciar Docker e monitoramento
    iniciar_docker()

    monitor_task = asyncio.create_task(
        monitorar_docker(
            intervalo=0.5,
            resultados=amostras_docker
        )
    )

    print("Containers iniciados.")

    # 3. Aguardar NGINX
    try:
        await esperar_nginx()

    # 4. Enviar requisições
        print("Iniciando envio de requisições...")

        resultados, tempo_total = await executar_carga(args.requisicoes)

        print("Carga finalizada.")

        monitor_task.cancel()

    # 5. Calcular metricas
        print("Calculando métricas...")

        metricas_gerais = calcular_metricas(resultados, tempo_total)
        uso_medio_docker = calcular_uso_medio(amostras_docker)

        imprimir_metricas(metricas_gerais, uso_medio_docker)

    # 6. Parar Docker
    finally:
        parar_docker()

        print("Experimento finalizado.")

if __name__ == "__main__":
    asyncio.run(main())

# python testes/experimentos.py --servidores 1 --algoritmo round_robin --requisicoes 10000