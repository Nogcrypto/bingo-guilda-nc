#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso e teste do sistema Bingo da Golden Club

Este arquivo demonstra como usar as classes e funcionalidades
do sistema de bingo programaticamente.
"""

from models import User, Room
import random
import time

def exemplo_criacao_usuarios():
    """Demonstra criação de usuários"""
    print("=== CRIAÇÃO DE USUÁRIOS ===")
    
    # Criar usuários
    usuarios = [
        User("DragonMaster"),
        User("GoldenKnight"),
        User("FireMage"),
        User("ShadowHunter"),
        User("CrystalWizard")
    ]
    
    for user in usuarios:
        print(f"Usuário criado: {user.username} (ID: {user.user_id[:8]}...)")
    
    return usuarios

def exemplo_criacao_sala():
    """Demonstra criação e gerenciamento de sala"""
    print("\n=== CRIAÇÃO DE SALA ===")
    
    # Criar sala
    sala = Room("Sala dos Dragões", "DragonMaster", max_players=10)
    print(f"Sala criada: {sala.room_name}")
    print(f"Admin: {sala.admin_username}")
    print(f"Máximo de jogadores: {sala.max_players}")
    
    return sala

def exemplo_adicionar_jogadores(sala, usuarios):
    """Demonstra adição de jogadores à sala"""
    print("\n=== ADICIONANDO JOGADORES ===")
    
    for user in usuarios:
        if sala.add_player(user):
            print(f"✅ {user.username} entrou na sala")
        else:
            print(f"❌ {user.username} não pôde entrar (sala cheia)")
    
    print(f"\nJogadores na sala: {len(sala.players)}/{sala.max_players}")
    for player in sala.players:
        admin_status = " (ADMIN)" if player.is_admin else ""
        print(f"  - {player.username}{admin_status}")

def exemplo_gerar_cartelas(sala):
    """Demonstra geração de cartelas"""
    print("\n=== GERANDO CARTELAS ===")
    
    for player in sala.players:
        player.card = sala.generate_card()
        # Marca automaticamente o centro livre
        if 'FREE' in player.card:
            player.marked_numbers.add('FREE')
        
        print(f"\nCartela de {player.username}:")
        print("  B    I    N    G    O")
        
        # Exibe cartela em formato 5x5
        for i in range(5):
            row = []
            for j in range(5):
                index = i * 5 + j
                number = player.card[index]
                if number == 'FREE':
                    row.append(" FREE")
                else:
                    row.append(f"{number:4d}")
            print("  " + "  ".join(row))

def exemplo_simular_jogo(sala):
    """Simula um jogo completo de bingo"""
    print("\n=== SIMULANDO JOGO ===")
    
    # Iniciar jogo
    if sala.start_game():
        print("🚀 Jogo iniciado!")
    else:
        print("❌ Não foi possível iniciar o jogo")
        return
    
    # Simular sorteio de números
    numeros_sorteados = 0
    max_sorteios = 30  # Limite para evitar loop infinito
    
    print("\n🎲 Sorteando números...")
    
    while numeros_sorteados < max_sorteios:
        # Sortear número
        numero = sala.draw_number()
        
        if numero is None:
            print("Todos os números foram sorteados!")
            break
        
        numeros_sorteados += 1
        print(f"Número sorteado: {numero} ({numeros_sorteados}/75)")
        
        # Marcar número nas cartelas dos jogadores
        for player in sala.players:
            if player.mark_number(numero):
                marcados = len(player.marked_numbers)
                total = len(player.card)
                print(f"  {player.username}: {marcados}/{total} marcados")
        
        # Verificar se alguém ganhou
        winner = sala.check_winner()
        if winner:
            print(f"\n🏆 BINGO! {winner.username} ganhou!")
            print(f"Números sorteados: {len(sala.numbers_drawn)}")
            break
        
        # Pequena pausa para simular tempo real
        time.sleep(0.1)
    
    if not sala.winner:
        print("\n⏰ Jogo terminou sem vencedor (limite de sorteios atingido)")

def exemplo_estatisticas_jogo(sala):
    """Exibe estatísticas do jogo"""
    print("\n=== ESTATÍSTICAS DO JOGO ===")
    
    print(f"Sala: {sala.room_name}")
    print(f"Jogadores: {len(sala.players)}")
    print(f"Números sorteados: {len(sala.numbers_drawn)}")
    print(f"Status: {'Finalizado' if sala.winner else 'Em andamento'}")
    
    if sala.winner:
        print(f"Vencedor: {sala.winner}")
    
    print("\nNúmeros sorteados:")
    if sala.numbers_drawn:
        # Agrupa por coluna (B, I, N, G, O)
        colunas = {'B': [], 'I': [], 'N': [], 'G': [], 'O': []}
        
        for num in sala.numbers_drawn:
            if 1 <= num <= 15:
                colunas['B'].append(num)
            elif 16 <= num <= 30:
                colunas['I'].append(num)
            elif 31 <= num <= 45:
                colunas['N'].append(num)
            elif 46 <= num <= 60:
                colunas['G'].append(num)
            elif 61 <= num <= 75:
                colunas['O'].append(num)
        
        for letra, numeros in colunas.items():
            if numeros:
                print(f"  {letra}: {', '.join(map(str, sorted(numeros)))}")
    
    print("\nStatus dos jogadores:")
    for player in sala.players:
        marcados = len(player.marked_numbers)
        total = len(player.card)
        porcentagem = (marcados / total) * 100 if total > 0 else 0
        status = "🏆 VENCEDOR" if player.username == sala.winner else f"{porcentagem:.1f}% completo"
        print(f"  {player.username}: {marcados}/{total} - {status}")

def exemplo_reiniciar_jogo(sala):
    """Demonstra como reiniciar um jogo"""
    print("\n=== REINICIANDO JOGO ===")
    
    sala.reset_game()
    print("✅ Jogo reiniciado!")
    print("- Números sorteados limpos")
    print("- Novas cartelas geradas")
    print("- Status resetado")
    
    # Verificar se cartelas foram regeneradas
    print("\nNovas cartelas geradas:")
    for player in sala.players:
        if player.card:
            print(f"  {player.username}: Cartela com {len(player.card)} números")

def main():
    """Função principal que executa todos os exemplos"""
    print("🎯 BINGO DA GOLDEN CLUB - EXEMPLO DE USO")
    print("=" * 50)
    
    try:
        # Executar exemplos
        usuarios = exemplo_criacao_usuarios()
        sala = exemplo_criacao_sala()
        exemplo_adicionar_jogadores(sala, usuarios)
        exemplo_gerar_cartelas(sala)
        exemplo_simular_jogo(sala)
        exemplo_estatisticas_jogo(sala)
        exemplo_reiniciar_jogo(sala)
        
        print("\n✅ Todos os exemplos executados com sucesso!")
        print("\n🌐 Para jogar online, execute: python app.py")
        print("   E acesse: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()