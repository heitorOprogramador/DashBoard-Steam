import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

df = pd.read_csv("steam-200k_1.csv", sep=",", header=None)
df = df.iloc[:, :-1]
df.columns = ['user_id', 'game_name', 'component_name', 'value']
df_play = df[df['component_name'] == 'play']
df_purchase = df[df['component_name'] == 'purchase']

#Total dos quatro dados
total_compras = df_purchase.shape[0]
total_horas = df[df['component_name'] == 'play']['value'].sum()
total_usuarios = df['user_id'].nunique()
total_jogos = df['game_name'].nunique()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🛒 Total de Compras", value=f"{total_compras:,}")
with col2:
    st.metric(label="⏱️ Total de Horas Jogadas", value=f"{total_horas:,}")
with col3:
    st.metric(label="👥 Usuários Únicos", value=f"{total_usuarios:,}")
with col4:
    st.metric(label="🎮 Jogos Diferentes", value=f"{total_jogos:,}")
with st.expander("📊 O que significam esses totais?"):
        st.markdown("""
        Estes quatro indicadores fornecem uma **visão geral rápida e essencial** sobre os dados analisados:

        - **🛒 Total de Compras**:  
        Conta quantas vezes um jogo foi comprado no total, considerando todas as compras feitas por todos os usuários.  
        > Por exemplo, se um jogo foi comprado por 20 pessoas diferentes, ele soma 20 aqui.
                    
        - **🕒 Total de Horas Jogadas**:  
        Soma de todas as horas de jogo registradas no sistema. Mostra o **nível de engajamento total** dos usuários com os jogos adquiridos.
                    
        - **👥 Usuários Únicos**:  
        Representa a quantidade de diferentes usuários presentes no sistema. Cada usuário pode ter comprado ou jogado vários jogos, mas é contado apenas uma vez aqui.

        - **🎮 Jogos Diferentes**:  
        Indica quantos jogos únicos aparecem nos registros de compras e tempo de jogo. É útil para entender a **variedade** de títulos envolvidos.

        Esses números são úteis para capturar a **dimensão e o comportamento geral** dos dados de forma direta e visual. Eles ajudam a perceber, logo de início, o **volume da atividade** dentro da plataforma.
""")


#Agrupamento dos mais jogados e comprados - Coluna horizontal
jogos_mais_jogados = df_play.groupby('game_name')['value'].sum().sort_values(ascending=False).head(10)
jogos_mais_jogados_df = jogos_mais_jogados.reset_index()
jogos_mais_jogados_df.columns = ['Jogo', 'Horas']
jogos_mais_comprados = df_purchase['game_name'].value_counts().head(10)
jogos_mais_comprados_df = jogos_mais_comprados.reset_index()
jogos_mais_comprados_df.columns = ['Jogo', 'Compra']

fig_jogados = px.bar(
    jogos_mais_jogados_df,
    x='Horas',
    y='Jogo',
    orientation='h',
    color=jogos_mais_jogados.values,
    color_continuous_scale='greens',
    labels={'Horas': 'Horas Jogadas', 'Jogo': 'Jogos'},
    title='🎮 Top 10 Jogos Mais Jogados'
)
fig_jogados.update_layout(yaxis=dict(autorange="reversed"))

fig_comprados = px.bar(
    jogos_mais_comprados_df,
    x='Compra',
    y='Jogo',
    orientation='h',
    color=jogos_mais_comprados.values,
    color_continuous_scale='blues',
    labels={'Compra': 'Números de Compras', 'Jogo': 'Jogos'},
    title='🛒 Top 10 Jogos Mais Comprados'
)
fig_comprados.update_layout(yaxis=dict(autorange="reversed"))

c1, c2= st.columns(2)

with c1:
    st.plotly_chart(fig_jogados, use_container_width=True)
    with st.expander("ℹ️ Entenda este gráfico"):
        st.markdown("""
        Este gráfico mostra os **10 jogos mais jogados** com base no total de horas registradas por todos os usuários.

        - Jogos com maior tempo de gameplay ou multiplayer tendem a aparecer aqui.
        - Os dados refletem **tempo somado**, não tempo médio por usuário.
        - Ideal para identificar títulos com maior **engajamento**.

        > Passe o mouse sobre as barras para ver os valores exatos.
""")
with c2:
    st.plotly_chart(fig_comprados, use_container_width=True)
    with st.expander("ℹ️ Entenda este gráfico"):
        st.markdown("""
        Aqui estão os **10 jogos mais comprados** pelos usuários.

        - O número representa a **quantidade de vezes que o jogo foi adquirido**.
        - Jogos populares, gratuitos ou em promoção podem aparecer em destaque.
        - Excelente para entender a **popularidade comercial**.

        > Passe o mouse sobre as barras para ver os valores exatos.
""")


#Distribuição de tempo de jogo
df_jogos = df_play[['user_id', 'game_name', 'value']].rename(columns={
    'user_id': 'Usuário',
    'game_name': 'Jogo',
    'value': 'Horas Jogadas'
})
#Filtragem por nome de jogo
jogos_disponiveis = sorted(df_jogos['Jogo'].unique())
jogos_selecionado = st.selectbox("🎮 Selecione um jogo para ver os jogadores:", options=jogos_disponiveis)
#Exibição de dados filtrados
df_filtrado= df_jogos[df_jogos['Jogo'] == jogos_selecionado].sort_values(by='Horas Jogadas', ascending=False)

st.markdown(f"### ⏱️ Distribuição de Horas Jogadas no jogo **{jogos_selecionado}**")
st.dataframe(df_filtrado, use_container_width=True)


#Top 10 usuarios ativos - Pizza
top_users = df_play.groupby('user_id')['value'].sum().sort_values(ascending=False).head(10)
top_users_df = top_users.reset_index()
top_users_df.columns = ['Id_usuário', 'Horas_ativo']

fig_pizza = px.pie(
    top_users_df,
    names='Id_usuário',
    values='Horas_ativo',
    title='🔥 Top 10 Usuários Mais Ativos (Horas Jogadas)',
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.RdBu,
    labels={'Id_usuário': 'ID de Usuário', 'Horas_ativo': 'Horas Ativo'}
)


#Relação Compra e tempo - Dispersão
compras_por_usuario = df_purchase.groupby('user_id').size()
tempo_por_usuario = df_play.groupby('user_id')['value'].sum()
#Juntando os dois
df_relacao = pd.DataFrame({
    'Horas Jogadas': tempo_por_usuario,
    'Compras': compras_por_usuario
}).fillna(0)

fig_scatter = px.scatter(
    df_relacao,
    x='Compras',
    y='Horas Jogadas',
    title='🧩 Relação entre Compras e Tempo de Jogo',
    labels={'Compras': 'Total de Compras', 'Horas Jogadas': 'Horas Jogadas'},
    color='Horas Jogadas',
    size='Horas Jogadas',
    color_continuous_scale='viridis'
)

co1, co2= st.columns(2)

with co1:
    st.plotly_chart(fig_pizza, use_container_width=True)
    with st.expander("👤 Quem são os usuários mais ativos?"):
        st.markdown("""
        Este gráfico de pizza mostra os **10 usuários que mais acumularam horas de jogo** no sistema.

        - Cada fatia representa um usuário.
        - O tamanho da fatia indica a **quantidade total de horas jogadas** por aquele usuário.
        - As cores ajudam a diferenciar visualmente cada jogador.

        Este gráfico é uma ótima maneira de identificar quem são os **jogadores mais engajados** da plataforma.  
        Quanto maior a fatia, mais tempo o usuário passou jogando, o que pode indicar grande interesse, lealdade à plataforma ou preferência por jogos longos.
        
        > Passe o mouse sobre as barras para ver os valores exatos.
""")
with co2:
    st.plotly_chart(fig_scatter, use_container_width=True)
    with st.expander("📉 Como compras se relacionam com tempo de jogo?"):
        st.markdown("""
        Este gráfico de dispersão mostra a **relação entre o número de compras e o tempo total de jogo para cada usuário**.

        - Cada ponto representa um usuário.
        - O eixo **X** mostra quantas compras o usuário fez.
        - O eixo **Y** mostra o total de horas jogadas por aquele usuário.

        Com isso, é possível observar diferentes **perfis de comportamento**:
        - Usuários que compram muito e jogam muito 🧠🎮
        - Usuários que compram pouco, mas jogam muito 🎯
        - Usuários que compram muito e jogam pouco 😅

        Esse tipo de visualização ajuda a entender **padrões de uso da plataforma**, e pode ser útil para direcionar estratégias de marketing, fidelização ou recomendações personalizadas.
        
        > Passe o mouse sobre as barras para ver os valores exatos.
""")


#Estatisticas por usuario
st.sidebar.markdown("## 📊 Estatística do Usuário")
usuarios_disponiveis = df_play['user_id'].unique()
usuarios_selecionado = st.sidebar.selectbox("Selecione um usuário:", options=sorted(usuarios_disponiveis))

df_usuario = df_play[df_play['user_id'] == usuarios_selecionado]
df_jogos_usuario = df_usuario.groupby('game_name')['value'].sum().reset_index()
df_jogos_usuario = df_jogos_usuario.rename(columns={
    'game_name': 'Jogo',
    'value': 'Horas Jogadas'
}).sort_values(by='Horas Jogadas', ascending=False)

st.sidebar.markdown(f"### 🧑 Usuário: {usuarios_selecionado}")
st.sidebar.markdown(f"Jogos jogados: {len(df_jogos_usuario)}")
st.sidebar.markdown("### 🎮 Tempo de Jogo por Jogo:")
st.sidebar.dataframe(df_jogos_usuario, use_container_width=True)


#Easter Eggs
if st.button("⚙️"):
    st.balloons()  # Animação divertida
    st.success("Parabéns! Você encontrou o Easter Egg! 🎉")
    st.markdown("""
    Você claramente é uma pessoa curiosa — e curiosidade é essencial para explorar dados!  
    Já que está aqui, sabia que o primeiro jogo da Steam foi o **Counter-Strike: Condition Zero**, lançado em 2004?

    E aí vai um bônus inútil (ou não):  
    > "Jogadores que jogam de madrugada têm 80% mais chance de esquecer que tinham compromissos pela manhã." 😴

    Continue explorando o dashboard... quem sabe há mais segredos por aqui? 👀
    """)
