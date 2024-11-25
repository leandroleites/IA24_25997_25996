def plot_gantt(tempos_inicio, duracao_recursos, predecessores):
    tarefas = list(tempos_inicio.keys())
    inicio = [tempos_inicio[tarefa] for tarefa in tarefas]
    duracao = [duracao_recursos[tarefa]["duracao"] for tarefa in tarefas]

    # Gerar cores distintas para cada precedência
    cores = {}
    for tarefa, dependencias in predecessores.items():
        for dep in dependencias:
            if tarefa not in cores:
                cores[tarefa] = random.choice(['#FF6347', '#8A2BE2', '#20B2AA', '#FFD700', '#FF1493', '#32CD32', '#FF8C00'])

    plt.figure(figsize=(12, 8))
    for i, tarefa in enumerate(tarefas):
        cor = cores.get(tarefa, '#00BFFF')  # Cor padrão se não houver uma cor associada
        plt.barh(tarefa, duracao[i], left=inicio[i], height=0.6, color=cor, edgecolor='black', linewidth=1.5)
        plt.text(inicio[i] + duracao[i] / 2, i, f"{inicio[i]} - {inicio[i] + duracao[i]}", 
                 ha='center', va='center', fontweight='bold', color='white', fontsize=10)

    plt.xlabel("Tempo", fontsize=14)
    plt.ylabel("Tarefas", fontsize=14)
    plt.title("Gráfico de Gantt - Planejamento das Tarefas", fontsize=16)
    plt.xticks(range(0, max(inicio) + max(duracao) + 1, 2))  # Definir intervalos de tempo
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()  # Ajustar o layout para evitar sobreposição
    plt.show()