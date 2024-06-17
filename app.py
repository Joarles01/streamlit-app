import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw
import os

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
    logomarca = logomarca.resize((largura_nova, altura_nova), Image.ANTIALIAS)

    # Posicionar a logomarca na imagem do gráfico
    posicao_logo = (imagem_grafico.width - largura_nova - 10, imagem_grafico.height - altura_nova - 10)
    imagem_grafico.paste(logomarca, posicao_logo, logomarca)

    # Salvar a imagem combinada em um objeto BytesIO
    buf_final = BytesIO()
    imagem_grafico.save(buf_final, format='png')
    buf_final.seek(0)

    return buf_final

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
        st.session_state['cores'] = []

    # Login ou Cadastro de Pilotos
    st.sidebar.title('Login/Cadastro de Piloto')
    piloto_nome = st.sidebar.text_input('Nome do Piloto')

    if st.sidebar.button('Login/Cadastrar'):
        if piloto_nome:
            if piloto_nome not in st.session_state['pilotos']:
                st.session_state['pilotos'][piloto_nome] = []
                st.session_state['cores'].append('#1f77b4')  # Cor padrão azul
                st.sidebar.success(f'Piloto {piloto_nome} cadastrado com sucesso!')
            st.session_state['piloto_atual'] = piloto_nome
            st.sidebar.success(f'Piloto {piloto_nome} logado com sucesso!')
        else:
            st.sidebar.error('Por favor, insira o nome do piloto.')

    if 'piloto_atual' in st.session_state:
        piloto_atual = st.session_state['piloto_atual']
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
                st.image(buf_final)
            else:
                st.pyplot(fig)

            # Botão para baixar o gráfico
            if os.path.exists(logo_path):
                st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico_com_logomarca.png", mime="image/png")
            else:
                buf = salvar_grafico(fig)
                st.download_button(label="Baixar Gráfico", data=buf, file_name="grafico.png", mime="image/png")

if __name__ == '__main__':
    main()
