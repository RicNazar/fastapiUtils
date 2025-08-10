from sqlalchemy import column, create_engine, select,insert,delete,update, and_, or_, Engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
import importlib
import pkgutil
import json
from typing import List,Dict,TypedDict,Literal,Any,Type,Optional

#Imports internos
from app.api.excel.classes.dbBases import Base

#Tipagem
class ColunaDict(TypedDict):
    tipo: str
    unica: bool
    primaria: bool
    autoincremento: Optional[bool]
    anulavel: bool

EstruturaTabela = Dict[str, Dict[str, ColunaDict]]

# Tipos de relações SQL comuns
tiposJoins = Literal[
    "left",
    "right",
    "inner",
]

class RelacoesDict(TypedDict):
    tabela_a: str
    tabela_b: str
    coluna_a: str
    coluna_b: str
    tipo: tiposJoins

'''
estrutura = {
    "tabela1": {
        "coluna1": {
            "tipo": "INTEGER",
            "unica": False,
            "primaria": True,
            "anulavel": False,
            "chaveEstrangeira": True,
            "referencia": {
                "tabela": "usuarios",
                "coluna": "id"
            }
        }
    }
}
'''
#Classe de Apoio
class _Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
#Classe principal
class Db(metaclass=_Singleton):
    @property
    def estrutura(self) -> EstruturaTabela:
        return self._estrutura

    @property
    def base(self):
        return self._base
    
    @property
    def engine(self) -> Engine:
        return self._engine
    
    def _importar_models(self,package_name):
        package = importlib.import_module(package_name)
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                importlib.import_module(f"{package_name}.{module_name}")

    def _gerar_dict_estrutura(self,base) -> EstruturaTabela:
        estrutura = {}
        for table_name, table in base.metadata.tables.items():
            estrutura[table_name] = {}
            for column_name, column in table.columns.items():
                estrutura[table_name][column.name] = {
                    "tipo": str(column.type),
                    "unica": column.unique or False,
                    "primaria": column.primary_key,
                    "anulavel": column.nullable,
                    "autoincremento": column.primary_key and column.autoincrement == "auto",
                }
        return estrutura

    def _gerar_dict_primarias(self,base) -> Dict[str, str]:
        primarias = {}
        for table_name, table in base.metadata.tables.items():
            for column in table.columns:
                if column.primary_key:
                    primarias[table_name] = column.name
                    break
        return primarias

    def __init__(self, database_url: str = None, env_path: str = ".env"):
        if not hasattr(self, "_initialized"):
            if not database_url:
                load_dotenv(env_path)
                database_url = os.getenv("DATABASE_URL")
                if not database_url:
                    raise ValueError("DATABASE_URL não está definida no arquivo .env")
            self._engine = create_engine(database_url, echo=True)
            self._session_factory = sessionmaker(bind=self._engine, autocommit=False, autoflush=False)
            self._base = Base
            self._initialized = True
            self._importar_models("app.api.excel.models")
            self._estrutura = self._gerar_dict_estrutura(self._base)
            self._primarias = self._gerar_dict_primarias(self._base)

            # Verifica se a estrutura foi carregada corretamente
            if not self._estrutura:
                raise ValueError("A estrutura do banco de dados não foi carregada corretamente.")
            if not self._primarias:
                raise ValueError("As chaves primárias não foram carregadas corretamente.")

    def __enter__(self) -> Session:
        self._session = self._session_factory()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
        finally:
            self._session.close()
            self._session = None
    
    def criar_tabelas(self):
        self._base.metadata.create_all(bind=self._engine)
    
    def obter_valor(self,valor, tipo:str=None,tabela:str=None,coluna:str=None) -> Any:
        '''
        dado valor e o tipo (opcional) ou tabela e coluna (opcional) retorna o valor convertido para o tipo correto
        '''
        if tabela and coluna:
            tipo = self._estrutura[tabela][coluna]["tipo"]
        
        if not tipo:
            raise ValueError("Tipo não especificado e não encontrado na estrutura do banco de dados.")
        
        if valor is None:
            return None

        tipo = tipo.lower()
        if "json" in tipo:
            if isinstance(valor, (list, dict)):
                return valor
            try:
                return json.loads(valor)
            except Exception:
                return valor
        elif "integer" in tipo:
            try:
                return int(valor)
            except Exception:
                return valor
        elif "float" in tipo or "double" in tipo or "numeric" in tipo or "real" in tipo or "decimal" in tipo:
            try:
                return float(valor)
            except Exception:
                return valor
        elif "boolean" in tipo or "bool" in tipo:
            if isinstance(valor, bool):
                return valor
            if isinstance(valor, (int, float)):
                return valor != 0
            if isinstance(valor, str):
                return valor.strip().lower() in ["true", "1", "yes", "y", "sim", "s"]
            return False
        elif "date" in tipo:
            from datetime import datetime
            if isinstance(valor, (datetime, )):
                return valor.date()
            if isinstance(valor, str):
                try:
                    return datetime.strptime(valor, "%Y-%m-%d").date()
                except Exception:
                    return valor
            return valor
        elif "time" in tipo:
            from datetime import datetime
            if isinstance(valor, (datetime, )):
                return valor.time()
            if isinstance(valor, str):
                try:
                    return datetime.strptime(valor, "%H:%M:%S").time()
                except Exception:
                    return valor
            return valor
        elif "datetime" in tipo or "timestamp" in tipo:
            from datetime import datetime
            if isinstance(valor, (datetime, )):
                return valor
            if isinstance(valor, str):
                try:
                    return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    return valor
            return valor
        else:
            return valor

    def formatar_valor(self,valor, tipo:str=None,tabela:str=None,coluna:str=None) -> str:
        '''
        Formata um valor com base no tipo fornecido ou na estrutura do banco de dados e retorna um texto
        '''
        if tabela and coluna:
            tipo = self._estrutura[tabela][coluna]["tipo"]
        if not tipo:
            raise ValueError("Tipo não especificado e não encontrado na estrutura do banco de dados.")
        if valor is None:
            return ""
        tipo = tipo.lower()
        if "json" in tipo:
            if isinstance(valor, (list, dict)):
                if isinstance(valor, list):
                    return "; ".join(map(str, valor))
                return json.dumps(valor)
            try:
                obj = json.loads(valor)
                if isinstance(obj, list):
                    return "; ".join(map(str, obj))
                return json.dumps(obj)
            except Exception:
                return str(valor)
        elif "integer" in tipo:
            try:
                return f"{int(valor):,}".replace(",", ".")
            except Exception:
                return str(valor)
        elif "float" in tipo or "double" in tipo or "numeric" in tipo or "real" in tipo or "decimal" in tipo:
            try:
                return f"{float(valor):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except Exception:
                return str(valor)
        else:
            return str(valor)

    def imprimir_estrutura(self):
        """Imprime a estrutura do banco de dados de forma elegante"""
        print("\n" + "="*60)
        print("ESTRUTURA DO BANCO DE DADOS")
        print("="*60)
        
        for table_name, columns in self._estrutura.items():
            print(f"\n📋 Tabela: {table_name.upper()}")
            print("-" * 40)
            
            for column_name, details in columns.items():
                # Símbolos para indicar propriedades especiais
                symbols = []
                if details['primaria']:
                    symbols.append("🔑")  # Chave primária
                if details['unica']:
                    symbols.append("⭐")  # Único
                if not details['anulavel']:
                    symbols.append("❗")  # Não nulo
                
                symbol_str = " ".join(symbols) if symbols else ""
                
                print(f"  • {column_name:<15} | {details['tipo']:<15} {symbol_str}")
                
        
        print("\n" + "="*60)
        print("Legenda: 🔑 Chave Primária | ⭐ Único | ❗ Não Nulo")
        print("="*60 + "\n")
    
    def listar_dados_tabela(self, nome_tabela: str):
        """
        Lista os dados (linhas) de uma tabela específica em formato tabular,
        limitando cada coluna a 50 caracteres (com ...).
        """
        if nome_tabela not in self._estrutura:
            print(f"Tabela '{nome_tabela}' não encontrada na estrutura do banco de dados.")
            return

        # Importa dinamicamente o modelo da tabela
        try:
            model_module = importlib.import_module(f"app.api.excel.models.{nome_tabela}")
            model_class = getattr(model_module, nome_tabela.capitalize())
        except (ModuleNotFoundError, AttributeError):
            print(f"Modelo para a tabela '{nome_tabela}' não encontrado.")
            return

        def limitar(valor: str, limite: int = 50) -> str:
            valor = str(valor)
            if len(valor) > limite:
                return valor[:limite-3] + "..."
            return valor

        with self as session:
            rows = session.query(model_class).limit(10).all()
            if not rows:
                print(f"Nenhum dado encontrado na tabela '{nome_tabela}'.")
                return

            # Cabeçalho
            colunas = list(self._estrutura[nome_tabela].keys())
            print(f"\n📋 Dados da tabela: {nome_tabela.upper()}")
            print("-" * 40)
            print(" | ".join([f"{col:<15}" for col in colunas]))
            print("-" * 40)
            # Linhas
            for row in rows:
                linha = []
                for col in colunas:
                    tipo = self._estrutura[nome_tabela][col]["tipo"]
                    valor = getattr(row, col, "")
                    valor_formatado = self.formatar_valor(valor, tipo)
                    linha.append(f"{limitar(valor_formatado):<15}")
                print(" | ".join(linha))
            print("-" * 40)

    def consultar_base(self,colunas: List[str],tabelas: List[str],criterios: List[List[Any]] = None,tabelas_criterios: List[str] = None, relacoes: List[RelacoesDict] = None,caractere_invalido: str = "-")-> List[List[Any]]:
        #Testa se todas as tabelas estão na estrutura
        for tabela in tabelas:
            if tabela not in self._estrutura:
                raise ValueError(f"Tabela '{tabela}' não encontrada na estrutura do banco de dados.")
        
        #varre as colunas e tabelas
        colunas_ok = []
        colunas_posicoes = []
        for pos, coluna in enumerate(colunas):
            tabela = tabelas[pos]
            colunas_posicoes.append(-1)  # Inicializa com -1
            if tabela in self._estrutura:
                if coluna in self._estrutura[tabela]:
                    colunas_ok.append((tabela, coluna))
                    colunas_posicoes[-1] = len(colunas_ok)-1  # Atualiza a posição da coluna

        #testa se sobrou alguma coluna
        if not colunas_ok:
            raise ValueError("Nenhuma coluna válida encontrada nas tabelas especificadas.")
        
        #Cria o select
        stmt = select(*[getattr(importlib.import_module(f"app.api.excel.models.{t}"), t.capitalize()).__table__.c[c] for t, c in colunas_ok])

        #adiciona as relacoes
        if relacoes:
            for relacao in reversed(relacoes):
                tabela_a = relacao['tabela_a']
                tabela_b = relacao['tabela_b']
                coluna_a = relacao['coluna_a']
                coluna_b = relacao['coluna_b']
                tipo = relacao['tipo']

                # Coleta as classes dos modelos
                modelo_a = getattr(importlib.import_module(f"app.api.excel.models.{tabela_a}"), tabela_a.capitalize())
                modelo_b = getattr(importlib.import_module(f"app.api.excel.models.{tabela_b}"), tabela_b.capitalize())
                
                if tipo == "inner":
                    stmt = stmt.join(modelo_a, modelo_a.__table__.c[coluna_a] == modelo_b.__table__.c[coluna_b])
                elif tipo == "right":
                    stmt = stmt.join(modelo_b, modelo_a.__table__.c[coluna_a] == modelo_b.__table__.c[coluna_b],isouter=True)
                else:
                    #tipo == "left"
                    stmt = stmt.join(modelo_a, modelo_a.__table__.c[coluna_a] == modelo_b.__table__.c[coluna_b],isouter=True)

        #Adiciona as condições
        if criterios:
            if len(criterios)>1:
                #Verifica se tabelas critérios existe e cria uma lista repetindo tabelas[0] para todas as colunas de criterios
                if not tabelas_criterios:
                    tabelas_criterios = [tabelas[0] for t in tabelas]

                #Primeira linha o cabeçalho as demais linhas os critérios OU e colunas E
                crit_or = []
                for l, linha in enumerate(criterios[1:], start=1):
                    crit_and = []
                    for c, coluna in enumerate(linha):
                        tab = tabelas_criterios[c]
                        col = criterios[0][c]
                        #Coleta o sinal (início da string = >= < <= <>) e o valor
                        sinal = ""
                        if isinstance(coluna, str):
                            #Trata casos numéricos
                            if coluna.startswith(">"):
                                sinal = ">"
                            elif coluna.startswith("<"):
                                sinal = "<"
                            elif coluna.startswith("="):
                                sinal = "="
                            elif coluna.startswith(">="):
                                sinal = ">="
                            elif coluna.startswith("<="):
                                sinal = "<="
                            elif coluna.startswith("!=") or coluna.startswith("<>"):
                                sinal = "!="
                            coluna = coluna[len(sinal):].strip()
                            #Trata casos de texto
                            if coluna.startswith("*") and coluna.endswith("*"):
                                sinal = "**"
                                coluna = coluna[1:-1]
                            elif coluna.startswith("*"):
                                sinal = "*-"
                                coluna = coluna[1:]
                            elif coluna.endswith("*"):
                                sinal = "-*"
                                coluna = coluna[:-1]

                        #Trata o caso de or no critério caso tenha mais de uma coluna ;
                        if isinstance(coluna, str):
                            colunas_or = coluna.split(";")
                        else:
                            colunas_or = [coluna]
                        
                        #para cada item da coluna or, cria um critério
                        modelo = getattr(importlib.import_module(f"app.api.excel.models.{tab}"), tab.capitalize())
                        for col_or in colunas_or:
                            crit_and_or = []
                            valor_txt = self.formatar_valor(col_or,tabela = tab,coluna = col)
                            if valor_txt != "" or len(sinal) > 0:
                                valor_efetivo = self.obter_valor(col_or, tabela=tab, coluna=col)
                                if sinal == ">":
                                    crit_and_or.append(modelo.__table__.c[col] > valor_efetivo)
                                elif sinal == "<":
                                    crit_and_or.append(modelo.__table__.c[col] < valor_efetivo)
                                elif sinal == ">=":
                                    crit_and_or.append(modelo.__table__.c[col] >= valor_efetivo)
                                elif sinal == "<=":
                                    crit_and_or.append(modelo.__table__.c[col] <= valor_efetivo)
                                elif sinal == "**":
                                    crit_and_or.append(modelo.__table__.c[col].ilike(f"%{valor_efetivo}%"))
                                elif sinal == "*-":
                                    crit_and_or.append(modelo.__table__.c[col].ilike(f"%{valor_efetivo}"))
                                elif sinal == "-*":
                                    crit_and_or.append(modelo.__table__.c[col].ilike(f"{valor_efetivo}%"))
                                elif sinal == "!=":
                                    crit_and_or.append(modelo.__table__.c[col] != valor_efetivo)
                                    if valor_efetivo == "":
                                        crit_and_or.append(modelo.__table__.c[col].isnot_(None))
                                else:  # "=" ou sem sinal
                                    crit_and_or.append(modelo.__table__.c[col] == valor_efetivo)
                                    if valor_efetivo == "":
                                        crit_and_or.append(modelo.__table__.c[col].is_(None))
                            #Adiciona os critérios or se tiver algo
                            if crit_and_or:
                                if len(crit_and_or) == 1:
                                    crit_and.append(crit_and_or[0])
                                else:
                                    crit_and.append(or_(*crit_and_or))

                    #Adiciona a linha de critérios se tiver algo
                    if crit_and:
                        crit_or.append(and_(*crit_and))
                #Adiciona os critérios ao select se tiver algo
                if crit_or:
                    if len(crit_or) == 1:
                        stmt = stmt.where(crit_or[0])
                    else:
                        stmt = stmt.where(or_(*crit_or))

        #Executa o select
        with self as session:
            resultados = session.execute(stmt).all()
        
        #Formata os resultados gerando uma matriz
        resultados_formatados = []
        for row in resultados:
            linha_formatada = []
            for col in colunas_posicoes:
                if col >= 0:
                    linha_formatada.append(row[col])
                else:
                    linha_formatada.append(caractere_invalido)
            resultados_formatados.append(linha_formatada)

        return resultados_formatados

    def atualizar(self,tabela:str,matriz: List[List[Any]]):
        '''
        Atualiza os dados de uma tabela com base em uma matriz de dados.
        A matriz deve conter os dados na mesma ordem das colunas da tabela.
        Cada linha representa um registro a ser atualizado.
        '''
        if tabela not in self._estrutura:
            raise ValueError(f"Tabela '{tabela}' não encontrada na estrutura do banco de dados.")
        
        # Importa dinamicamente o modelo da tabela
        try:
            model_module = importlib.import_module(f"app.api.excel.models.{tabela}")
            model_class = getattr(model_module, tabela.capitalize())
        except (ModuleNotFoundError, AttributeError):
            raise ValueError(f"Modelo para a tabela '{tabela}' não encontrado.")
        
        #Coleta o nome da coluna de id
        coluna_id = self._primarias[tabela]
        if not coluna_id:
            raise ValueError(f"A tabela '{tabela}' não possui uma chave primária definida.")
        
        #Verifica se a primeira coluna é o id
        if matriz[0][0] != coluna_id:
            raise ValueError(f"A primeira coluna da matriz deve ser '{coluna_id}' para a tabela '{tabela}'.")

        #Verifica se é autoincremento
        coluna_autoincremento = self._estrutura[tabela][coluna_id]["autoincremento"]
        
        #Coleta as colunas válidas da primeira linha da matriz
        validos_cabecalho = []
        validos_dados = [[] for _ in range(len(matriz)-1)]  # Inicializa uma lista para cada linha
        for poscol, col in enumerate(matriz[0]):
            if col in self._estrutura[tabela]:
                validos_cabecalho.append(col)
                for poslin, lin in enumerate(matriz[1:]):
                    validos_dados[poslin].append(self.obter_valor(lin[poscol],tabela=tabela,coluna=col))

        #Processa os dados
        dados_ids = [] #salva os ids dos novos dados
        with self as session:
            #Coleta todos os ids da tabela
            ids_existentes = session.execute(select(getattr(model_class, coluna_id))).scalars().all()

            #Separa os dados entre novos e existentes
            dados_existentes = []
            dados_existentes_ids = []
            dados_novos = []
            dados_origens = [] #lista para saber de onde veio o dado
            
            for linha in validos_dados:  # Ignora o cabeçalho
                dados_existentes_ids.append(linha[0])  # Coleta o id da linha
                if linha[0] in ids_existentes:
                    dados_existentes.append(linha)
                    dados_origens.append("e")
                else:
                    dados_novos.append(linha)
                    dados_origens.append("n")

            #Caso existam dados existentes, pesquisa na base os campos validos_cabecalhos para os ids dados_existentes_ids
            if dados_existentes:
                # Atualiza para processar no máximo 900 ids por vez
                resultados_existentes = []
                for i in range(0, len(dados_existentes_ids), 900):
                    ids_lote = dados_existentes_ids[i:i+900]
                    stmt = select(*[getattr(model_class, col) for col in validos_cabecalho]).where(
                        getattr(model_class, coluna_id).in_(ids_lote)
                    )
                    resultados_existentes.extend(session.execute(stmt).all())

                #Gera o dados atualizar caso algum campo tenha sido alterado
                dados_atualizar = [] #estrutura de blocos a serem atualizados [[{coluna_id: valor, coluna1: valor1, ...}, ...],[{coluna_id: valor, coluna1: valor1, ...}, ...]]
                dados_atualizar_bloco_atual = -1
                total_campos = 0

                for poslin, linha in enumerate(dados_existentes):
                    #gera a linha de atualização
                    linha_atualizar = {}
                    linha_atualizar[coluna_id] = linha[0]
                    for poscol, col in enumerate(linha[1:], 1):  # Ignora o id
                        if col != resultados_existentes[poslin][poscol]:
                            linha_atualizar[validos_cabecalho[poscol]] = col
                    
                    # Adiciona a linha de atualização se houver alguma alteração
                    if len(linha_atualizar)>1:
                        # Limite de 900 campos por bloco
                        if total_campos >= 900 or dados_atualizar_bloco_atual == -1:  
                            dados_atualizar.append([])
                            total_campos = 0
                            dados_atualizar_bloco_atual += 1
                        # Adiciona a linha de atualização ao bloco atual
                        dados_atualizar[dados_atualizar_bloco_atual].append(linha_atualizar)
                        total_campos += len(linha_atualizar)

                # Atualiza os dados existentes utilizando bulk
                if dados_atualizar:
                    for bloco in dados_atualizar:
                        session.execute(
                            update(model_class),
                            bloco
                        )
                        session.flush()
                
            #Se houver dados novos, adiciona-os
            if dados_novos:
                dados_incluir = []  # estrutura de blocos a serem inseridos [[{coluna1: valor1, ...}, ...],[{coluna1: valor1, ...}, ...]]
                dados_novos_bloco_atual = -1
                total_campos = 0
                # Processa os dados novos
                for poslin, linha in enumerate(dados_novos):
                    novo_dado = {col: valor for col, valor in zip(validos_cabecalho, linha)}
                    if coluna_autoincremento and coluna_id in novo_dado:
                        del novo_dado[coluna_id]  # Remove o id se for autoincremento
                    # Limite de 900 campos por bloco
                    if total_campos >= 900 or dados_novos_bloco_atual == -1:
                        dados_incluir.append([])
                        dados_novos_bloco_atual += 1
                        total_campos = 0
                    # Adiciona o novo dado ao bloco atual
                    dados_incluir[dados_novos_bloco_atual].append(novo_dado)
                    total_campos += len(novo_dado)

                # Insere os novos dados e obtém o id
                for bloco in dados_incluir:
                    stmt = insert(model_class).returning(getattr(model_class, coluna_id))
                    result = session.execute(stmt, bloco)
                    dados_ids.extend(result.scalars().all())

        # Gera uma lista de ids com o mesmo número de linhas de validos_dados com base nos dados_origens e dados_ids
        dados_ids_final = []
        for pos, origem in enumerate(dados_origens):
            if origem == "e":
                dados_ids_final.append(dados_existentes_ids[pos])
            elif origem == "n":
                dados_ids_final.append(dados_ids.pop(0))  # Pega o próximo id dos novos dados

        #Retorne os ids atualizados
        return dados_ids_final
    
    def remover(self,tabela:str,ids: List[Any]):
        '''
        Remove registros de uma tabela com base em uma lista de ids.
        A lista de ids deve conter os valores da chave primária da tabela.
        '''
        if tabela not in self._estrutura:
            raise ValueError(f"Tabela '{tabela}' não encontrada na estrutura do banco de dados.")
        
        # Importa dinamicamente o modelo da tabela
        try:
            model_module = importlib.import_module(f"app.api.excel.models.{tabela}")
            model_class = getattr(model_module, tabela.capitalize())
        except (ModuleNotFoundError, AttributeError):
            raise ValueError(f"Modelo para a tabela '{tabela}' não encontrado.")
        
        #Coleta o nome da coluna de id
        coluna_id = self._primarias[tabela]
        if not coluna_id:
            raise ValueError(f"A tabela '{tabela}' não possui uma chave primária definida.")
        
        #Verifica se os ids são válidos
        if not ids:
            raise ValueError("A lista de ids não pode estar vazia.")
        
        #processa a remoção dos ids passados
        with self as session:
            # Remove em lotes de até 900 ids por vez usando SQLAlchemy 2.0 style
            for i in range(0, len(ids), 900):
                ids_lote = ids[i:i+900]
                stmt = delete(model_class).where(getattr(model_class, coluna_id).in_(ids_lote))
                session.execute(stmt)
                session.flush()

    
if __name__ == "__main__":
    # Create the database instance
    db = Db()
    
    # Cria a tabela de testes
    db.criar_tabelas()
    db.imprimir_estrutura()

    # Adiciona dados de exemplo
    ids_atualizar = db.atualizar("users", [
        ["id","name", "email","idade","uf","interesses","observacao"],
        [0,"John Doe", "john@example.com", 30, "SP", ["tecnologia", "esportes"], ""],
        [0,"Jane Smith", "jane@example.com", 25, "RJ", ["musica", "arte"], "Observação 2"],
        [0,"Ricardo", "ricardo@example.com", 28, "MG", ["cinema", "literatura"], ""]
    ])
    print("IDs atualizados:", ids_atualizar)
    db.listar_dados_tabela("users")

    # Adiciona dados de exemplo
    ids_atualizar = db.atualizar("users", [
        ["id","name", "email","idade","uf","interesses"],
        [20,"Ricardo Novo", "ricardoNovo@example.com", 28, "MG", ["cinema", "literatura"]],
        [3,"Ricardo Atualizar", "ricardoAtualizar@example.com", 28, "MG", ["cinema", "literatura"]]
    ])
    print("\nApós atualização:")
    db.listar_dados_tabela("users")
    print("IDs atualizados:", ids_atualizar)

    # Pesquisa
    resultados = db.consultar_base(
        colunas=["id", "name", "email","diacho"],
        tabelas=["users","users","users","users"],
        criterios=[["observacao"], [""]]
        )
    print("\nResultados da consulta:")
    for linha in resultados:
        print(linha)
    
    # Remove dados
    db.remover("users", [1, 2, 20])
    print("\nApós remoção:")
    db.listar_dados_tabela("users")

    #Adiciona orders
    ids_atualizar = db.atualizar("orders", [
        ["id", "user_id", "product", "quantity", "price", "order_date", "status"],
        [0, 2, "Notebook Dell", 1, 3500.00, "2024-06-01", "completed"],
        [0, 3, "Mouse Logitech", 2, 120.50, "2024-06-02", "pending"],
        [0, 2, "Teclado Mecânico", 1, 450.00, "2024-06-03", "shipped"],
        [0, 20, "Monitor LG", 1, 1200.00, "2024-06-04", "completed"],
        [0, 3, "Cadeira Gamer", 1, 950.00, "2024-06-05", "cancelled"],
        [0, 2, "Headset HyperX", 1, 350.00, "2024-06-06", "pending"],
    ])
    print("IDs atualizados:", ids_atualizar)
    db.listar_dados_tabela("orders")
    db.listar_dados_tabela("users")

    # Adiciona uma relação entre as tabelas users e orders
    relacao_users_orders: RelacoesDict = {
            "tabela_a": "users",
            "tabela_b": "orders",
            "coluna_a": "id",
            "coluna_b": "user_id",
            "tipo": "left"  # Tipo de relação: "left", "right", "inner"
        }

    #Pesquisa as orders do cliente "Ricardo"
    resultados = db.consultar_base(
        colunas=["id", "name", "email","product","amount","price"],
        tabelas=["users","users","users","orders","orders","orders"],
        criterios=[["uf"], ["MG"]],
        tabelas_criterios=["users"],
        relacoes=[
            relacao_users_orders
        ]
        )
    print("\nResultados da consulta com relação:")
    for linha in resultados:
        print(linha)
    
    #Pesquisa as orders do cliente "Ricardo"
    resultados = db.consultar_base(
        colunas=["id", "name", "email","product","amount","price"],
        tabelas=["users","users","users","orders","orders","orders"],
        relacoes=[
            relacao_users_orders
        ]
        )
    print("\nResultados da consulta com relação:")
    for linha in resultados:
        print(linha)