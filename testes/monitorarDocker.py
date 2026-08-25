import asyncio
import json


async def monitorar_docker(intervalo, resultados):
    while True:
        comando = [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{json .}}"
        ]

        processo = await asyncio.create_subprocess_exec(
            *comando,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await processo.communicate()

        if processo.returncode != 0:
            print(
                "Erro ao executar docker stats:",
                stderr.decode()
            )

        linhas = stdout.decode().strip().splitlines()

        for linha in linhas:
            try:
                dados = json.loads(linha)
                nome = dados["Name"]

                # Considera somente os servidores
                if nome.startswith("balanceamentocarga-servidor"):
                    resultados.append(dados)

            except json.JSONDecodeError:
                pass

        await asyncio.sleep(intervalo)