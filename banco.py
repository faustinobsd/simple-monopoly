from configparser import NoSectionError
from random import randint, getrandbits, shuffle
from dataclasses import dataclass
from typing import List
from collections import Counter
import operator
from Dados import propriedades


@dataclass
class Comportamento:
    """
    Classe que representa o comportamento de um jogador.

    Atributos
    ----------
    impulsivo : bool
        Compra qualquer propriedade sobre a qual ele parar.
    exigente : bool
        Compra qualquer propriedade, desde que o valor do aluguel dela seja maior do que 50.
    cauteloso : bool
        Compra qualquer propriedade desde que ele tenha uma reserva de 80 saldo sobrando depois de realizada a compra.
    aleatorio : bool
        Compra a propriedade que ele parar em cima com probabilidade de 50%.

    Métodos
    -------
    decide_compra(custo_propriedade, valor_aluguel, saldo):
        Decide se irá comprar uma propriedade baseado no comportamento do jogador.
    """
    impulsivo: bool = False
    exigente: bool = False
    cauteloso: bool = False
    aleatorio: bool = False

    def decide_compra(self, custo_propriedade, valor_aluguel, saldo):
        """Decide se irá comprar uma propriedade baseado no comportamento do jogador.

        Args:
            custo_propriedade (int): Valor de compra da propriedade
            valor_aluguel (int): Valor do aluguel da propriedade
            saldo (int): Saldo do jogador

        Retorna:
            bool: True se compra, False se não compra.
        """
        if self.impulsivo:
            return True
        if self.exigente and valor_aluguel >= 50:
            return True
        if self.cauteloso and (saldo - custo_propriedade) >= 80:
            return True
        if self.aleatorio:
            return getrandbits(1) # Gera um bool aleatorio com 50% de chance

        return False


@dataclass
class Jogador:
    """Representa um jogador dentro do jogo"""
    nome: str
    saldo: int
    comportamento: Comportamento
    posicao_tabuleiro: int = 0
    falido: bool = False

    def joga_dado(self):
        """Joga um dado e retorna um numero de 1 a 6"""
        valor = randint(1,6)
        return valor

    def executa_jogada(self, tabuleiro):
        """Joga um dado, move-se pelo tabuleiro e decide"""
        qtd_posicoes_andar = self.joga_dado()

        if self.posicao_tabuleiro + qtd_posicoes_andar > 20:
            self.posicao_tabuleiro = self.posicao_tabuleiro + qtd_posicoes_andar - 20
            self.saldo += 100
        else:
            self.posicao_tabuleiro += qtd_posicoes_andar

        propriedade = tabuleiro.propriedades[self.posicao_tabuleiro-1]

        if not propriedade.dono:
            compra = self.comportamento.decide_compra(propriedade.custo_venda, propriedade.valor_aluguel, self.saldo)

            if compra:
                propriedade.dono = self
                self.saldo -= propriedade.custo_venda
        else:
            self.saldo -= propriedade.valor_aluguel

        if self.saldo < 0:
            self.falido = True

    def retorna_comportamento(self):
        """Retorna o nome do comportamento do jogador"""
        if self.comportamento.impulsivo:
            return "impulsivo"
        if self.comportamento.exigente:
            return "exigente"
        if self.comportamento.cauteloso:
            return "cauteloso"
        if self.comportamento.aleatorio:
            return "aleatorio"


@dataclass
class Propriedade:
    """Representa uma propriedade dentro do jogo"""
    nome: str
    custo_venda: int
    valor_aluguel: int
    dono: Jogador = None
    posicao_tabuleiro: int = None


@dataclass
class Tabuleiro:
    """Representa o tabuleiro"""
    propriedades: List[Propriedade]

    def remove_jogador(self, jogador):
        """Remove jogador de todas as propriedades"""
        for propriedade in self.propriedades:
            if propriedade.dono == jogador:
                propriedade.dono = None


@dataclass
class Jogo:
    """Representa o jogo"""
    jogadores: List[Jogador]
    tabuleiro: Tabuleiro
    rodada: int = 0
    jogadores_falidos: int = 0

    def play(self):
        """Joga o jogo e retorna os resultados"""
        while self.rodada < 1000 and self.jogadores_falidos < 3:
            for jogador in self.jogadores:
                if jogador.falido:
                    continue

                jogador.executa_jogada(self.tabuleiro)
                if jogador.falido:
                    self.tabuleiro.remove_jogador(jogador)
                    self.jogadores_falidos += 1

                if self.jogadores_falidos > 2:
                    break

            self.rodada += 1

        time_out = 1 if self.rodada == 1000 and self.jogadores_falidos < 3 else 0

        vencedor = None
        for jogador in self.jogadores:
            if not vencedor:
                vencedor = jogador
            elif jogador.saldo > vencedor.saldo:
                vencedor = jogador


        comportamento_vencedor = vencedor.retorna_comportamento()
        resultado = {"timeout": time_out, "turnos": self.rodada, comportamento_vencedor: 1}
        self.reset()

        return Counter(resultado)


    def reset(self):
        """Reseta as classes para limpeza"""
        self.jogadores = None
        self.tabuleiro = None
        self.rodada = 0
        self.jogadores_falidos = 0


def setup_jogo():
    """
    Instancia jogadores, randomiza suas posições e adiciona propriedades ao tabuleiro.

    Retorna: Objeto Jogo
    """

    # Instancia os jogadores
    lista_jogadores = []
    lista_jogadores.append(Jogador("Jogador1", 300, Comportamento(impulsivo=True)))
    lista_jogadores.append(Jogador("Jogador2", 300, Comportamento(exigente=True)))
    lista_jogadores.append(Jogador("Jogador3", 300, Comportamento(cauteloso=True)))
    lista_jogadores.append(Jogador("Jogador4", 300, Comportamento(aleatorio=True)))

    # Randomiza a lista de jogadores
    shuffle(lista_jogadores)

    # Instancia a lista de propriedades
    lista_propriedades = []
    # Adiciona as propriedades ao tabuleiro
    for prop in propriedades.lista:
        lista_propriedades.append(
            Propriedade(
                nome = prop["nome"],
                custo_venda = prop["custo_venda"],
                valor_aluguel = prop["valor_aluguel"]
            )
        )

    # Instancia o jogo
    jogo = Jogo(
        jogadores = lista_jogadores,
        tabuleiro = Tabuleiro(lista_propriedades)
    )

    return jogo


def inicia_jogo(jogo):
    return jogo.play()


if __name__ == "__main__":
    turnos = 300

    resultado_final = {
        "timeout": 0,
        "turnos": 0,
        "impulsivo": 0,
        "exigente": 0,
        "cauteloso": 0,
        "aleatorio": 0
    }
    resultado_final_counter = Counter(resultado_final)


    for i in range(turnos):
        #print(f"\r\n ========== Iniciando jogo número {i} ========== \r\n")
        jogo = setup_jogo()
        resultado = inicia_jogo(jogo)
        resultado_final_counter += resultado

    resultado_final.update(dict(resultado_final_counter))

    porcentagem_vitorias_comportamento = {
        "impulsivo": (resultado_final["impulsivo"]/turnos) * 100,
        "exigente": (resultado_final["exigente"]/turnos) * 100,
        "cauteloso": (resultado_final["cauteloso"]/turnos) * 100,
        "aleatorio": (resultado_final["aleatorio"]/turnos) * 100
    }

    comportamento_vencedor = max(porcentagem_vitorias_comportamento.items(), key=operator.itemgetter(1))[0]

    print(f"\r\n === RESULTADOS === \r\n")
    print(f"Partidas terminadas por timeout: {resultado_final['timeout']:.0f}")
    print(f"Média de turnos por partida: {resultado_final['turnos']/turnos}")
    print(f"Porcentagem de vitórias por comportamento:")
    print(f"\t Impulsivo: {porcentagem_vitorias_comportamento['impulsivo']:.2f}%")
    print(f"\t Exigente: {porcentagem_vitorias_comportamento['exigente']:.2f}%")
    print(f"\t Cauteloso: {porcentagem_vitorias_comportamento['cauteloso']:.2f}%")
    print(f"\t Aleatório: {porcentagem_vitorias_comportamento['aleatorio']:.2f}%")
    print(f"Comportamento que mais vence: {comportamento_vencedor}")