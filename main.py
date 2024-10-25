import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase

class Neo4jCRUD:
    def __init__(self, uri, usuario, senha):
        self.driver = GraphDatabase.driver(uri, auth=(usuario, senha))

    def fechar_conexao(self):
        self.driver.close()

    def criar_funcionario(self, nome, idade, email, telefone, nome_empresa, cargo, setor):
        with self.driver.session() as session:
            existe = session.run("MATCH (f:Funcionario) WHERE f.nome = $nome RETURN f", nome=nome)
            if existe.peek() is not None:
                print(f"Erro: Já existe um funcionário com o nome {nome}.")
                return

            session.run("""
                CREATE (f:Funcionario {nome: $nome, idade: $idade, email: $email, telefone: $telefone})
            """, nome=nome, idade=idade, email=email, telefone=telefone)

            empresa_existe = session.run("MATCH (e:Empresa {nome: $nome_empresa}) RETURN e", nome_empresa=nome_empresa)
            if empresa_existe.peek() is None:
                session.run("CREATE (e:Empresa {nome: $nome_empresa, setor: $setor})", nome_empresa=nome_empresa, setor=setor)
                print(f"Empresa {nome_empresa} criada no setor {setor}.")

            session.run("""
                MATCH (f:Funcionario {nome: $nome}), (e:Empresa {nome: $nome_empresa})
                CREATE (f)-[:TRABALHA_EM {cargo: $cargo}]->(e)
            """, nome=nome, nome_empresa=nome_empresa, cargo=cargo)
            print(f"Funcionario {nome} criado e relacionado à empresa {nome_empresa} como {cargo}.")

    def buscar_funcionario(self, nome):
        with self.driver.session() as session:
            resultado = session.run("""
                MATCH (f:Funcionario {nome: $nome})
                OPTIONAL MATCH (f)-[r:TRABALHA_EM]->(e:Empresa)
                RETURN f, e, r.cargo AS cargo
            """, nome=nome)

            funcionario_encontrado = False
            for registro in resultado:
                funcionario = registro["f"]
                empresa = registro["e"]
                cargo = registro["cargo"]

                print(f"\nID: {funcionario.id}, Nome: {funcionario['nome']}\nIdade: {funcionario['idade']}\nEmail: {funcionario['email']}\nTelefone: {funcionario['telefone']}")
                if empresa:
                    print(f"\nEmpresa: {empresa['nome']}\nSetor: {empresa['setor']}\nCargo: {cargo}")
                else:
                    print("Não há empresa associada.")
                funcionario_encontrado = True
            
            if not funcionario_encontrado:
                print("Funcionario não encontrado.")

    def atualizar_funcionario(self, nome, novo_nome="", nova_idade="", novo_email="", novo_telefone="", novo_cargo=""):
        with self.driver.session() as session:
            if novo_nome:
                session.run("MATCH (f:Funcionario {nome: $nome}) SET f.nome = $novo_nome", nome=nome, novo_nome=novo_nome)
            if nova_idade:
                session.run("MATCH (f:Funcionario {nome: $nome}) SET f.idade = $nova_idade", nome=nome, nova_idade=nova_idade)
            if novo_email:
                session.run("MATCH (f:Funcionario {nome: $nome}) SET f.email = $novo_email", nome=nome, novo_email=novo_email)
            if novo_telefone:
                session.run("MATCH (f:Funcionario {nome: $nome}) SET f.telefone = $novo_telefone", nome=nome, novo_telefone=novo_telefone)
            if novo_cargo:
                session.run("""
                    MATCH (f:Funcionario {nome: $nome})-[r:TRABALHA_EM]->(e:Empresa)
                    SET r.cargo = $novo_cargo
                """, nome=nome, novo_cargo=novo_cargo)

            print(f"Dados do funcionário {nome} atualizados.")

    def deletar_funcionario(self, nome):
        with self.driver.session() as session:
            session.run("MATCH (f:Funcionario {nome: $nome}) DETACH DELETE f", nome=nome)
            print(f"Funcionario {nome} deletado.")

    def buscar_empresa(self, nome):
        with self.driver.session() as session:
            resultado = session.run("MATCH (e:Empresa {nome: $nome}) RETURN e", nome=nome)
            empresa_encontrada = False
            for registro in resultado:
                empresa = registro["e"]
                print(f"\nEmpresa: {empresa['nome']}\nSetor: {empresa['setor']}")
                empresa_encontrada = True
            
            if not empresa_encontrada:
                print("Empresa não encontrada.")

    def atualizar_empresa(self, nome, novo_setor):
        with self.driver.session() as session:
            session.run("MATCH (e:Empresa {nome: $nome}) SET e.setor = $novo_setor", nome=nome, novo_setor=novo_setor)
            print(f"Empresa {nome} atualizada para setor {novo_setor}.")

    def deletar_empresa(self, nome):
        with self.driver.session() as session:
            session.run("MATCH (e:Empresa {nome: $nome}) DETACH DELETE e", nome=nome)
            print(f"Empresa {nome} deletada.")

    def obter_grafo(self):
        with self.driver.session() as session:
            resultado = session.run("MATCH (f:Funcionario)-[r:TRABALHA_EM]->(e:Empresa) RETURN f, e, r.cargo AS cargo")
            grafo = nx.Graph()
            for registro in resultado:
                funcionario = registro["f"]
                empresa = registro["e"]
                cargo = registro["cargo"]
                grafo.add_node(funcionario["nome"], type="Funcionario")
                grafo.add_node(empresa["nome"], type="Empresa")
                grafo.add_edge(funcionario["nome"], empresa["nome"], cargo=cargo)
            return grafo

def visualizar_grafo(grafo):
    pos = nx.spring_layout(grafo)
    plt.figure(figsize=(10, 6))
    nx.draw(grafo, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_color='black')
    edge_labels = nx.get_edge_attributes(grafo, 'cargo')
    nx.draw_networkx_edge_labels(grafo, pos, edge_labels=edge_labels)
    plt.title("Grafo de Funcionários e Empresas")
    plt.show()

def submenu_crud(opcao, crud):
    if opcao == "1":
        tipo = input('''\nCriar: 
1. Funcionario 
2. Empresa
Escolha: ''')
        if tipo == "1":
            nome = input("Nome do Funcionario: ")
            idade = input("Idade do Funcionario: ")
            email = input("Email do Funcionario: ")
            telefone = input("Telefone do Funcionario: ")
            nome_empresa = input("Nome da Empresa: ")
            cargo = input("Cargo do Funcionario: ")
            setor = input("Setor da Empresa: ")
            crud.criar_funcionario(nome, idade, email, telefone, nome_empresa, cargo, setor)
        elif tipo == "2":
            nome = input("Nome da Empresa: ")
            setor = input("Setor da Empresa: ")
            crud.atualizar_empresa(nome, setor)

    elif opcao == "2":
        tipo = input('''\nBuscar: 
1. Funcionario 
2. Empresa
Escolha: ''')
        if tipo == "1":
            nome = input("Nome do Funcionario: ")
            crud.buscar_funcionario(nome)
        elif tipo == "2":
            nome = input("Nome da Empresa: ")
            crud.buscar_empresa(nome)

    elif opcao == "3":
        tipo = input('''\nAtualizar: 
1. Funcionario 
2. Empresa
Escolha: ''')
        if tipo == "1":
            nome = input("Nome do Funcionario a ser atualizado: ")
            novo_nome = input("Novo Nome do Funcionario (deixe em branco para não alterar): ")
            nova_idade = input("Nova Idade do Funcionario (deixe em branco para não alterar): ")
            novo_email = input("Novo Email do Funcionario (deixe em branco para não alterar): ")
            novo_telefone = input("Novo Telefone do Funcionario (deixe em branco para não alterar): ")
            novo_cargo = input("Novo Cargo do Funcionario (deixe em branco para não alterar): ")
            crud.atualizar_funcionario(nome, novo_nome, nova_idade, novo_email, novo_telefone, novo_cargo)

        elif tipo == "2":
            nome = input("Nome da Empresa: ")
            novo_setor = input("Novo Setor da Empresa: ")
            crud.atualizar_empresa(nome, novo_setor)

    elif opcao == "4":
        tipo = input('''\nDeletar: 
1. Funcionario 
2. Empresa
Escolha: ''')
        if tipo == "1":
            nome = input("Nome do Funcionario: ")
            crud.deletar_funcionario(nome)
        elif tipo == "2":
            nome = input("Nome da Empresa: ")
            crud.deletar_empresa(nome)

def main():
    crud = Neo4jCRUD("bolt://localhost:7687", "neo4j", "Senha2024")

    while True:
        print("\nMenu Principal")
        print("1. Criar Funcionario ou Empresa")
        print("2. Buscar Funcionario ou Empresa")
        print("3. Atualizar Funcionario ou Empresa")
        print("4. Deletar Funcionario ou Empresa")
        print("5. Visualizar o grafo dos relacionamentos")
        print("0. Sair")

        escolha = input("Escolha uma opção: ")
        if escolha == "0":
            print("Saindo...")
            break
        elif escolha in ["1", "2", "3", "4"]:
            submenu_crud(escolha, crud)
        elif escolha == "5":
            grafo = crud.obter_grafo()
            visualizar_grafo(grafo)
        else:
            print("Opção inválida.")

    crud.fechar_conexao()

if __name__ == "__main__":
    main()