import pygame
import cmath
import math
import random

# =============================================================================
# 1. CONFIGURAÇÕES E CONSTANTES
# =============================================================================
pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- Carregamento do Som ---
## Som da colisão
try:
    # Tenta carregar o arquivo de som 
    SOM_IMPACTO = pygame.mixer.Sound("assets/ping.wav")
    SOM_IMPACTO.set_volume(0.4)  # Ajusta o volume 
except Exception as e:
    print(f"Aviso: Som não encontrado ({e}). O jogo continuará mudo.")
    SOM_IMPACTO = None

# --- Música de Fundo ---
try:
    # Tenta carregar o arquivo de som 
    pygame.mixer.music.load("assets/music_festival.wav") 
    
    # volume
    pygame.mixer.music.set_volume(0.2) 
    
    pygame.mixer.music.play(-1) # Loop infinito
except Exception as e:
    print(f"Erro na música: {e}")

# --- Geometria da Tela ---
LARGURA = 1366
ALTURA = 715
CENTRO = (LARGURA // 2, ALTURA // 2)
RAIO = 300

# --- Física do Jogo ---
VELOCIDADE_GIRO_RAQUETE = 0.05
VELOCIDADE_MINIMA = 3.0    # Velocidade inicial (módulo do vetor)
VELOCIDADE_MAXIMA = 12.0    # Velocidade limite
ACELERACAO = 1.002         # Fator de multiplicação vetorial por frame
TEMPO_DE_ESPERA = 2000     # Pausa entre pontos (ms)

# --- Aparência (Estilo Neon) ---
COR_FUNDO = (20, 0, 40)        # Roxo Profundo (Background)
COR_PRINCIPAL = (0, 255, 200)  # Verde Água (Elementos Ativos)
COR_SECUNDARIA = (60, 20, 80)  # Roxo Médio (Estrutura da Arena)
COR_AVISO = (255, 255, 0)      # Amarelo (Alertas)
COR_TEXTO = (255, 255, 255)    # Branco

# --- Cores players ---
COR_P1 = (0, 191, 255)    # Azul Neon (Deep Sky Blue) para o Player 1
COR_P2 = (255, 20, 147)   # Rosa Neon (Deep Pink) para o Player 2

# --- Fontes e Texto ---
FONTE_TITULO = pygame.font.SysFont("arial", 60, bold=True)
FONTE_OPCOES = pygame.font.SysFont("arial", 30, bold=False)
FONTE_PLACAR = pygame.font.SysFont("arial", 35, bold=True)
FONTE_AVISO = pygame.font.SysFont("arial", 20, bold=False)
FONTE_ROUNDS = pygame.font.SysFont("arial", 20, bold=False)

# --- Variáveis Globais de Controle ---
pontos_p1 = 0
pontos_p2 = 0
rounds_ganhosp1 = 0
rounds_ganhosp2 = 0
estado_jogo = "MENU"  # Estados: "MENU" ou "JOGANDO" ou "VENCEDOR"
modo_jogo = "BOT"     # Modos: "BOT" ou "PVP"
limite_round = 3
LIMITE_VITORIAS_POR_ROUND = 3

TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pong Circular - Variáveis Complexas & IA")


# =============================================================================
# 2. FUNÇÕES AUXILIARES
# =============================================================================
def complexo_para_cartesiano(z):
    """
    Converte coordenadas do plano complexo (z) para pixels da tela (x, y).
    Nota: O eixo Y é invertido pois na biblioteca gráfica o Y cresce para baixo.
    """
    x_tela = CENTRO[0] + int(z.real)
    y_tela = CENTRO[1] - int(z.imag)
    return (x_tela, y_tela)


def desenhar_menu():
    """Renderiza a interface gráfica do Menu Principal."""
    TELA.fill(COR_FUNDO)

    # Título
    titulo = FONTE_TITULO.render("PONG CIRCULAR", True, COR_PRINCIPAL)
    subtitulo = FONTE_AVISO.render(
        "Simulação com Variáveis Complexas", True, COR_AVISO)

    # Opções de Jogo
    texto_1 = FONTE_OPCOES.render(
        "Pressione [1] para 1 Jogador (vs Bot)", True, COR_TEXTO)
    texto_2 = FONTE_OPCOES.render(
        "Pressione [2] para 2 Jogadores (Local)", True, COR_TEXTO)
    texto_sair = FONTE_AVISO.render("ESC para Sair", True, COR_SECUNDARIA)

    # Centralização dos elementos
    rect_titulo = titulo.get_rect(center=(CENTRO[0], CENTRO[1] - 100))
    rect_sub = subtitulo.get_rect(center=(CENTRO[0], CENTRO[1] - 50))
    rect_1 = texto_1.get_rect(center=(CENTRO[0], CENTRO[1] + 50))
    rect_2 = texto_2.get_rect(center=(CENTRO[0], CENTRO[1] + 100))
    rect_sair = texto_sair.get_rect(center=(CENTRO[0], ALTURA - 50))

    TELA.blit(titulo, rect_titulo)
    TELA.blit(subtitulo, rect_sub)
    TELA.blit(texto_1, rect_1)
    TELA.blit(texto_2, rect_2)
    TELA.blit(texto_sair, rect_sair)


def resetar_partida():
    """Reinicia variáveis de pontuação e posições para um novo jogo."""
    global pontos_p1, pontos_p2
    global rounds_ganhosp1, rounds_ganhosp2
    pontos_p1 = 0
    pontos_p2 = 0
    rounds_ganhosp1 = 0
    rounds_ganhosp2 = 0
    bola.resetar()
    # Restaura posição inicial das raquetes (Top e Bottom)
    player1.angulo = math.pi/2
    player2.angulo = 3*math.pi/2


def procurar_vencedor():
    global rounds_ganhosp1, rounds_ganhosp2, estado_jogo
    vencedor = None

    if rounds_ganhosp1 >= LIMITE_VITORIAS_POR_ROUND:
        vencedor = "JOGADOR 1"
    elif rounds_ganhosp2 >= LIMITE_VITORIAS_POR_ROUND:
        vencedor = "JOGADOR 2"

    if vencedor:
        # Muda o estado de jogo para VENCEDOR
        estado_jogo = "VENCEDOR"
        return vencedor

    return None
# =============================================================================
# 3. CLASSES (OBJETOS)
# =============================================================================


class Bola:
    def __init__(self):
        self.raio = 10
        self.cor = COR_PRINCIPAL
        self.resetar()

    def resetar(self):
        """Posiciona a bola na origem (0,0) do plano complexo."""
        self.pos = complex(0, 0)
        self.vel = complex(0, 0)
        self.esperando = True
        self.momento_reset = pygame.time.get_ticks()

    def mover(self):
        """Gerencia a cinemática da bola, colisões polares e pontuação."""
        global pontos_p1, pontos_p2

        # A. Controle de Pausa (Cooldown)
        if self.esperando:
            if pygame.time.get_ticks() - self.momento_reset < TEMPO_DE_ESPERA:
                return
            self.esperando = False
            # Define vetor inicial com ângulo aleatório (0 a 2Pi)
            self.vel = cmath.rect(
                VELOCIDADE_MINIMA, random.uniform(0, 2*math.pi))

        # B. Dinâmica de Movimento
        # Aplica aceleração constante ao vetor velocidade
        if abs(self.vel) < VELOCIDADE_MAXIMA:
            self.vel *= ACELERACAO

        self.pos += self.vel

        # C. Detecção de Colisão (Limites da Arena)
        # Verifica o módulo do número complexo (distância da origem)
        if abs(self.pos) >= (RAIO - self.raio):

            # --- CÁLCULO POLAR ---
            # Extrai a fase (ângulo) da bola no plano complexo
            angulo_bola = cmath.phase(self.pos)
            # Normaliza para o intervalo [0, 2Pi]
            if angulo_bola < 0:
                angulo_bola += 2 * math.pi

            margem = (player1.tamanho + 0.001) / 2

            # Verifica intersecção angular com as raquetes
            bateu_p1 = (player1.angulo -
                        margem) <= angulo_bola <= (player1.angulo + margem)
            bateu_p2 = (player2.angulo -
                        margem) <= angulo_bola <= (player2.angulo + margem)

            if bateu_p1 or bateu_p2:
                
                # --- TOCA O SOM NA COLISÂO ---
                if SOM_IMPACTO:  # Só toca se o arquivo foi carregado corretamente
                    SOM_IMPACTO.play()

                # Colisão elástica: inverte o vetor velocidade
                self.vel = -self.vel

                # Adiciona perturbação angular (Ruído) para evitar loops estáticos
                ruido = cmath.exp(complex(0, random.uniform(-0.2, 0.2)))
                self.vel *= ruido

                self.pos += self.vel * 2  # Afasta da borda para evitar 'grudar'
            else:
                # Pontuação (Bola passou pela defesa)
                global rounds_ganhosp1, rounds_ganhosp2
                if 0 < angulo_bola < math.pi:
                    pontos_p2 += 1  # Passou por cima
                    if pontos_p2 == limite_round:
                        rounds_ganhosp2 += 1
                        pontos_p2 = 0
                        pontos_p1 = 0
                else:
                    pontos_p1 += 1  # Passou por baixo
                    if pontos_p1 == limite_round:
                        rounds_ganhosp1 += 1
                        pontos_p2 = 0
                        pontos_p1 = 0
                self.resetar()

    def desenhar(self):
        pos_pixel = complexo_para_cartesiano(self.pos)
        pygame.draw.circle(TELA, self.cor, pos_pixel, self.raio)
        if self.esperando:
            texto = FONTE_AVISO.render("PREPARE-SE...", True, COR_AVISO)
            TELA.blit(texto, (pos_pixel[0]-60, pos_pixel[1]-40))


class Raquete:

    def __init__(self, angulo_inicial, limite_min, limite_max, cor):
        """Define raquete controlada por coordenadas polares."""
        self.angulo = angulo_inicial
        self.min = limite_min
        self.max = limite_max
        self.velocidade_giro = VELOCIDADE_GIRO_RAQUETE
        self.tamanho = 0.3  # Comprimento do arco (em radianos)
        self.cor = cor

        # --- IA (Simulação de Comportamento Humano) ---
        self.timer_reacao = 0          # Delay de processamento visual
        self.visao_atual = self.angulo  # Posição estimada da bola
        self.erro_mira = 0             # Fator de imprecisão estocástica

    def mover(self, direcao):
        """Atualiza o ângulo da raquete respeitando os limites físicos."""
        novo = self.angulo + (direcao * self.velocidade_giro)
        if self.min <= novo <= self.max:
            self.angulo = novo

    def desenhar(self):
        rect = (CENTRO[0]-RAIO, CENTRO[1]-RAIO, RAIO*2, RAIO*2)
        pygame.draw.arc(TELA, self.cor, rect,
                        self.angulo - self.tamanho/2,
                        self.angulo + self.tamanho/2, 8)

    def atualizar_ia(self, bola):
        """
        Algoritmo de controle autônomo:
        1. Amostragem Discreta (Tempo de Reação).
        2. Estimativa com Ruído (Erro Humano).
        """
        # 1. Reação (Atualiza a cada 4 frames)
        self.timer_reacao += 1
        if self.timer_reacao > 4:
            self.timer_reacao = 0

            # Calcula fase real da bola
            angulo_real = cmath.phase(bola.pos)
            if angulo_real < 0:
                angulo_real += 2 * math.pi

            # 2. Aplica erro aleatório à mira (+/- 0.05 rad)
            self.erro_mira = random.uniform(-0.05, 0.05)
            self.visao_atual = angulo_real + self.erro_mira

        # 3. Lógica de Decisão
        # Se a bola está no hemisfério inferior (campo do P2), persegue o alvo
        if math.pi < self.visao_atual < 2 * math.pi:
            alvo = self.visao_atual
        else:
            # Se a bola foi para cima, recua para o centro (defesa)
            alvo = 3 * math.pi / 2

        # 4. Execução do Movimento
        diferenca = alvo - self.angulo

        # Zona morta (Deadzone) para evitar oscilação
        if abs(diferenca) > 0.05:
            if diferenca > 0:
                self.mover(1)
            else:
                self.mover(-1)


# =============================================================================
# 4. INICIALIZAÇÃO E LOOP PRINCIPAL
# =============================================================================

# P1 (Cima) vs P2 (Baixo)
player1 = Raquete(math.pi/2, 0, math.pi, COR_P1)
player2 = Raquete(3*math.pi/2, math.pi, 2*math.pi, COR_P2)

bola = Bola()
relogio = pygame.time.Clock()
rodando = True

while rodando:
    # --- ENTRADAS (EVENTOS) ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:
            # Lógica do Menu
            if estado_jogo == "MENU":
                if evento.key == pygame.K_1:
                    modo_jogo = "BOT"
                    estado_jogo = "JOGANDO"
                    resetar_partida()
                elif evento.key == pygame.K_2:
                    modo_jogo = "PVP"
                    estado_jogo = "JOGANDO"
                    resetar_partida()
                elif evento.key == pygame.K_ESCAPE:
                    rodando = False

            # Lógica durante a partida
            elif estado_jogo == "JOGANDO":
                if evento.key == pygame.K_ESCAPE:
                    estado_jogo = "MENU"

            # Lógica do Vencedor
            elif estado_jogo == "VENCEDOR":
                if evento.key == pygame.K_m or evento.key == pygame.K_ESCAPE:
                    estado_jogo = "MENU"
                    resetar_partida()

    # =========================================================================
    # ESTADO: MENU
    # =========================================================================
    if estado_jogo == "MENU":
        desenhar_menu()

    # =========================================================================
    # ESTADO: JOGANDO
    # =========================================================================
    elif estado_jogo == "JOGANDO":

        teclas = pygame.key.get_pressed()

        # Controles Player 1 (Manual - Teclas A/D)
        if teclas[pygame.K_a]:
            player1.mover(1)
        if teclas[pygame.K_d]:
            player1.mover(-1)

        # Controles Player 2 (IA ou Manual)
        if modo_jogo == "BOT":
            player2.atualizar_ia(bola)
        else:
            # Modo PVP (Setas)
            if teclas[pygame.K_LEFT]:
                player2.mover(-1)
            if teclas[pygame.K_RIGHT]:
                player2.mover(1)

        # --- ATUALIZAÇÃO FÍSICA ---
        bola.mover()

        # --- RENDERIZAÇÃO ---
        TELA.fill(COR_FUNDO)

        # Cenário (Arena Circular)
        pygame.draw.circle(TELA, COR_SECUNDARIA, CENTRO, RAIO)
        pygame.draw.circle(TELA, COR_PRINCIPAL, CENTRO, RAIO, 2)

        # Linha do Horizonte (Divisão de Campos)
        ponto_esq = complex(-RAIO, 0)
        ponto_dir = complex(RAIO, 0)
        pygame.draw.line(TELA, COR_PRINCIPAL,
                         complexo_para_cartesiano(ponto_esq),
                         complexo_para_cartesiano(ponto_dir), 1)

        # Desenho dos Objetos
        player1.desenhar()
        player2.desenhar()
        bola.desenhar()

        # Placar
        TELA.blit(FONTE_PLACAR.render(
            f"P1: {pontos_p1}", True, COR_PRINCIPAL), (50, 50))
        TELA.blit(FONTE_ROUNDS.render(
            f"Rounds ganhos: {rounds_ganhosp1}/{LIMITE_VITORIAS_POR_ROUND}", True, COR_PRINCIPAL), (50, 90))
        TELA.blit(FONTE_PLACAR.render(
            f"P2: {pontos_p2}", True, COR_PRINCIPAL), (50, ALTURA-100))
        TELA.blit(FONTE_ROUNDS.render(
            f"Rounds ganhos: {rounds_ganhosp2}/{LIMITE_VITORIAS_POR_ROUND}", True, COR_PRINCIPAL), (50, ALTURA-60))

        procurar_vencedor()

        # Instrução de saída
        TELA.blit(FONTE_AVISO.render("ESC: Menu", True,
                  COR_SECUNDARIA), (LARGURA - 120, 20))


# =========================================================================
# ESTADO: VENCEDOR
# =========================================================================
    elif estado_jogo == "VENCEDOR":
        # Aqui, a física do jogo não é atualizada, apenas o placar final é mostrado.
        TELA.fill(COR_FUNDO)

        vencedor = "JOGADOR 1" if rounds_ganhosp1 >= LIMITE_VITORIAS_POR_ROUND else "JOGADOR 2"

        texto_venceu = FONTE_TITULO.render(
            f"O {vencedor} VENCEU!", True, COR_AVISO)
        texto_reset = FONTE_AVISO.render(
            "Pressione [M] para o Menu", True, COR_TEXTO)

        rect_venceu = texto_venceu.get_rect(center=(CENTRO[0], CENTRO[1]))
        rect_reset = texto_reset.get_rect(center=(CENTRO[0], CENTRO[1] + 50))

        TELA.blit(texto_venceu, rect_venceu)
        TELA.blit(texto_reset, rect_reset)

        # Lógica de input para voltar ao menu
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_m] or teclas[pygame.K_ESCAPE]:
            estado_jogo = "MENU"
            resetar_partida()  # Garante que as pontuações sejam limpas ao voltar'

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
