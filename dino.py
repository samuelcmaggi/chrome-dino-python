# ================================================================
# COMUNIDADE SAMUEL MAGGI // CHROME DINO EM PYTHON
# Pygame | Som sintetizado | Dia/noite | Estrelas cadentes
# Projeto educacional inspirado no jogo offline do Chrome
# ================================================================

import json
import math
import random
from array import array
from pathlib import Path

import pygame

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

LARGURA, ALTURA = 1000, 350
CHAO_Y, FPS = 269, 60
FUNDO_DIA, TINTA_DIA = (247, 247, 247), (45, 45, 45)
FUNDO_NOITE, TINTA_NOITE = (31, 32, 36), (241, 241, 241)
ESCALA_DINO, ESCALA_OBSTACULO = 2, 3
ARQUIVO_RECORDE = Path(__file__).with_name("dino_recorde.json")

janela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Comunidade Samuel Maggi // Chrome Dino em Python")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("consolas", 19, bold=True)
fonte_pequena = pygame.font.SysFont("consolas", 14, bold=True)
fonte_grande = pygame.font.SysFont("consolas", 30, bold=True)

# Desenhos feitos com pixels: 1 = pixel visivel, 0 = transparente.
DINO_1 = (
    "0000000000011111000000",
    "0000000000111111110000",
    "0000000000111111111000",
    "0000000000111101111000",
    "0000000000111111111000",
    "0000000000111111111000",
    "0000000000111111111000",
    "0000000000111111111000",
    "0000000000111111111000",
    "0000000000111110000000",
    "1000000001111110000000",
    "1100000011111110000000",
    "1110000111111111000000",
    "1111001111111111000000",
    "1111111111111111000000",
    "0111111111111110000000",
    "0011111111111100000000",
    "0001111111111000000000",
    "0000111111110000000000",
    "0000011111100000000000",
    "0000011011000000000000",
    "0000011001100000000000",
    "0000011000110000000000",
    "0000110000000000000000",
)
DINO_2 = DINO_1[:-4] + (
    "0000011001100000000000",
    "0000110001100000000000",
    "0001100001100000000000",
    "0000000000110000000000",
)
DINO_AGACHADO_1 = (
    "0000000000000000000000000000",
    "0000000000000000000111111000",
    "0000000000000000011111111100",
    "0000000000000000011110111100",
    "0000000000000000011111111100",
    "0000000000000000011111111100",
    "1000000000001111111111111100",
    "1100000000111111111111110000",
    "1111000011111111111111110000",
    "1111111111111111111111100000",
    "0111111111111111111111000000",
    "0011111111111111111100000000",
    "0000111111111111110000000000",
    "0000011000011000000000000000",
    "0000110000001100000000000000",
)
DINO_AGACHADO_2 = DINO_AGACHADO_1[:-2] + (
    "0000110000000110000000000000",
    "0000011000001100000000000000",
)
CACTO_PEQUENO = (
    "000110000", "000110000", "000110000", "010110000",
    "010110100", "011110100", "001111100", "000110000",
    "000110000", "000110000", "000110000", "000110000",
    "000110000", "001111000",
)
CACTO_GRANDE = (
    "0000110000", "0000110000", "0000110000", "0000110100",
    "0000110100", "0100111100", "0100111000", "0111110000",
    "0011110000", "0000110000", "0000110000", "0000110000",
    "0000110000", "0000110000", "0001111000",
)
PASSARO_1 = (
    "000000001100000000", "000000011110000000", "100000111111000000",
    "110001111111100000", "111111111111110000", "011111111111111100",
    "001111111111111110", "000111111111111100", "000011111111000000",
)
PASSARO_2 = (
    "000000000000000000", "000000011110000000", "000000111111000000",
    "111111111111110000", "011111111111111100", "001111111111111110",
    "000111111111111100", "000011111111000000", "000000110011000000",
)

_cache_sprites = {}


def sprite_pixels(padrao, escala, cor):
    """Converte o desenho em pixels para Surface, usando cache."""
    chave = (padrao, escala, cor)
    if chave not in _cache_sprites:
        w = max(map(len, padrao)) * escala
        h = len(padrao) * escala
        superficie = pygame.Surface((w, h), pygame.SRCALPHA)
        for linha, texto in enumerate(padrao):
            for coluna, digito in enumerate(texto):
                if digito == "1":
                    pygame.draw.rect(superficie, cor, (
                        coluna * escala, linha * escala, escala, escala
                    ))
        _cache_sprites[chave] = superficie
    return _cache_sprites[chave]


def misturar(cor1, cor2, fator):
    return tuple(round(a + (b - a) * fator) for a, b in zip(cor1, cor2))


def escrever(texto, fonte_usada, cor, centro=None, topo=None):
    imagem = fonte_usada.render(texto, True, cor)
    caixa = imagem.get_rect()
    if centro is not None:
        caixa.center = centro
    else:
        caixa.topleft = topo
    janela.blit(imagem, caixa)


def carregar_recorde():
    try:
        return max(0, int(json.loads(ARQUIVO_RECORDE.read_text(
            encoding="utf-8")).get("recorde", 0)))
    except (OSError, ValueError, TypeError, AttributeError):
        return 0


def salvar_recorde(recorde):
    try:
        ARQUIVO_RECORDE.write_text(json.dumps(
            {"recorde": int(recorde)}, indent=2), encoding="utf-8")
    except OSError:
        pass


class Sons:
    """Sintetiza efeitos retrô sem arquivos WAV/MP3 externos."""

    def __init__(self):
        self.ativo = pygame.mixer.get_init() is not None
        self.mudo = False
        self.efeitos = {}
        if not self.ativo:
            return
        try:
            self.efeitos = {
                "pulo": self.criar(530, 810, 0.17, "seno", 0.23),
                "pouso": self.criar(155, 85, 0.06, "triangulo", 0.13),
                "ponto": self.criar(820, 1250, 0.23, "quadrada", 0.17),
                "colisao": self.criar(245, 55, 0.40, "ruido", 0.29),
                "noite": self.criar(640, 310, 0.38, "seno", 0.16),
                "agachar": self.criar(260, 170, 0.09, "triangulo", 0.10),
                "iniciar": self.criar(360, 760, 0.26, "seno", 0.18),
            }
        except pygame.error:
            self.ativo = False
            self.efeitos.clear()

    def criar(self, inicial, final, duracao, forma, volume):
        taxa = pygame.mixer.get_init()[0]
        amostras = array("h")
        fase = 0.0
        rng = random.Random(425)
        total = int(taxa * duracao)
        for indice in range(total):
            t = indice / max(total - 1, 1)
            frequencia = inicial + (final - inicial) * t
            fase += math.tau * frequencia / taxa
            seno = math.sin(fase)
            if forma == "triangulo":
                onda = (2 / math.pi) * math.asin(seno)
            elif forma == "quadrada":
                onda = 1.0 if seno >= 0 else -1.0
            elif forma == "ruido":
                onda = 0.45 * seno + 0.55 * rng.uniform(-1, 1)
            else:
                onda = seno
            ataque = min(1.0, t * 95)
            envelope = ataque * (1 - t) ** 1.8
            amostras.append(int(32767 * volume * envelope * onda))
        return pygame.mixer.Sound(buffer=amostras.tobytes())

    def tocar(self, nome):
        if self.ativo and not self.mudo and nome in self.efeitos:
            try:
                self.efeitos[nome].play()
            except pygame.error:
                self.ativo = False


class Dino:
    def __init__(self):
        self.x = 85
        self.pes = float(CHAO_Y)
        self.velocidade_y = 0.0
        self.agachado = False
        self.animacao = 0.0
        self.quadro = 0

    @property
    def no_chao(self):
        return self.pes >= CHAO_Y - 0.01

    def pular(self):
        if self.no_chao:
            self.velocidade_y = -670
            self.pes -= 0.1
            self.agachado = False
            return True
        return False

    def desenho(self):
        if not self.no_chao:
            return DINO_1
        if self.agachado:
            return DINO_AGACHADO_1 if self.quadro == 0 else DINO_AGACHADO_2
        return DINO_1 if self.quadro == 0 else DINO_2

    def caixa(self):
        desenho = self.desenho()
        w, h = len(desenho[0]) * ESCALA_DINO, len(desenho) * ESCALA_DINO
        return pygame.Rect(self.x + 8, round(self.pes - h) + 5,
                           w - 14, h - 9)

    def atualizar(self, dt, agachar):
        aterrissou = False
        if not self.no_chao:
            gravidade = 1950 * (1.65 if agachar else 1.0)
            self.velocidade_y += gravidade * dt
            self.pes += self.velocidade_y * dt
            if self.pes >= CHAO_Y:
                self.pes = float(CHAO_Y)
                self.velocidade_y = 0
                aterrissou = True
        self.agachado = agachar and self.no_chao
        self.animacao += dt
        if self.animacao >= 0.12:
            self.animacao %= 0.12
            self.quadro = 1 - self.quadro
        return aterrissou

    def desenhar(self, tinta):
        imagem = sprite_pixels(self.desenho(), ESCALA_DINO, tinta)
        janela.blit(imagem, (self.x, round(self.pes - imagem.get_height())))


class Obstaculo:
    def __init__(self, tipo, x, grupo=1, altura_passaro=None):
        self.tipo, self.x, self.grupo = tipo, float(x), grupo
        self.tempo = 0.0
        if tipo == "passaro":
            self.y = CHAO_Y - (63 if altura_passaro is None else altura_passaro)
            self.padrao = PASSARO_1
            self.escala = 3
            self.largura = len(PASSARO_1[0]) * self.escala
            self.altura = len(PASSARO_1) * self.escala
        else:
            self.padrao = CACTO_GRANDE if tipo == "grande" else CACTO_PEQUENO
            self.escala = ESCALA_OBSTACULO
            self.largura_peca = len(self.padrao[0]) * self.escala
            self.altura = len(self.padrao) * self.escala
            self.passo = self.largura_peca - 4
            self.largura = self.largura_peca + (grupo - 1) * self.passo
            self.y = CHAO_Y - self.altura

    def atualizar(self, velocidade, dt):
        self.x -= velocidade * dt * (1.05 if self.tipo == "passaro" else 1.0)
        self.tempo += dt

    def caixa(self):
        return pygame.Rect(round(self.x) + 5, self.y + 4,
                           self.largura - 10, self.altura - 7)

    def desenhar(self, tinta):
        if self.tipo == "passaro":
            padrao = PASSARO_1 if int(self.tempo / 0.17) % 2 == 0 else PASSARO_2
            janela.blit(sprite_pixels(padrao, self.escala, tinta),
                        (round(self.x), round(self.y)))
        else:
            imagem = sprite_pixels(self.padrao, self.escala, tinta)
            for i in range(self.grupo):
                janela.blit(imagem, (round(self.x + self.passo * i), self.y))


class Nuvem:
    def __init__(self, x=None):
        self.x = float(random.randint(0, LARGURA) if x is None else x)
        self.y = random.randint(67, 137)
        self.vel = random.uniform(13, 23)
        self.escala = random.choice((0.8, 1.0, 1.1))

    def atualizar(self, dt):
        self.x -= self.vel * dt

    def desenhar(self, cor):
        x, y, s = round(self.x), self.y, self.escala
        pontos = [(0, 13), (10, 13), (12, 7), (19, 3), (28, 4),
                  (34, 11), (45, 11), (51, 15), (50, 18), (0, 18)]
        pontos = [(x + round(px*s), y + round(py*s)) for px, py in pontos]
        pygame.draw.lines(janela, cor, False, pontos, 2)


class Meteoro:
    """Estrela cadente decorativa: nao e obstaculo do jogo original."""

    def __init__(self):
        self.x = float(random.randint(650, 1000))
        self.y = float(random.randint(52, 115))
        self.vida = 1.1

    def atualizar(self, dt):
        self.x -= 420 * dt
        self.y += 115 * dt
        self.vida -= dt

    def desenhar(self, cor):
        for i in range(5):
            x = round(self.x + i * 7)
            y = round(self.y - i * 2)
            pygame.draw.line(janela, cor, (x, y), (x+4, y-1), 1)
        pygame.draw.circle(janela, cor, (round(self.x), round(self.y)), 2)


class Jogo:
    def __init__(self):
        self.sons = Sons()
        self.recorde = carregar_recorde()
        self.estrelas = [(random.randrange(20, LARGURA - 20),
                          random.randrange(42, 178), random.choice((1, 1, 2)))
                         for _ in range(31)]
        self.detalhes_chao = [(i * 27, random.choice((6, 11, 17)))
                              for i in range(45)]
        self.nuvens = [Nuvem(x) for x in (300, 760, 1100)]
        self.meteoros = []
        self.tempo_meteoro = random.uniform(5, 9)
        self.noite_manual = None
        self.noite_visivel = 0.0
        self.marcador_fase = False
        self.estado = "inicio"
        self.reiniciar(dar_inicio=False)

    def reiniciar(self, dar_inicio=True):
        self.dino = Dino()
        self.obstaculos = []
        self.poeira = []
        self.pontos = 0.0
        self.velocidade = 390.0
        self.distancia_spawn = 550.0
        self.deslocamento_chao = 0.0
        self.proximo_marco = 100
        self.tempo_poeira = 0.0
        self.estado = "jogando" if dar_inicio else "inicio"
        self.sons.tocar("iniciar") if dar_inicio else None

    def alvo_noite(self):
        if self.noite_manual is not None:
            return self.noite_manual
        return int(self.pontos // 700) % 2 == 1

    def gerar_obstaculo(self):
        if self.pontos > 155 and random.random() < 0.25:
            altura = random.choice((63, 87, 111))
            obstaculo = Obstaculo("passaro", LARGURA + 20,
                                  altura_passaro=altura)
        else:
            tipo = "grande" if random.random() < 0.38 else "pequeno"
            grupo = random.choices((1, 2, 3), weights=(65, 27, 8))[0]
            obstaculo = Obstaculo(tipo, LARGURA + 20, grupo)
        self.obstaculos.append(obstaculo)
        # Espacamento baseado em distancia, para dar tempo de reagir.
        self.distancia_spawn = random.uniform(340, 520) + self.velocidade * 0.30

    def perder(self):
        self.estado = "fim"
        self.sons.tocar("colisao")
        self.recorde = max(self.recorde, int(self.pontos))
        salvar_recorde(self.recorde)

    def eventos(self, evento):
        if evento.type != pygame.KEYDOWN:
            return
        tecla = evento.key
        if tecla == pygame.K_m:
            self.sons.mudo = not self.sons.mudo
            return
        if tecla == pygame.K_n:
            self.noite_manual = not self.alvo_noite()
            self.sons.tocar("noite")
            return
        if tecla == pygame.K_t:
            self.noite_manual = None  # Retorna ao ciclo automatico
            return
        if tecla == pygame.K_p:
            if self.estado == "jogando":
                self.estado = "pausa"
            elif self.estado == "pausa":
                self.estado = "jogando"
            return
        if tecla in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            if self.estado in ("inicio", "fim"):
                self.reiniciar()
            if self.estado == "jogando" and self.dino.pular():
                self.sons.tocar("pulo")
        elif tecla == pygame.K_r and self.estado == "fim":
            self.reiniciar()
        elif tecla in (pygame.K_DOWN, pygame.K_s) and self.estado == "jogando":
            self.sons.tocar("agachar")

    def atualizar(self, dt):
        # As transicoes e as nuvens seguem suaves mesmo antes de iniciar.
        alvo = 1.0 if self.alvo_noite() else 0.0
        velocidade_transicao = 0.80
        passo = velocidade_transicao * dt
        if self.noite_visivel < alvo:
            self.noite_visivel = min(alvo, self.noite_visivel + passo)
        else:
            self.noite_visivel = max(alvo, self.noite_visivel - passo)

        for nuvem in self.nuvens:
            nuvem.atualizar(dt)
            if nuvem.x < -90:
                nuvem.x = LARGURA + random.randint(40, 250)
                nuvem.y = random.randint(67, 137)

        if self.noite_visivel > 0.75:
            self.tempo_meteoro -= dt
            if self.tempo_meteoro <= 0:
                self.meteoros.append(Meteoro())
                self.tempo_meteoro = random.uniform(5, 9)
        for meteoro in self.meteoros:
            meteoro.atualizar(dt)
        self.meteoros = [m for m in self.meteoros if m.vida > 0]

        if self.estado != "jogando":
            return

        self.pontos += dt * 12
        self.velocidade = min(850, 390 + self.pontos * 0.19)
        if int(self.pontos) >= self.proximo_marco:
            self.proximo_marco += 100
            self.sons.tocar("ponto")

        teclas = pygame.key.get_pressed()
        agachar = teclas[pygame.K_DOWN] or teclas[pygame.K_s]
        if self.dino.atualizar(dt, agachar):
            self.sons.tocar("pouso")

        self.deslocamento_chao = (self.deslocamento_chao + self.velocidade*dt) % 27
        self.distancia_spawn -= self.velocidade * dt
        if self.distancia_spawn <= 0:
            self.gerar_obstaculo()
        for obstaculo in self.obstaculos:
            obstaculo.atualizar(self.velocidade, dt)
            if self.dino.caixa().colliderect(obstaculo.caixa()):
                self.perder()
                break
        self.obstaculos = [o for o in self.obstaculos if o.x + o.largura > -20]

        self.tempo_poeira += dt
        if self.dino.no_chao and self.tempo_poeira >= 0.10:
            self.tempo_poeira = 0
            self.poeira.append([self.dino.x + 3, CHAO_Y - 2, 0.28])
        for p in self.poeira:
            p[0] -= self.velocidade * dt * 0.45
            p[2] -= dt
        self.poeira = [p for p in self.poeira if p[2] > 0]

    def desenhar_ceu(self, fundo, tinta, noite):
        if noite > 0.05:
            cor_lua = misturar(fundo, (238, 240, 240), noite)
            lua_x, lua_y = 770, 101
            pygame.draw.circle(janela, cor_lua, (lua_x, lua_y), 17)
            pygame.draw.circle(janela, fundo, (lua_x + 8, lua_y - 6), 17)
            cor_estrela = misturar(fundo, (221, 225, 231), noite * 0.86)
            for x, y, raio in self.estrelas:
                pygame.draw.circle(janela, cor_estrela, (x, y), raio)
            for meteoro in self.meteoros:
                meteoro.desenhar(cor_estrela)
        cor_nuvens = misturar(fundo, tinta, 0.23)
        for nuvem in self.nuvens:
            nuvem.desenhar(cor_nuvens)

    def desenhar_chao(self, tinta, fundo):
        pygame.draw.line(janela, tinta, (0, CHAO_Y), (LARGURA, CHAO_Y), 2)
        detalhe = misturar(fundo, tinta, 0.52)
        for x, largura in self.detalhes_chao:
            px = round((x - self.deslocamento_chao) % (LARGURA + 42))
            pygame.draw.line(janela, detalhe, (px, CHAO_Y + 8),
                             (px + largura, CHAO_Y + 8), 1)
        for x, _, vida in self.poeira:
            if vida > 0:
                pygame.draw.rect(janela, detalhe, (round(x), CHAO_Y - 2, 3, 2))

    def desenhar_placar(self, tinta, fundo):
        escrito = f"HI {self.recorde:05d}  {int(self.pontos):05d}"
        escrever(escrito, fonte, misturar(fundo, tinta, 0.7), topo=(760, 24))
        escrever("COMUNIDADE SAMUEL MAGGI  //  PYTHON", fonte_pequena,
                 misturar(fundo, tinta, 0.52), topo=(25, 23))
        estado_som = "OFF" if self.sons.mudo or not self.sons.ativo else "ON"
        escrever(f"M SOM: {estado_som}   N NOITE   T AUTO", fonte_pequena,
                 misturar(fundo, tinta, 0.45), topo=(25, ALTURA - 29))

    def desenhar_mensagem(self, fundo, tinta):
        if self.estado == "inicio":
            escrever("CHROME DINO // PYTHON", fonte_grande, tinta,
                     centro=(LARGURA//2, 115))
            escrever("PRESSIONE ESPACO PARA COMECAR", fonte, tinta,
                     centro=(LARGURA//2, 159))
        elif self.estado == "fim":
            escrever("GAME OVER", fonte_grande, tinta,
                     centro=(LARGURA//2, 111))
            escrever("ESPAÇO OU R PARA REINICIAR", fonte, tinta,
                     centro=(LARGURA//2, 153))
            # Ícone de reinício estilizado, sem precisar de imagem.
            pygame.draw.arc(janela, tinta,
                            (LARGURA//2 - 15, 184, 30, 30), 0.25, 5.6, 3)
            pygame.draw.polygon(janela, tinta, [(484, 189), (488, 203), (496, 194)])
        elif self.estado == "pausa":
            escrever("PAUSADO  •  P PARA VOLTAR", fonte_grande, tinta,
                     centro=(LARGURA//2, 132))

    def desenhar(self):
        # Quantizar a cor reduz muito as variacoes no cache de sprites.
        noite = round(self.noite_visivel * 20) / 20
        fundo = misturar(FUNDO_DIA, FUNDO_NOITE, noite)
        tinta = misturar(TINTA_DIA, TINTA_NOITE, noite)
        janela.fill(fundo)
        self.desenhar_ceu(fundo, tinta, noite)
        self.desenhar_chao(tinta, fundo)
        for obstaculo in self.obstaculos:
            obstaculo.desenhar(tinta)
        self.dino.desenhar(tinta)
        self.desenhar_placar(tinta, fundo)
        self.desenhar_mensagem(fundo, tinta)
        pygame.display.flip()


def main():
    jogo = Jogo()
    rodando = True
    while rodando:
        dt = min(relogio.tick(FPS) / 1000.0, 0.05)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            else:
                jogo.eventos(evento)
        jogo.atualizar(dt)
        jogo.desenhar()
    salvar_recorde(max(jogo.recorde, int(jogo.pontos)))
    pygame.quit()


if __name__ == "__main__":
    main()
