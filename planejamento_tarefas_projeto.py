import random
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Função para carregar dados de um dataset
def carregar_dados(arquivo):
    with open(arquivo, 'r') as f:
        data = f.readlines()

    predecessores = {}
    duracao_recursos = {}
    recursos_disponiveis = {}

    # Encontrar seções
    for i, line in enumerate(data):
        if line.startswith("#Precedence relations"):
            inicio_precedencia = i + 1
        if line.startswith("#Duration and resources"):
            fim_precedencia = i
            inicio_duracao = i + 1
        if line.startswith("#Resource availability"):
            fim_duracao = i
            inicio_recursos = i + 1

    # Processar Predecessores
    for line in data[inicio_precedencia:fim_precedencia]:
        if line.strip() and not line.startswith('#') and '************************************************************************' not in line:
            partes = list(map(int, line.split()))
            predecessores[partes[0]] = partes[3:]
    
    # Processar Duração e Recursos
    for line in data[inicio_duracao:fim_duracao]:
        if line.strip() and not line.startswith('#') and '************************************************************************' not in line:
            partes = list(map(int, line.split()))
            job_id = partes[0]
            duracao_recursos[job_id] = {
                "duracao": partes[2],
                "recursos": partes[3:]
            }
    
    # Processar Recursos Disponíveis
    for line in data[inicio_recursos:]:
        if line.strip() and not line.startswith('#') and '************************************************************************' not in line:
            partes = line.split()
            recurso = partes[0]
            quantidade = int(partes[1])
            recursos_disponiveis[recurso] = quantidade

    return predecessores, duracao_recursos, recursos_disponiveis

# Função para calcular o makespan (duração total do projeto)
def calcular_makespan(agenda, duracao_recursos):
    tempos_inicio = {tarefa: 0 for tarefa in agenda}
    tempos_fim = {}

    # Inicializa todos os tempos de início com zero, incluindo os dependentes
    for tarefa in agenda:
        if tarefa not in tempos_inicio:
            tempos_inicio[tarefa] = 0
    
    for tarefa in agenda:
        inicio = tempos_inicio[tarefa]
        fim = inicio + duracao_recursos[tarefa]["duracao"]
        tempos_fim[tarefa] = fim

        # Verificar as dependências e garantir que as tarefas dependentes têm o tempo correto
        for dependente in predecessores.get(tarefa, []):
            if dependente not in tempos_inicio:
                tempos_inicio[dependente] = max(tempos_inicio.get(dependente, 0), fim)

    makespan = max(tempos_fim.values())
    return makespan

# Função CPM - Critical Path Method
def critical_path_method(predecessores, duracao_recursos):
    tempos_inicio = {tarefa: 0 for tarefa in predecessores}
    tempos_fim = {}

    # Ordenar tarefas topologicamente
    ordem_topologica = list(nx.topological_sort(grafo))

    # Forward pass
    for tarefa in ordem_topologica:
        inicio = tempos_inicio[tarefa]
        fim = inicio + duracao_recursos[tarefa]["duracao"]
        tempos_fim[tarefa] = fim
        for dependente in predecessores.get(tarefa, []):
            tempos_inicio[dependente] = max(tempos_inicio.get(dependente, 0), fim)

    makespan = max(tempos_fim.values())
    return tempos_inicio, tempos_fim, makespan

# Função de validação de recursos
def validar_recursos(tempos_inicio, duracao_recursos, recursos_disponiveis):
    alocacao_tempo = {}

    for tarefa, inicio in tempos_inicio.items():
        duracao = duracao_recursos[tarefa]["duracao"]
        recursos = duracao_recursos[tarefa]["recursos"]

        for t in range(inicio, inicio + duracao):
            if t not in alocacao_tempo:
                alocacao_tempo[t] = [0] * len(recursos_disponiveis)
            for i, r in enumerate(recursos):
                alocacao_tempo[t][i] += r
    
    for t, uso in alocacao_tempo.items():
        for i, r in enumerate(uso):
            if r > list(recursos_disponiveis.values())[i]:
                return False, t
    return True, None

# Algoritmo Genético para otimização
def algoritmo_genetico(agenda_inicial, duracao_recursos, generations=100, population_size=50):
    population = [random.sample(agenda_inicial, len(agenda_inicial)) for _ in range(population_size)]
    best_solution = None
    best_makespan = float('inf')

    for generation in range(generations):
        population.sort(key=lambda agenda: calcular_makespan(agenda, duracao_recursos))

        if calcular_makespan(population[0], duracao_recursos) < best_makespan:
            best_solution = population[0]
            best_makespan = calcular_makespan(population[0], duracao_recursos)

        # Seleção, cruzamento e mutação
        new_population = population[:10]  # Keep the top 10 solutions
        for i in range(len(population)//2):
            parent1 = population[i]
            parent2 = population[len(population)-i-1]
            crossover_point = random.randint(0, len(parent1))
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            new_population.append(child1)
            new_population.append(child2)

        population = new_population
    
    return best_solution, best_makespan

# Gráfico de Gantt com cores para cada precedência
def plot_gantt(tempos_inicio, duracao_recursos, predecessores):
    import matplotlib.pyplot as plt
    import random

    # Criar um dicionário para mapear tarefas às suas cores
    cores_tarefas = {}
    cores_usadas = ['#FF6347', '#8A2BE2', '#20B2AA', '#FFD700', '#FF1493', '#32CD32', '#FF8C00']
    cor_atual = 0

    # Atribuir cores aos predecessores e seus sucessores
    for tarefa in predecessores:
        if tarefa not in cores_tarefas:
            # Atribuir uma nova cor à tarefa predecessora
            cores_tarefas[tarefa] = cores_usadas[cor_atual % len(cores_usadas)]
            cor_atual += 1
        # Propagar a mesma cor para os sucessores diretos
        for sucessor in predecessores[tarefa]:
            cores_tarefas[sucessor] = cores_tarefas[tarefa]

    tarefas = list(tempos_inicio.keys())
    inicio = [tempos_inicio[tarefa] for tarefa in tarefas]
    duracao = [duracao_recursos[tarefa]["duracao"] for tarefa in tarefas]

    # Plotar o gráfico de Gantt
    plt.figure(figsize=(12, 8))
    for i, tarefa in enumerate(tarefas):
        cor = cores_tarefas.get(tarefa, '#00BFFF')  # Cor padrão se não houver uma cor associada
        plt.barh(i + 1, duracao[i], left=inicio[i], height=0.6, color=cor, edgecolor='black', linewidth=1.5)
        plt.text(inicio[i] + duracao[i] / 2, i + 1, f"{inicio[i]} - {inicio[i] + duracao[i]}", 
                 ha='center', va='center', fontweight='bold', color='white', fontsize=10)

    # Configurações do eixo y
    plt.yticks(range(1, len(tarefas) + 1), tarefas)  # Define os valores no eixo y de 1 em 1
    plt.gca().invert_yaxis()  # Inverte o eixo y para que a tarefa 1 fique no topo

    # Configurações do eixo x
    max_tempo = max(inicio) + max(duracao)
    plt.xticks(range(0, max_tempo + 1))  # Define os valores no eixo x de 1 em 1

    # Configurações gerais do gráfico
    plt.xlabel("Horas", fontsize=14)
    plt.ylabel("Tarefas", fontsize=14)
    plt.title("Calendario", fontsize=16)
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()  # Ajustar o layout para evitar sobreposição
    plt.show()

# Exemplo de execução
predecessores, duracao_recursos, recursos_disponiveis = carregar_dados('p01_dataset_8.txt')

# Criar o grafo de precedência
grafo = nx.DiGraph()
for tarefa, dependencias in predecessores.items():
    for dependente in dependencias:
        grafo.add_edge(tarefa, dependente)

# Rodar o CPM
tempos_inicio, tempos_fim, makespan = critical_path_method(predecessores, duracao_recursos)

# Verificar restrições de recursos
valido, conflito = validar_recursos(tempos_inicio, duracao_recursos, recursos_disponiveis)
if valido:
    print("Os recursos são válidos.")
else:
    print(f"Conflito de recursos no tempo {conflito}.")

# Rodar o algoritmo genético para otimização
best_solution, best_makespan = algoritmo_genetico(list(predecessores.keys()), duracao_recursos)
print("Melhor solução encontrada:", best_solution)
print("Makespan otimizado:", best_makespan)

# Plotar o gráfico de Gantt
plot_gantt(tempos_inicio, duracao_recursos, predecessores)
