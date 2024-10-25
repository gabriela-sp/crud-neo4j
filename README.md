# Neo4j CRUD - Gerenciamento de Funcionários e Empresas

Este projeto implementa um sistema CRUD em Python para gerenciar funcionários e empresas, utilizando o banco de dados Neo4j. Além de permitir operações básicas de criação, leitura, atualização e exclusão (CRUD), o sistema visualiza as relações entre funcionários e empresas como um grafo.

## Funcionalidades

1. **CRUD para Funcionários e Empresas**:
   - **Criação**: Cria novos funcionários e empresas.
   - **Leitura**: Busca e exibe detalhes dos funcionários e empresas.
   - **Atualização**: Permite a atualização de dados de funcionários e empresas.
   - **Exclusão**: Exclui funcionários e empresas do banco de dados.

2. **Visualização de Grafos**:
   - Exibe a rede de funcionários e empresas, com a relação de cargo entre eles, utilizando NetworkX e Matplotlib.

## Tecnologias Utilizadas

- **Python 3**
- **Neo4j** (driver `neo4j` para Python)
- **NetworkX** e **Matplotlib** para visualização de grafos

## Pré-requisitos

1. **Neo4j**: Certifique-se de que o Neo4j está instalado e rodando localmente.
2. **Dependências Python**: Instale as bibliotecas necessárias executando:
   ```bash
   pip install neo4j networkx matplotlib

## Configuração do Banco de Dados

Configure as credenciais de autenticação no código:

```python
crud = Neo4jCRUD("bolt://localhost:7687", "neo4j", "Senha2024")
