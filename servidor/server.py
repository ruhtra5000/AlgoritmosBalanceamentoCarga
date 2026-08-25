import asyncio
import os
import random
from fastapi import FastAPI



NOME_SERVIDOR = os.getenv("NOME_SERVIDOR", "Servidor desconhecido")

TEMPO_MIN = float(os.getenv("TEMPO_MIN", "0.1"))
TEMPO_MAX = float(os.getenv("TEMPO_MAX", "1.0"))

# Criação da API
app = FastAPI()

# Rota do tipo GET
@app.get("/")
async def home():
    # Simulação de tempo de processamento de uma requisição
    tempo = random.uniform(TEMPO_MIN, TEMPO_MAX)
    await asyncio.sleep(tempo)

    # Retorno da resposta
    return {
        "servidor": NOME_SERVIDOR,
        "tempo_simulado": tempo
    }


# Configurações de servidor rapido
# docker run -d -p 8001:8000 -e NOME_SERVIDOR=Servidor-1 -e TEMPO_MIN=0.1 -e TEMPO_MAX=0.3 servidor-python

# Configurações de servidor medio
# docker run -d -p 8002:8000 -e NOME_SERVIDOR=Servidor-2 -e TEMPO_MIN=0.3 -e TEMPO_MAX=0.6 servidor-python

# Configurações de servidor lento
# docker run -d -p 8003:8000 -e NOME_SERVIDOR=Servidor-3 -e TEMPO_MIN=0.6 -e TEMPO_MAX=1.0 servidor-python
