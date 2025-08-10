# 🎯 Bingo da Golden Club

Sistema de Bingo online desenvolvido para a Golden Club Guild com suporte a múltiplas salas simultâneas e até 50 jogadores por sala.

## 🚀 Características

- ✅ **Sistema de Login**: Cada jogador tem sua conta individual
- 🏠 **Múltiplas Salas**: Crie e entre em diferentes salas de bingo
- 👥 **Até 50 Jogadores**: Cada sala suporta até 50 jogadores simultâneos
- 🎲 **Cartelas Únicas**: Cada jogador recebe uma cartela única de 5x5
- 👑 **Sistema de Admin**: Administrador da sala controla o jogo
- ⚡ **Tempo Real**: Atualização instantânea via WebSocket
- 🎨 **Design Temático**: Interface com as cores da Golden Club (dourado/laranja)
- 📱 **Responsivo**: Funciona em desktop e mobile

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python Flask + Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript
- **WebSocket**: Comunicação em tempo real
- **Design**: CSS Grid, Flexbox, Animações CSS

## 📋 Pré-requisitos

- Python 3.7+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. **Clone ou baixe o projeto**:
   ```bash
   cd bingo_golden
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o servidor**:
   ```bash
   python app.py
   ```

4. **Acesse o jogo**:
   Abra seu navegador e vá para: `http://localhost:5000`

## 🎮 Como Jogar

### 1. **Login**
- Digite seu nome de usuário (mínimo 3 caracteres)
- Clique em "ENTRAR NA GUILDA"

### 2. **Lobby**
- Veja as salas disponíveis
- Crie uma nova sala ou entre em uma existente
- Máximo de 50 jogadores por sala

### 3. **Sala de Bingo**
- **Jogadores**: Aguardam o admin iniciar o jogo
- **Admin** (primeiro a entrar): Controla o jogo
  - Iniciar Jogo
  - Sortear Números
  - Reiniciar Jogo

### 4. **Durante o Jogo**
- Números são sorteados automaticamente pelo admin
- Sua cartela é marcada automaticamente
- Primeiro a completar a cartela ganha!
- Centro da cartela é "FREE" (sempre marcado)

## 🎯 Funcionalidades Detalhadas

### **Sistema de Salas**
- Criação dinâmica de salas
- Limite de 50 jogadores por sala
- Múltiplas salas simultâneas
- Admin automático (primeiro jogador)

### **Cartelas de Bingo**
- Formato 5x5 tradicional
- Colunas: B (1-15), I (16-30), N (31-45), G (46-60), O (61-75)
- Centro "FREE" sempre marcado
- Geração aleatória única para cada jogador

### **Controles do Admin**
- **Iniciar Jogo**: Gera cartelas para todos os jogadores
- **Sortear Número**: Sorteia números de 1-75 aleatoriamente
- **Reiniciar Jogo**: Limpa o jogo e gera novas cartelas

### **Interface em Tempo Real**
- Atualização instantânea de cartelas
- Lista de jogadores online
- Números sorteados em tempo real
- Notificações de eventos
- Modal de vitória

## 🎨 Design e Tema

O design segue as cores da Golden Club:
- **Dourado**: `#FFD700` (primário)
- **Laranja**: `#FFA500` (secundário)
- **Preto**: `#000000` (fundo)
- **Gradientes**: Efeitos dourado/laranja
- **Animações**: Flutuação, brilho, pulse

## 📁 Estrutura do Projeto

```
bingo_golden/
├── app.py                 # Servidor Flask principal
├── models.py              # Classes User e Room
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── static/
│   ├── style.css         # Estilos CSS
│   └── logo.svg          # Logo da Golden Club
└── templates/
    ├── index.html        # Página de login
    ├── lobby.html        # Lobby principal
    └── room.html         # Sala de bingo
```

## 🔧 Configurações

### **Limites do Sistema**
- Máximo 50 jogadores por sala
- Cartelas 5x5 (25 números)
- Números de 1 a 75
- Sessões em memória (reinicia ao parar servidor)

### **Personalização**
- Modifique `max_players` em `Room` para alterar limite de jogadores
- Ajuste cores CSS em `style.css`
- Personalize logo em `static/logo.svg`

## 🚨 Solução de Problemas

### **Erro de Dependências**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **Porta em Uso**
Modifique a porta no final de `app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### **Problemas de WebSocket**
- Verifique se o firewall não está bloqueando
- Teste em navegador diferente
- Desative extensões que possam interferir

## 🎯 Recursos Avançados

### **Notificações**
- Jogador entrou/saiu da sala
- Número sorteado
- Jogo iniciado/finalizado
- Erros e avisos

### **Animações**
- Números flutuantes no fundo
- Efeitos de brilho dourado
- Animações de entrada
- Pulse nos números marcados

### **Responsividade**
- Layout adaptável para mobile
- Controles touch-friendly
- Texto legível em telas pequenas

## 🏆 Melhorias Futuras

- [ ] Banco de dados persistente
- [ ] Sistema de ranking
- [ ] Histórico de jogos
- [ ] Salas privadas com senha
- [ ] Diferentes tipos de bingo
- [ ] Sistema de premiação
- [ ] Chat entre jogadores
- [ ] Estatísticas detalhadas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Consulte os logs do terminal
3. Teste em navegador atualizado
4. Reinicie o servidor se necessário

---

**Desenvolvido para a Golden Club Guild** 🐉✨

*Que os números da sorte estejam sempre com vocês!* 🎲🏆