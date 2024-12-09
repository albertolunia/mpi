from mpi4py import MPI

# Inicializando o ambiente MPI
comm = MPI.COMM_WORLD # Cria um ambiente de comunicação entre os processos.
rank = comm.Get_rank()  # Cada processo tem um identificador único chamado rank. Ele define qual "papel" o processo desempenha.
tamanho = comm.Get_size()  # O número total de processos que estão participando.

# Grafo representando os nós e os pesos das conexões
# (Exemplo: {nó: [(nó_destino, peso)]})
grafo = {
    0: [(1, 4), (2, 1)],
    1: [(0, 4), (2, 2), (3, 5)],
    2: [(0, 1), (1, 2), (3, 8)],
    3: [(1, 5), (2, 8)]
}

# Função para calcular o vetor de distâncias
def calculo_distancia_vetor(rank, grafo):
    distancias = {no: float('inf') for no in grafo}  # Inicializar com infinito
    distancias[rank] = 0  # A distância para si mesmo é 0

    for vizinho, peso in grafo[rank]:  # Atualizar distâncias para vizinhos diretos
        distancias[vizinho] = peso

    return distancias

# Algoritmo de troca de mensagens para encontrar o menor caminho
def roteamento_distribuido(grafo, rank, tamanho):
    distancias = calculo_distancia_vetor(rank, grafo)

    # Enviar e receber atualizações de distância
    for _ in range(tamanho - 1):  # Iterar até convergir
        for vizinho, _ in grafo[rank]: # Para cada vizinho do nó atual
            comm.send(distancias, dest=vizinho) # O vetor de distâncias atual do nó (processo) é enviado para o nó vizinho
            vizinho_distancias = comm.recv(source=vizinho) # Recebe o vetor de distâncias do nó vizinho

            # Atualizar vetor de distâncias
            for no, distancia in vizinho_distancias.items(): # Para cada nó e sua distância no vetor recebido
                if distancias[no] > distancias[vizinho] + distancia:
                    distancias[no] = distancias[vizinho] + distancia
                    print(f"Processo {rank}, atualizando distancia do no {rank} ao {no} para {distancias[no]}")

    return distancias

# Executar o algoritmo
if __name__ == "__main__":
    if rank in grafo:
        resultado = roteamento_distribuido(grafo, rank, tamanho)
        print(f"Processo {rank}, vetor de distancias: {resultado}\n")
