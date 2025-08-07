from typing import List,Any

from app.api.excel.classes.db import Db,RelacoesDict
from app.api.excel.classes.singleton import Singleton

class Excel(metaclass=Singleton):
    def __init__(self):
        if not hasattr(self, '_db'):
            self._db = Db()

    @property
    def db(self)-> Db:
        return self._db

    def pesquisar(self,colunas: List[List[str]], tabelas: List[List[str]],criterios: List[List[Any]] = None, criterios_tabelas: List[List[str]] = None,relacoes: List[List[str]] = None,caractere_especial = "-") -> List[List[Any]]:
        '''
        Realiza uma pesquisa na base de dados utilizando os parâmetros fornecidos para colunas, tabelas, critérios, relações e caractere especial.
        Args:
            colunas (List[List[str]]): Lista contendo uma linha com os nomes das colunas a serem selecionadas.
            tabelas (List[List[str]]): Lista contendo uma linha com os nomes das tabelas a serem consultadas.
            criterios (List[List[Any]], optional): Lista contendo ao menos duas linhas, uma para os nomes das colunas e outra para os valores dos critérios de filtragem. Pode ser None.
            criterios_tabelas (List[List[str]], optional): Lista contendo uma linha com os nomes das tabelas relacionadas aos critérios. Pode ser None.
            relacoes (List[List[str]], optional): Lista contendo as relações entre as tabelas com 5 colunas: tabela A, tabela B, Coluna tabela A, Coluna Tabela B, Relação(inner, left, right). Pode ser None.
            caractere_especial (str, optional): Caractere especial utilizado na consulta. Padrão é "-".
        Returns:
            List[List[Any]]: Resultado da consulta, contendo os dados encontrados conforme os parâmetros informados.
        Raises:
            ValueError: Se as listas de colunas, tabelas ou critérios não estiverem no formato esperado.
        '''
        
        #Testa se colunas possúi apenas uma linha
        if len(colunas) != 1:
            raise ValueError("A lista de colunas deve conter apenas uma linha com os nomes das colunas.")
        
        #Coleta as colunas em uma lista
        colunas_ok = [col for col in colunas[0]]

        #Testa se tabelas possúi apenas uma linha
        if len(tabelas) != 1:
            raise ValueError("A lista de tabelas deve conter apenas uma linha com os nomes das tabelas.")
        #Coleta as tabelas em uma lista
        tabelas_ok = [tabela for tabela in tabelas[0]]

        #Testa se criterios possúi ao menos 2 linhas ou é None
        if criterios is not None and len(criterios) < 2:
            raise ValueError("A lista de critérios deve conter pelo menos duas linhas, uma para os nomes das colunas e outra para os valores dos critérios.")
        
        #Testa se criterios_tabelas possúi apenas uma linha ou é None
        if criterios_tabelas is not None and len(criterios_tabelas) != 1:
            raise ValueError("A lista de tabelas de critérios deve conter apenas uma linha com os nomes das tabelas.")
        
        #Coleta os critérios em uma lista
        criterios_tabelas_ok = criterios_tabelas[0]

        #Gea as relações
        relacoes_ok = None
        if relacoes is not None:
            relacoes_ok = []
            for relacao in relacoes:
                if len(relacao) not in [4,5]:
                    raise ValueError("Cada relação deve conter exatamente 4 ou 5 colunas: tabela A, tabela B, coluna A, coluna B e tipo de relação (inner, left, right) padrão é right.")
                relacao_dict: RelacoesDict = {
                    "tabela_a": relacao[0],
                    "tabela_b": relacao[1],
                    "coluna_a": relacao[2],
                    "coluna_b": relacao[3],
                    "tipo": 'right' if len(relacao) == 4 else relacao[4]  # Tipo de relação: "inner", "left", "right"
                }
                relacoes_ok.append(relacao_dict)
        
        #Pesquisa
        resultado = self.db.consultar_base(
            colunas=colunas_ok,
            tabelas=tabelas_ok,
            criterios=criterios,
            tabelas_criterios=criterios_tabelas_ok,
            relacoes=relacoes_ok,
            caractere_invalido=caractere_especial)
        
        #Retorna o resultado
        return resultado

    def atualizar(self, tabela: str, matriz:List[List[Any]]) -> List[Any]:
        '''
        Recebe uma matriz com o id na primeira coluna e MD na última coluna.
        A última coluna deve conter 'A' (Atualizar/Incluir) ou 'D' (Excluir).
        Retorna uma lista com os ids atualizados ou excluídos.
        Exemplo de matriz:
        [
            ['id', 'name', 'email', 'MD'],
            [1, 'Ricardo', 'ricardo@example.com', 'A'],
            [2, 'Maria', 'maria@example.com', 'D'],
            [0, 'João', 'joao@example.com', 'A'],
            [0, 'João', 'joao@example.com', ''],
        ]
        Exemplo de retorno:
        [1, 'D', 3,'']
        
        Onde:
        - A primeira linha contém os nomes das colunas.
        - A primeira coluna contém os ids (0 para novo registro).
        - A última coluna contém 'A' para atualizar ou incluir e 'D' para excluir.
        Retorno:
        Uma lista com os ids atualizados ou excluídos "D" para excluídos "" para nada e o id para atualizados.
        '''
        
        #Verifica o tamanho da matriz
        if matriz and len(matriz[0]) <=1 or len(matriz)<=1:
            raise ValueError("Tamanho da matriz inválida. Deve conter pelo menos duas colunas e duas linhas.")
        
        #Verifica se na última coluna da matriz existe a coluna chamada "MD"
        if matriz[0][-1] != "MD":
            raise ValueError("A última coluna da matriz deve ser chamada 'MD' para indicar a ação de atualização A (Atualizar ou Incluir) ou D (Excluir).")

        #Separa as linhas da matriz em dois grupos: atualizar_incluir e excluir
        ids = [''] #inicializa ids com uma string vazia (cabeçalho)
        matriz_atualizar_incluir = [matriz[0][:-1]]  # Mantém a primeira linha (cabeçalho) sem a última coluna
        matriz_excluir = []
        for linha_pos, linha in enumerate(matriz[1:]):
            if linha[-1].upper() not in ['A', 'D','']:
                raise ValueError(f"A última coluna da matriz deve conter 'A' (Atualizar/Incluir) ou 'D' (Excluir), erro na linha {linha_pos + 2}.")
            
            tipo = linha[-1].upper()
            if tipo == 'A':
                matriz_atualizar_incluir.append(linha[:-1])
            elif tipo == 'D':
                matriz_excluir.append(linha[0])
            ids.append(tipo)

        #Exclui os dados se necessário
        if matriz_excluir:
            self.db.remover(tabela, matriz_excluir)

        #Atualiza ou inclui os dados
        if len(matriz_atualizar_incluir)>1:
            print(matriz_atualizar_incluir)
            novos_ids = self.db.atualizar(tabela, matriz_atualizar_incluir)
            for i, id in enumerate(ids):
                if id == 'A':
                    ids[i] = novos_ids.pop(0)

        #Retorna
        return ids
    
    def coletar_estrutura(self, tabelas: List[str]):
        estrutura = self.db.estrutura
        return {tabela: estrutura[tabela] for tabela in tabelas if tabela in estrutura}

if __name__ == "__main__":
    excel = Excel()
    excel.db.criar_tabelas()  # Cria as tabelas se não existirem
    
    # Exemplo de uso para atualizar (inclusão de registros em usuarios)
    usuarios = [
        ['id', 'name', 'email', 'idade', 'uf', 'observacao', 'salario', 'data_nascimento', 'eh_funcionario', 'interesses', 'MD'],
        [0, 'Ricardo', 'ricardo@example.com', 30, 'SP', 'Observação 1', 3000.0, '1990-01-01', True, ['interesse1', 'interesse2'], 'A'],
        [1, 'Maria', 'maria@example.com', 25, 'RJ', 'Observação 2', 2500.0, '1995-02-02', False, ['interesse2'], 'A'],
        [2, 'João', 'joao@example.com', 28, 'SP', 'Observação 3', 2800.0, '1992-03-03', True, ['interesse1'], 'A'],
    ]
    resultado = excel.atualizar('users', usuarios)
    print("Resultado da atualização:", resultado)

    resultado = excel.pesquisar(
        tabelas=[['users','users','users','users']],
        colunas=[['id', 'name', 'email', 'idade']],
        criterios_tabelas=[['users']],
        criterios=[['uf'], ['SP']],
    )
    print("Resultado da pesquisa:", resultado)