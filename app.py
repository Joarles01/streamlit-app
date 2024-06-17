import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw
import os
import hashlib

# Função para gerar o gráfico
def gerar_grafico(df, colors):
    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(df['data'], df['hectares'], color=colors, alpha=0.6)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')
    
    ax.set_ylabel('Hectares')
    ax.set_xlabel('Data')
    ax.set_title('Quantidade de Hectares Aplicada Diariamente')
    fig.autofmt_xdate()
    
    return fig

# Função para adicionar logomarca ao gráfico
def adicionar_logomarca(fig, logo_path):
    # Salvar o gráfico em um objeto BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Abrir a imagem do gráfico com o Pillow
    imagem_grafico = Image.open(buf)

    # Abrir a logomarca
    logomarca = Image.open(logo_path).convert("RGBA")

    # Redimensionar a logomarca
    largura_logo, altura_logo = logomarca.size
    largura_nova = 100  # ajuste a largura desejada
    altura_nova = int((altura_logo / largura_logo) * largura_nova)
    logomarca = logomarca.resize((largura_nova, altura_nova), Image.LANCZOS)

    # Posicionar a logomarca na imagem do gráfico
    posicao_logo = (imagem_grafico.width - largura_nova - 10, imagem_grafico.height - altura_nova - 10)
    imagem_grafico.paste(logomarca, posicao_logo, logomarca)

    # Salvar a imagem combinada em um objeto BytesIO
    buf_final = BytesIO()
    imagem_grafico.save(buf_final, format='png')
    buf_final.seek(0)

    return buf_final

# Função para salvar o gráfico
def salvar_grafico(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

# Função para gerar um token simples
def gerar_token(piloto_nome):
    return hashlib.sha256(piloto_nome.encode()).hexdigest()

# Função principal do aplicativo
def main():
    st.set_page_config(page_title="PILOTOS DS DRONES", page_icon="drone_icon.png", layout="wide")
    st.title('PILOTOS DS DRONES')

    # Adicionar o logotipo da empresa na barra lateral
    logo_path = "logo.png"  # Caminho relativo do logotipo
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
    else:
        st.sidebar.write("Logotipo não encontrado. Verifique o caminho do arquivo.")

    # Inicializar a lista de pilotos e cores no session_state
    if 'pilotos' not in st.session_state:
        st.session_state['pilotos'] = {}
    if 'cores' not in st.session_state:
        st.session_state['cores'] = {}
    if 'tokens' not in st.session_state:
        st.session_state['tokens'] = {}

    # Identificar se é administrador ou piloto baseado no URL
    query_params = st.experimental_get_query_params()
    token = query_params.get("token", [None])[0]

    if token is None:
        st.sidebar.title('Login de Administrador')
        admin_password = st.sidebar.text_input("Senha do Administrador", type="password")
        
        if admin_password == "admin123":  # Senha fixa para demonstração
            st.sidebar.success("Login de Administrador bem-sucedido")
            painel = "Administrador"
        else:
            st.sidebar.error("Senha incorreta")
            return
    else:
        painel = "Piloto"
        piloto_atual = next((piloto for piloto, t in st.session_state['tokens'].items() if t == token), None)
        if piloto_atual is None:
            st.error("Token inválido")
            return

    if painel == "Administrador":
        st.sidebar.title('Painel do Administrador')

        # Adicionar piloto
        st.sidebar.subheader('Adicionar Piloto')
        novo_piloto = st.sidebar.text_input('Nome do Novo Piloto')
        if st.sidebar.button('Adicionar Piloto'):
            if novo_piloto:
                if novo_piloto not in st.session_state['pilotos']:
                    st.session_state['pilotos'][novo_piloto] = []
                    token = gerar_token(novo_piloto)
                    st.session_state['tokens'][novo_piloto] = token
                    link = f"{st.experimental_get_query_params().get('base', [''])[0]}?token={token}"
                    st.sidebar.success(f'Piloto {novo_piloto} cadastrado com sucesso!')
                    st.sidebar.write(f"Link para {novo_piloto}: {link}")
                else:
                    st.sidebar.error('Piloto já existe')
            else:
                st.sidebar.error('Por favor, insira o nome do piloto.')

        # Remover piloto
        st.sidebar.subheader('Remover Piloto')
        piloto_remover = st.sidebar.selectbox('Selecione o Piloto para Remover', list(st.session_state['pilotos'].keys()))
        if st.sidebar.button('Remover Piloto'):
            if piloto_remover in st.session_state['pilotos']:
                del st.session_state['pilotos'][piloto_remover]
                del st.session_state['tokens'][piloto_remover]
                st.sidebar.success(f'Piloto {piloto_remover} removido com sucesso!')
            else:
                st.sidebar.error('Piloto não encontrado')

        # Mostrar gráfico agregando dados de todos os pilotos
        st.title('Dados de Todos os Pilotos')
        
        if st.session_state['pilotos']:
            df_total = pd.DataFrame()
            for piloto, dados in st.session_state['pilotos'].items():
                df_piloto = pd.DataFrame(dados)
                df_piloto['piloto'] = piloto
                df_total = pd.concat([df_total, df_piloto])

            if not df_total.empty:
                st.write(df_total)

                fig, ax = plt.subplots(figsize=(14, 8))
                for piloto, group_data in df_total.groupby('piloto'):
                    ax.plot(group_data['data'], group_data['hectares'], marker='o', linestyle='-', label=piloto)
                
                ax.set_ylabel('Hectares')
                ax.set_xlabel('Data')
                ax.set_title('Quantidade de Hectares Aplicada Diariamente por Piloto')
                ax.legend()
                fig.autofmt_xdate()

                # Adicionar logomarca ao gráfico
                if os.path.exists(logo_path):
                    buf_final = adicionar_logomarca(fig, logo_path)
                    st.image(buf_final)
                else:
                    st.pyplot(fig)

                # Botão para baixar o gráfico
                if os.path.exists(logo_path):
                    st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico_com_logomarca.png", mime="image/png")
                else:
                    buf = salvar_grafico(fig)
                    st.download_button(label="Baixar Gráfico", data=buf, file_name="grafico.png", mime="image/png")

                # Mostrar estatísticas por piloto
                st.title('Estatísticas por Piloto')
                stats = df_total.groupby('piloto').agg(
                    total_hectares=pd.NamedAgg(column='hectares', aggfunc='sum'),
                    media_hectares_dia=pd.NamedAgg(column='hectares', aggfunc=lambda x: x.sum() / x.count()),
                    total_dias=pd.NamedAgg(column='data', aggfunc='count')
                ).reset_index()
                st.write(stats)
        else:
            st.write("Nenhum dado de piloto disponível.")

    elif painel == "Piloto":
        st.sidebar.title('Painel do Piloto')
        st.sidebar.success(f'Logado como {piloto_atual}')
        st.write(f'Piloto atual: {piloto_atual}')

        # Entrada de Hectares Diários
        st.title('Entrada de Hectares Diários')
        data = st.date_input('Data')
        hectares = st.number_input('Hectares', min_value=0.0, format='%f')

        if st.button('Adicionar Hectares'):
            if data and hectares:
                st.session_state['pilotos'][piloto_atual].append({'data': data, 'hectares': hectares})
                st.success('Hectares adicionados com sucesso!')
            else:
                st.error('Por favor, preencha todos os campos.')

        # Mostrar Dados e Gráfico
        st.title('Dados de Hectares')
        df = pd.DataFrame(st.session_state['pilotos'][piloto_atual])
        if not df.empty:
            st.write(df)

            fig = gerar_grafico(df, 'blue')

            # Adicionar logomarca ao gráfico
            if os.path.exists(logo_path):
                buf_final = adicionar_logomarca(fig, logo_path)
                st.image
