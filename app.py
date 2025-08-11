from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from models import User, Room
import os

app = Flask(__name__)
app.secret_key = "golden-club-bingo-secret-2024"
socketio = SocketIO(app, cors_allowed_origins="*")

# Armazenamento em memória
users = {}  # username: User object
rooms = {}  # room_name: Room object
user_sessions = {}  # session_id: username

@app.route("/")
def index():
    """Página inicial de login"""
    if "username" in session and session["username"] in users:
        return redirect(url_for("lobby"))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """Processa o login do usuário"""
    username = request.form.get("username", "").strip()
    
    if not username:
        return render_template("index.html", error="Nome de usuário é obrigatório")
    
    if len(username) < 3:
        return render_template("index.html", error="Nome deve ter pelo menos 3 caracteres")
    
    # Cria ou recupera usuário
    if username not in users:
        users[username] = User(username)
    
    session["username"] = username
    # user_sessions será atualizado quando o usuário conectar via WebSocket
    
    return redirect(url_for("lobby"))

@app.route("/logout")
def logout():
    """Faz logout do usuário"""
    if "username" in session:
        username = session["username"]
        # Remove usuário de qualquer sala
        if username in users:
            user = users[username]
            if user.room and user.room in rooms:
                rooms[user.room].remove_player(user)
        
        session.pop("username", None)
    
    return redirect(url_for("index"))

@app.route("/lobby")
def lobby():
    """Lobby principal com lista de salas"""
    if "username" not in session or session["username"] not in users:
        return redirect(url_for("index"))
    
    # Filtra salas ativas
    active_rooms = {name: room.get_room_info() for name, room in rooms.items() if len(room.players) > 0}
    
    return render_template("lobby.html", 
                         username=session["username"],
                         rooms=active_rooms)

@app.route("/create_room", methods=["POST"])
def create_room():
    """Cria uma nova sala"""
    if "username" not in session or session["username"] not in users:
        return redirect(url_for("index"))
    
    room_name = request.form.get("room_name", "").strip()
    username = session["username"]
    
    if not room_name:
        return redirect(url_for("lobby"))
    
    if len(room_name) < 3:
        return redirect(url_for("lobby"))
    
    # Verifica se a sala já existe
    if room_name in rooms:
        return redirect(url_for("room", room_name=room_name))
    
    # Cria nova sala
    room_obj = Room(room_name, username)
    rooms[room_name] = room_obj
    
    # Adiciona o criador como primeiro jogador e admin
    user = users[username]
    room_obj.add_player(user)
    
    return redirect(url_for("room", room_name=room_name))

@app.route("/room/<room_name>")
def room(room_name):
    """Página da sala de bingo"""
    if "username" not in session or session["username"] not in users:
        return redirect(url_for("index"))
    
    if room_name not in rooms:
        return redirect(url_for("lobby"))
    
    username = session["username"]
    user = users[username]
    room_obj = rooms[room_name]
    
    return render_template("room.html", 
                         room_name=room_name,
                         username=username,
                         room_info=room_obj.get_room_info(),
                         is_admin=user.is_admin)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Usuário conectou via WebSocket"""
    print(f"Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Usuário desconectou"""
    print(f"Cliente desconectado: {request.sid}")
    
    # Remove apenas da sessão, mas mantém o usuário na sala para permitir reconexão
    if request.sid in user_sessions:
        user_sessions.pop(request.sid, None)

@socketio.on('join_room')
def handle_join_room(data):
    """Usuário entra em uma sala"""
    room_name = data.get('room')
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao entrar na sala'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    # Verifica se o usuário já está na sala (caso do criador)
    if user not in room_obj.players:
        # Tenta adicionar o usuário à sala
        if room_obj.add_player(user):
            join_room(room_name)
            user_sessions[request.sid] = username
            
            # Gera cartelas se o jogo já começou
            if room_obj.game_started:
                room_obj.generate_cards_for_player(user)
            
            # Notifica todos na sala
            emit('player_joined', {
                'username': username,
                'players_count': len(room_obj.players),
                'players': [p.username for p in room_obj.players],
                'is_admin': user.is_admin
            }, to=room_name)
            
        else:
            emit('room_full', {'message': 'Sala está cheia!'})
    else:
        # Usuário já está na sala, apenas conecta via WebSocket
        join_room(room_name)
        user_sessions[request.sid] = username
        
        # Gera cartelas se o jogo já começou
        if room_obj.game_started:
            room_obj.generate_cards_for_player(user)
    
    # Envia estado atual do jogo para o jogador (novo ou reconectando)
    cards_status = user.get_cards_status() if user.cards else []
    print(f"[DEBUG] Enviando game_state para {username}: {len(cards_status)} cartelas")
    if cards_status:
        print(f"[DEBUG] Primeira cartela: {cards_status[0]}")
    
    emit('game_state', {
        'room_info': room_obj.get_room_info(),
        'cards': cards_status,
        'numbers_drawn': room_obj.numbers_drawn,
        'players': [p.username for p in room_obj.players],
        'players_count': len(room_obj.players)
    })

@socketio.on('leave_room')
def handle_leave_room(data):
    """Usuário sai da sala"""
    room_name = data.get('room')
    username = session.get('username')
    
    if username and username in users and room_name in rooms:
        user = users[username]
        room_obj = rooms[room_name]
        
        if room_obj.remove_player(user):
            leave_room(room_name)
            
            emit('player_left', {
                'username': username,
                'players_count': len(room_obj.players),
                'players': [p.username for p in room_obj.players]
            }, to=room_name)
            
            # Remove sala se estiver vazia
            if len(room_obj.players) == 0:
                rooms.pop(room_name, None)

@socketio.on('start_game')
def handle_start_game(data):
    """Admin inicia o jogo"""
    room_name = data.get('room')
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao iniciar jogo'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    # Verifica se é admin
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode iniciar o jogo'})
        return
    
    if room_obj.start_game():
        # Envia evento de jogo iniciado para toda a sala
        emit('game_started', {
            'room_info': room_obj.get_room_info()
        }, to=room_name)
        
        # Envia cartelas específicas para cada jogador conectado
        for session_id, username in user_sessions.items():
            if username in [p.username for p in room_obj.players]:
                player = users[username]
                cards_status = player.get_cards_status()
                print(f"[DEBUG] Enviando cartelas para {username} (session {session_id}): {len(cards_status)} cartelas")
                if cards_status:
                    print(f"[DEBUG] Primeira cartela de {username}: {cards_status[0]}")
                
                socketio.emit('game_state', {
                    'cards': cards_status,
                    'room_info': room_obj.get_room_info(),
                    'numbers_drawn': room_obj.numbers_drawn,
                    'players': [p.username for p in room_obj.players],
                    'players_count': len(room_obj.players)
                }, to=session_id)
    else:
        emit('error', {'message': 'Não é possível iniciar o jogo'})

@socketio.on('draw_number')
def handle_draw_number(data):
    """Admin sorteia um número"""
    room_name = data.get('room')
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao sortear número'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    # Verifica se é admin e se o jogo está ativo
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode sortear números'})
        return
    
    if not room_obj.is_active:
        emit('error', {'message': 'O jogo não está ativo'})
        return
    
    # Sorteia número
    number = room_obj.draw_number()
    
    if number:
        # Marca automaticamente o número nas cartelas dos jogadores
        for player in room_obj.players:
            player.mark_number(number)
        
        # Verifica se alguém ganhou
        winner = room_obj.check_winner()
        
        emit('number_drawn', {
            'number': number,
            'total_drawn': len(room_obj.numbers_drawn),
            'remaining': 75 - len(room_obj.numbers_drawn)
        }, to=room_name)
        
        # Atualiza cartelas de todos os jogadores conectados
        for session_id, username in user_sessions.items():
            if username in [p.username for p in room_obj.players]:
                player = users[username]
                socketio.emit('card_updated', {
                    'cards': player.get_cards_status()
                }, to=session_id)
        
        if winner:
            emit('game_finished', {
                'winner': room_obj.winner,
                'message': f'{winner.username} fez BINGO!'
            }, to=room_name)
    else:
        emit('error', {'message': 'Todos os números já foram sorteados'})

@socketio.on('reset_game')
def handle_reset_game(data):
    """Admin reinicia o jogo"""
    room_name = data.get('room')
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao reiniciar jogo'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode reiniciar o jogo'})
        return
    
    room_obj.reset_game()
    
    emit('game_reset', {
        'message': 'Jogo reiniciado!',
        'room_info': room_obj.get_room_info()
    }, to=room_name)

@socketio.on('set_player_cards')
def handle_set_player_cards(data):
    """Admin define número de cartelas para um jogador"""
    room_name = data.get('room')
    target_username = data.get('username')
    num_cards = data.get('num_cards', 1)
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao definir cartelas'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode definir cartelas'})
        return
    
    if room_obj.set_player_cards(target_username, num_cards):
        # Notifica todos sobre a atualização
        emit('player_cards_updated', {
            'username': target_username,
            'num_cards': num_cards,
            'room_info': room_obj.get_room_info()
        }, to=room_name)
        
        # Se o jogo já começou, envia novas cartelas para o jogador
        if room_obj.game_started:
            target_user = users.get(target_username)
            if target_user:
                socketio.emit('cards_regenerated', {
                    'cards': target_user.get_cards_status(),
                    'message': f'Suas cartelas foram atualizadas para {num_cards}!'
                }, to=target_username)
    else:
        emit('error', {'message': 'Erro ao definir cartelas para o jogador'})

@socketio.on('get_players_config')
def handle_get_players_config(data):
    """Admin solicita configuração de cartelas dos jogadores"""
    room_name = data.get('room')
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao obter configuração'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode ver esta configuração'})
        return
    
    emit('players_config', {
        'players': room_obj.get_player_cards_config()
    })

@socketio.on('update_check_ins')
def handle_update_check_ins(data):
    """Admin atualiza check-ins de um jogador"""
    room_name = data.get('room')
    target_username = data.get('username')
    check_ins = data.get('check_ins', 0)
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao atualizar check-ins'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode atualizar check-ins'})
        return
    
    # Encontra o jogador e atualiza check-ins
    target_user = users.get(target_username)
    if target_user and target_user in room_obj.players:
        target_user.check_ins = max(0, check_ins)
        
        emit('check_ins_updated', {
            'username': target_username,
            'check_ins': target_user.check_ins,
            'room_info': room_obj.get_room_info()
        }, to=room_name)
    else:
        emit('error', {'message': 'Jogador não encontrado na sala'})

@socketio.on('transfer_admin')
def handle_transfer_admin(data):
    """Admin transfere privilégios para outro jogador"""
    room_name = data.get('room')
    new_admin_username = data.get('new_admin')
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao transferir admin'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode transferir privilégios'})
        return
    
    if username == new_admin_username:
        emit('error', {'message': 'Você já é o administrador'})
        return
    
    if room_obj.transfer_admin(new_admin_username):
        emit('admin_transferred', {
            'old_admin': username,
            'new_admin': new_admin_username,
            'message': f'{new_admin_username} agora é o administrador da sala',
            'room_info': room_obj.get_room_info()
        }, to=room_name)
    else:
        emit('error', {'message': 'Erro ao transferir admin. Verifique se o jogador existe na sala'})

@socketio.on('set_prize')
def handle_set_prize(data):
    """Admin define o prêmio do jogo"""
    room_name = data.get('room')
    prize = data.get('prize', '').strip()
    username = session.get('username')
    
    if not username or username not in users or room_name not in rooms:
        emit('error', {'message': 'Erro ao definir prêmio'})
        return
    
    user = users[username]
    room_obj = rooms[room_name]
    
    if not user.is_admin:
        emit('error', {'message': 'Apenas o administrador pode definir o prêmio'})
        return
    
    room_obj.set_prize(prize)
    
    emit('prize_updated', {
        'prize': room_obj.prize,
        'message': f'Prêmio atualizado: {room_obj.prize}' if room_obj.prize else 'Prêmio removido',
        'room_info': room_obj.get_room_info()
    }, to=room_name)

if __name__ == "__main__":
    # Cria diretórios se não existirem
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Configuração para produção (Render) e desenvolvimento
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("🎯 Servidor Bingo da Golden Club iniciado!")
    print(f"🌐 Rodando em: {host}:{port}")
    socketio.run(app, debug=False, host=host, port=port)