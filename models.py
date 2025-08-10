import random
import uuid
from datetime import datetime

class User:
    def __init__(self, username):
        self.username = username
        self.user_id = str(uuid.uuid4())
        self.room = None
        self.cards = []  # Lista de cartelas
        self.marked_numbers = {}  # Dicionário {card_index: set(números_marcados)}
        self.is_admin = False
        self.created_at = datetime.now()
        self.num_cards = 1  # Número de cartelas baseado em check-ins
        self.check_ins = 0  # Número de check-ins registrados

    def set_num_cards(self, num_cards):
        """Define o número de cartelas para o jogador"""
        self.num_cards = max(1, num_cards)  # Mínimo 1 cartela
        # Inicializa os números marcados para cada cartela
        for i in range(self.num_cards):
            if i not in self.marked_numbers:
                self.marked_numbers[i] = set()

    def mark_number(self, number):
        """Marca um número em todas as cartelas do usuário"""
        marked_any = False
        for card_index, card in enumerate(self.cards):
            if number in card:
                self.marked_numbers[card_index].add(number)
                marked_any = True
        return marked_any

    def check_bingo(self, card_index=None):
        """Verifica se o usuário fez bingo em alguma cartela ou cartela específica"""
        if card_index is not None:
            # Verifica cartela específica
            if card_index < len(self.cards):
                card = self.cards[card_index]
                marked = self.marked_numbers.get(card_index, set())
                # Conta números válidos (excluindo 'FREE')
                valid_numbers = [n for n in card if n != 'FREE']
                marked_valid = [n for n in marked if n != 'FREE']
                return len(marked_valid) == len(valid_numbers)
        else:
            # Verifica todas as cartelas
            for i in range(len(self.cards)):
                if self.check_bingo(i):
                    return True
        return False

    def get_winning_cards(self):
        """Retorna lista de índices das cartelas vencedoras"""
        winning_cards = []
        for i in range(len(self.cards)):
            if self.check_bingo(i):
                winning_cards.append(i)
        return winning_cards

    def get_cards_status(self):
        """Retorna o status de todas as cartelas com números marcados"""
        cards_status = []
        for i, card in enumerate(self.cards):
            marked = list(self.marked_numbers.get(i, set()))
            cards_status.append({
                'card_index': i,
                'card': card,
                'marked': marked,
                'total_marked': len([n for n in marked if n != 'FREE']),
                'total_numbers': len([n for n in card if n != 'FREE']),
                'is_winner': self.check_bingo(i),
                'owner': self.username
            })
        return cards_status

class Room:
    def __init__(self, room_name, admin_username, max_players=50):
        self.room_name = room_name
        self.room_id = str(uuid.uuid4())
        self.admin_username = admin_username
        self.max_players = max_players
        self.players = []
        self.numbers_drawn = []
        self.is_active = False
        self.created_at = datetime.now()
        self.winner = None
        self.game_started = False
        self.player_cards_config = {}  # {username: num_cards} - Configuração de cartelas por jogador
        self.prize = ""  # Prêmio do jogo (opcional)

    def add_player(self, user):
        """Adiciona um jogador à sala"""
        if len(self.players) < self.max_players and user not in self.players:
            self.players.append(user)
            user.room = self.room_name
            # Define o primeiro jogador como admin se não houver admin
            if len(self.players) == 1:
                user.is_admin = True
                self.admin_username = user.username
            # Inicializa com 1 cartela por padrão
            self.player_cards_config[user.username] = 1
            user.set_num_cards(1)
            return True
        return False

    def remove_player(self, user):
        """Remove um jogador da sala"""
        if user in self.players:
            self.players.remove(user)
            user.room = None
            user.is_admin = False
            # Remove configuração de cartelas
            if user.username in self.player_cards_config:
                del self.player_cards_config[user.username]
            # Se o admin saiu, define um novo admin
            if user.username == self.admin_username and self.players:
                self.players[0].is_admin = True
                self.admin_username = self.players[0].username
            return True
        return False

    def set_player_cards(self, username, num_cards):
        """Define o número de cartelas para um jogador específico"""
        if username in self.player_cards_config:
            self.player_cards_config[username] = max(1, num_cards)
            # Encontra o jogador e atualiza suas cartelas
            for player in self.players:
                if player.username == username:
                    player.set_num_cards(num_cards)
                    # Se o jogo já começou, gera novas cartelas
                    if self.game_started:
                        self.generate_cards_for_player(player)
                    return True
        return False

    def transfer_admin(self, new_admin_username):
        """Transfere admin para outro jogador"""
        # Encontra o jogador atual admin
        current_admin = None
        new_admin = None
        
        for player in self.players:
            if player.is_admin:
                current_admin = player
            if player.username == new_admin_username:
                new_admin = player
        
        # Verifica se o novo admin existe na sala
        if new_admin and current_admin:
            # Remove admin do jogador atual
            current_admin.is_admin = False
            # Define novo admin
            new_admin.is_admin = True
            self.admin_username = new_admin_username
            return True
        return False

    def get_player_cards_config(self):
        """Retorna a configuração de cartelas de todos os jogadores"""
        config = []
        for player in self.players:
            config.append({
                'username': player.username,
                'num_cards': self.player_cards_config.get(player.username, 1),
                'check_ins': player.check_ins,
                'is_admin': player.is_admin
            })
        return config

    def set_prize(self, prize):
        """Define o prêmio do jogo"""
        self.prize = prize if prize else ""
        return True

    def generate_card(self):
        """Gera uma cartela única de bingo (5x5 com centro livre)"""
        card = []
        # B: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75
        ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
        
        for i, (start, end) in enumerate(ranges):
            column = random.sample(range(start, end + 1), 5)
            # Centro livre (posição 12 - meio da cartela)
            if i == 2:  # Coluna N
                column[2] = 'FREE'  # Centro livre
            card.extend(column)
        
        return card

    def generate_cards_for_player(self, player):
        """Gera cartelas para um jogador específico"""
        num_cards = self.player_cards_config.get(player.username, 1)
        print(f"[DEBUG] Gerando {num_cards} cartelas para {player.username}")
        player.cards = []
        player.marked_numbers = {}
        
        for i in range(num_cards):
            card = self.generate_card()
            player.cards.append(card)
            player.marked_numbers[i] = set()
            # Marca automaticamente o centro livre
            if 'FREE' in card:
                player.marked_numbers[i].add('FREE')
        
        print(f"[DEBUG] {player.username} agora tem {len(player.cards)} cartelas")

    def draw_number(self):
        """Sorteia um número que ainda não foi sorteado"""
        all_numbers = list(range(1, 76))
        remaining = [n for n in all_numbers if n not in self.numbers_drawn]
        
        if remaining:
            number = random.choice(remaining)
            self.numbers_drawn.append(number)
            return number
        return None

    def get_room_info(self):
        """Retorna informações da sala"""
        total_cards = sum(self.player_cards_config.values())
        return {
            'room_name': self.room_name,
            'room_id': self.room_id,
            'admin': self.admin_username,
            'players_count': len(self.players),
            'max_players': self.max_players,
            'is_active': self.is_active,
            'game_started': self.game_started,
            'numbers_drawn': self.numbers_drawn,
            'winner': self.winner,
            'total_cards': total_cards,
            'players_config': self.get_player_cards_config(),
            'prize': self.prize
        }

    def check_winner(self):
        """Verifica se algum jogador fez bingo em alguma cartela"""
        for player in self.players:
            winning_cards = player.get_winning_cards()
            if winning_cards:
                self.winner = {
                    'username': player.username,
                    'winning_cards': winning_cards,
                    'total_cards': len(player.cards)
                }
                self.is_active = False
                return player
        return None

    def reset_game(self):
        """Reinicia o jogo"""
        self.numbers_drawn = []
        self.winner = None
        self.is_active = False
        self.game_started = False
        
        # Gera novas cartelas para todos os jogadores
        for player in self.players:
            self.generate_cards_for_player(player)

    def start_game(self):
        """Inicia o jogo"""
        if len(self.players) >= 1:  # Mínimo 1 jogador para testar
            self.game_started = True
            self.is_active = True
            # Gera cartelas para todos os jogadores baseado na configuração
            for player in self.players:
                self.generate_cards_for_player(player)
            return True
        return False