import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw
import os
import hashlib

# Função para gerar o gráfico
def gerar_grafico(df, colors):
    st.write("Gerando gráfico...")
    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(df['data'], df['hectares'], color=colors, alpha=0.6)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom')

    ax.set_ylabel('Hectares')
    ax.set_xlabel('Data')
    ax.set_title('Quantidade de Hectares Aplicada Diariamente')
    fig.autofmt_xdate()

    return fig

# Função para adicionar logomarca ao gráfico
def adicionar_logomarca(fig, logo_path):
    st.write("Adicionando logomarca ao gráfico...")
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
    st.write("Salvando gráfico...")
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

# Função para gerar um hash de senha
def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para verificar se o hash da senha fornecida corresponde ao hash armazenado
def verificar_senha(senha, hash_senha):
    return gerar_hash_senha(senha) == hash_senha

# Função principal do aplicativo
def main():
    st.set_page_config(page_title="PILOTOS DS DRONES", page_icon=":helicopter:", layout="wide")
    st.title('PILOTOS DS DRONES')
    st.write("Iniciando aplicação...")

    # Adicionar o logotipo da empresa na barra lateral
    logo_path = "logo.png"  # Caminho relativo do logotipo
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
        st.write("Logotipo carregado.")
    else:
        st.sidebar.write("Logotipo não encontrado. Verifique o caminho do arquivo.")
        st.write("Logotipo não encontrado.")

    # Inicializar a lista de pilotos e cores no session_state
    if 'pilotos' not in st.session_state:
        st.session_state['pilotos'] = {}
        st.write("Inicializando lista de pilotos.")
    if 'cores' not in st.session_state:
        st.session_state['cores'] = {}
        st.write("Inicializando lista de cores.")
    if 'tokens' not in st.session_state:
        st.session_state['tokens'] = {}
        st.write("Inicializando lista de tokens.")
    if 'usuarios' not in st.session_state:
        st.session_state['usuarios'] = {
            'admin': {
                'senha': gerar_hash_senha('admin123'),
                'tipo': 'Administrador'
            }
        }
        st.write("Inicializando lista de usuários com administrador padrão.")

    # Página de login
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username in st.session_state['usuarios']:
            stored_password_hash = st.session_state['usuarios'][username]['senha']
            if verificar_senha(password, stored_password_hash):
                st.session_state['usuario_logado'] = username
                st.session_state['painel'] = st.session_state['usuarios'][username]['tipo']
                st.sidebar.success(f"Bem-vindo, {username}!")
            else:
                st.sidebar.error("Senha incorreta")
        else:
            st.sidebar.error("Usuário não encontrado")

    # Cadastro de novos pilotos pelo administrador
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Administrador":
        st.sidebar.title("Cadastrar Novo Piloto")
        new_pilot_username = st.sidebar.text_input("Nome do Novo Piloto")
        new_pilot_password = st.sidebar.text_input("Senha do Novo Piloto", type="password")
        register_pilot_button = st.sidebar.button("Cadastrar Piloto")

        if register_pilot_button:
            if new_pilot_username and new_pilot_password:
                if new_pilot_username not in st.session_state['usuarios']:
                    st.session_state['usuarios'][new_pilot_username] = {
                        'senha': gerar_hash_senha(new_pilot_password),
                        'tipo': 'Piloto'
                    }
                    st.session_state['pilotos'][new_pilot_username] = []
                    st.sidebar.success(f"Piloto {new_pilot_username} cadastrado com sucesso!")
                else:
                    st.sidebar.error("Piloto já existe")
            else:
                st.sidebar.error("Por favor, insira um nome de usuário e uma senha")

    # Painel do Administrador
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Administrador":
        st.title("Painel do Administrador")

        # Mostrar gráfico agregando dados de todos os pilotos
        st.title('Dados de Todos os Pilotos')
        
        if st.session_state['pilotos']:
            df_total = pd.DataFrame()
            for piloto, dados in st.session_state['pilotos'].items():
                df_piloto = pd.DataFrame(dados)
                df_piloto['piloto'] = piloto
                df_total = pd.concat([df_total, df_piloto])

            if not df_total.empty:
                st.write("Dados agregados dos pilotos:")
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

    # Painel do Piloto
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Piloto":
        st.sidebar.title('Painel do Piloto')
        st.sidebar.success(f'Logado como {st.session_state["usuario_logado"]}')
        st.write(f'Piloto atual: {st.session_state["usuario_logado"]}')

        # Entrada de Hectares
        st.sidebar.subheader('Entrada de Hectares')
        data = st.sidebar.date_input('Data')
        hectares = st.sidebar.number_input('Hectares', min_value=0.0, format="%.2f")
        
        if st.sidebar.button('Adicionar Hectares'):
            piloto_atual = st.session_state["usuario_logado"]
            if piloto_atual:
                st.session_state['pilotos'][piloto_atual].append({'data': data, 'hectares': hectares})
                st.sidebar.success(f'{hectares} hectares adicionados para {piloto_atual} em {data}')
                st.write(f'{hectares} hectares adicionados para {piloto_atual} em {data}')
            else:
                st.sidebar.error('Erro ao identificar o piloto.')

        # Mostrar os dados do piloto atual
        st.title(f'Dados do Piloto: {st.session_state["usuario_logado"]}')
        dados_piloto = st.session_state['pilotos'].get(st.session_state["usuario_logado"], [])

        if dados_piloto:
            df_piloto = pd.DataFrame(dados_piloto)
            st.write(df_piloto)

            fig = gerar_grafico(df_piloto, 'skyblue')
            st.pyplot(fig)

            # Adicionar logomarca ao gráfico
            if os.path.exists(logo_path):
                buf_final = adicionar_logomarca(fig, logo_path)
                st.image(buf_final)

            # Botão para baixar o gráfico
            if os.path.exists(logo_path):
                st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico_com_logomarca.png", mime="image/png")
            else:
                buf = salvar_grafico(fig)
                st.download_button(label="Baixar Gráfico", data=buf, file_name="grafico.png", mime="image/png")
        else:
            st.write("Nenhum dado disponível para este piloto.")

if __name__ == "__main__":
    main()
