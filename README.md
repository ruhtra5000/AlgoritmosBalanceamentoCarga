# Análise de desempenho de algoritmos de balanceamento de carga em servidores heterogêneos

O projeto metrifica o desempenho de algoritmos de balanceamento de carga utilizando o NGINX e o Docker, mensurando: vazão (requisições/s), latência média, P50, P95. P99, uso médio de CPU, uso médio de memória, e distribuição das requisições.

**Lembrando que, devido a limitações do NGINX e do Docker: o projeto tem garantia de funcionamento SOMENTE no Windows!**

## Algoritmos analisados
- Round Robin
- Least Connections
- IP Hash

## Execução do projeto

### Criação de ambiente virtual

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Instalação de bibliotecas

```bash
pip install -r requirements.txt
```

### Abrir Docker

Mantenha o Docker aberto durante a execução do programa.

### Executar experimentos

Os experimentos são parametrizados, ou seja, é possível escolher:
- Qtde de servidores: 1, 3 ou 6 servidores
- Algoritmos de balanceamento: `round_robin`, `least_conn` ou `ip_hash`
- Qtde de requisições enviadas: 10000 ou 100000

**Exemplo de execução de experimento:**
```bash
python testes/experimentos.py --servidores 3 --algoritmo least_conn --requisicoes 10000
```