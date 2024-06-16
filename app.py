import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw
import os

# Função para gerar o gráfico
def gerar_grafico(df, colors):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 16), sharex=True)

    # Subplot para Total de Hectares
    bars1 = ax1.bar(df['piloto'], df['hectares'], color=colors, alpha=0.6, width=0.4)
    for i, piloto in enumerate(df['piloto']):
        ax1.plot(piloto, df['hectares'][i], color=colors[i], marker='o', linestyle='-', label=f'{piloto}')
        ax1.annotate(f'{df["hectares"][i]:.2f}', (piloto, df['hectares'][i]), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[i])
    ax1.set_ylabel('Total de Hectares')
    ax1.legend(loc='upper left', frameon=False, facecolor='none')
    ax1.set_title('Total de Hectares', pad=20)

    # Subplot para Duração da Safra
    bars2 = ax2.bar(df['piloto'], df['duracao_safra'], color=colors, alpha=0.6, width=0.4)
    for i, piloto in enumerate(df['piloto']):
        ax2.plot(piloto, df['duracao_safra'][i], color=colors[i], marker='o', linestyle='--', label=f'{piloto}')
        ax2.annotate(f'{df["duracao_safra"][i]}', (piloto, df['duracao_safra'][i]), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[i])
    ax2.set_ylabel('Duração da Safra (dias)')
    ax2.set_title('Duração da Safra (dias)', pad=20)

    # Subplot para Média de Hectares por Dia
    bars3 = ax3.bar(df['piloto'], df['media_hectares_dia'], color=colors, alpha=0.6, width=0.4)
    for i, piloto in enumerate(df['piloto']):
        ax3.plot(piloto, df['media_hectares_dia'][i], color=colors[i], marker='x', linestyle='-', label=f'{piloto}')
        ax3.annotate(f'{df["media_hectares_dia"][i]}', (piloto, df['media_hectares_dia'][i]), textcoords="offset points", xytext=(0, 10), ha='center', color=colors[i])
    ax3.set_xlabel('Piloto')
    ax3.set_ylabel('Média de Hectares por Dia')
    ax3.set_title('Média de Hectares por Dia', pad=20)

    fig.tight_layout(pad=3.0)

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
    st.set_page_config(page_title="GERENCIAMENTO DE PILOTOS DS DRONES", page_icon=":helicopter:", layout="wide")
    st.title('GERENCIAMENTO DE PILOTOS DS DRONES')

    # Adicionar o logotipo da empresa na barra lateral
    logo_path = "logo.png"  # Caminho relativo do logotipo
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
    else:
        st.sidebar.write("Logotipo não encontrado. Verifique o caminho do arquivo.")

    # Inicializar a lista de pilotos e cores no session_state
    if 'pilotos' not in st.session_state:
        st.session_state['pilotos'] = []
    if 'cores' not in st.session_state:
        st.session_state['cores'] = []

    st.sidebar.title('Adicionar Novo Piloto')
    piloto = st.sidebar.text_input('Nome do Piloto')
    inicio_safra = st.sidebar.date_input('Início da Safra')
    fim_safra = st.sidebar.date_input('Fim da Safra')
    hectares = st.sidebar.number_input('Total de Hectares', min_value=0.0, format='%f')

    if st.sidebar.button('Adicionar Piloto'):
        if piloto and inicio_safra and fim_safra and hectares:
            novo_piloto = {
                'piloto': piloto,
                'inicio_safra': inicio_safra.strftime('%d/%m/%Y'),
                'fim_safra': fim_safra.strftime('%d/%m/%Y'),
                'hectares': hectares
            }
            st.session_state['pilotos'].append(novo_piloto)
            st.session_state['cores'].append('#1f77b4')  # Cor padrão azul
            st.sidebar.success('Piloto adicionado com sucesso!')
        else:
            st.sidebar.error('Por favor, preencha todos os campos.')

    st.sidebar.title('Remover Piloto')
    if st.session_state['pilotos']:
        piloto_remover = st.sidebar.selectbox('Selecione o Piloto', [p['piloto'] for p in st.session_state['pilotos']])
        if st.sidebar.button('Remover Piloto'):
            index = next(i for i, p in enumerate(st.session_state['pilotos']) if p['piloto'] == piloto_remover)
            del st.session_state['pilotos'][index]
            del st.session_state['cores'][index]
            st.sidebar.success('Piloto removido com sucesso!')

    st.sidebar.title('Modificar Cor dos Pilotos')
    for i, p in enumerate(st.session_state['pilotos']):
        nova_cor = st.sidebar.color_picker(f'Cor do {p["piloto"]}', st.session_state['cores'][i])
        st.session_state['cores'][i] = nova_cor

    if st.session_state['pilotos']:
        df = pd.DataFrame(st.session_state['pilotos'])
        df['inicio_safra'] = pd.to_datetime(df['inicio_safra'], format='%d/%m/%Y')
        df['fim_safra'] = pd.to_datetime(df['fim_safra'], format='%d/%m/%Y')
        df['duracao_safra'] = (df['fim_safra'] - df['inicio_safra']).dt.days
        df['media_hectares_dia'] = df['hectares'] / df['duracao_safra']
        df['media_hectares_dia'] = df['media_hectares_dia'].round(2)

        st.write(df)

        fig = gerar_grafico(df, st.session_state['cores'])

        # Adicionar logomarca ao gráfico
        if os.path.exists(logo_path):
            buf_final = adicionar_logomarca(fig, logo_path)
            st.image(buf_final)
        else:
            st.pyplot(fig)

        # Botão para baixar o gráfico
        if os.path.exists(logo_path):
            st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico
