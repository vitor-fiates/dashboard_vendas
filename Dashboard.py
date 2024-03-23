import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Para ativar o ambiente virtual executar comando abaixo no terminal
# .\venv\Scripts/activate 
# Para rodar o aplicativo deve-se executar o comando abaixo no terminal
# streamlit run Dashboard.py

# Setar como layout padrão do streamlit o formato wide
st.set_page_config(layout = 'wide')

# Decalararr a função para formatar números
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Título do Aplicativo
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Importação dos dados
url = 'https://labdados.com/produtos'

# Vamos criar uma lista para implementar um filtro na url da api
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sul']

## Filtros
# Criando uma barra lateral para alocação dos filtros
st.sidebar.title('Filtros')

#Filtro por região
regiao = st.sidebar.selectbox('Regiao', regioes)
# Se a regiao for igual a Brasil não será aplicado o filtro na url da api
if  regiao == 'Brasil':
    regiao = ''

# Filtro por anos
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

# Criando um dicipnário com os parâmetros que serão aplicados ao filtro
query_string = {'regiao':regiao.lower(), 'ano':ano}
# Aplicando o filtro na url
response = requests.get(url, params = query_string)

# Conversão dos dados json da resposta da api em um dataframe
dados = pd.DataFrame.from_dict(response.json())

# Conversão o formato da coluna de data para datetime
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas de receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values(by = 'Preço', ascending = False)

# Agrupando os valores de preço por mês 
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
# Criando uma nova coluna com a informação do ano
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
# Criando uma nova coluna com a informação do mês
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Criando uma tabela com a receita por categoria de produto
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values(by = 'Preço', ascending = False)

## Tabelas de quantidade de vendas
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

## Tabelas vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


### Gráficos de Receita
# Criando um gráfico de mapa com dispersão
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por estado')


# Criando um gráfico de linhas com a receita mensal
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')
# Alterando o título do eixo Y de preço para receita
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# Construindo um gráfico de barras de receita por estado
fig_receita_estados = px.bar(receita_estados.head(5),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title= 'Top estados (receita)')
# Alterando o título do eixo Y de preço para receita
fig_receita_estados.update_layout(yaxis_title = 'Receita')

# Construindo um grafico de barras de receita por categoria de produto
# para esse gráfico não será necessário passar o x e o y, pois a tabela tem somente duas colunas a categoria e a receita
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria')
# Alterando o título do eixo Y de preço para receita
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

### Gráficos de Vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')
fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)
fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

## Visualização no streamlit
# Criar abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

# Aba 1
with aba1:
    # Criar colunas para colocar as métricas dentro das colunas
    coluna1, coluna2 = st.columns(2)
    # Adicionando métricas ao dashboard
    with coluna1:
        # A receita é igual a soma de todos os elementos da coluna Preço
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))    
        # Adicionando o gráfico a coluna 1
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        # Adicionando o gráfico de barras de receita por estado
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        # Quantidade de vendas é igual ao número de linhas do dataframe
        # o atributo shape fornce o número de linhas e colunas do dataframe
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        # Adicionando o gráfico de linhas
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        # Adicionando o gráfio de receita por categoria
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

# Aba2
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)        

# Aba 3
with aba3:
    # Criando um input para o usuário informar o número de vendedores (valor mín 2, valor máximo 10, valor padrão 5)
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    # Criar colunas para colocar as métricas dentro das colunas
    coluna1, coluna2 = st.columns(2)
    # Adicionando métricas ao dashboard
    with coluna1:
        # A receita é igual a soma de todos os elementos da coluna Preço
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))    
        # Construindo um gráfico de barras para mostrar o total de receita por vendedor
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values(by = 'sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values(by = 'sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        # Quantidade de vendas é igual ao número de linhas do dataframe
        # o atributo shape fornce o número de linhas e colunas do dataframe
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        # Construindo um gráfico de barras para mostrar o total de vendas por vendedor
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values(by = 'count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values(by = 'count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores) 

# Exibir o dataframe no aplicativo
#st.dataframe(dados)