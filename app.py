import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Função para gerar o gráfico
def gerar_grafico(df):
    colors = ['darkcyan', 'orange', 'green', 'blue', 'darkorange', 'darkblue', 'purple']
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

# Função principal do aplicativo
def main():
    st.title('Gerenciamento de Pilotos e Safra')
    
    st.sidebar.title('Adicionar Novo Piloto')
    piloto = st.sidebar.text_input('Nome do Piloto')
    inicio_safra = st.sidebar.date_input('Início da Safra')
    fim_safra = st.sidebar.date_input('Fim da Safra')
    hectares = st.sidebar.number_input('Total de Hectares', min_value=0.0, format='%f')

    if st.sidebar.button('Adicionar Piloto'):
        if piloto and inicio_safra and fim_safra and hectares:
            novo_piloto = {
                'piloto': piloto,
                'inicio_safra': inicio_safra,
                'fim_safra': fim_safra,
                'hectares': hectares
            }
            pilotos.append(novo_piloto)
            st.sidebar.success('Piloto adicionado com sucesso!')
        else:
            st.sidebar.error('Por favor, preencha todos os campos.')

    df = pd.DataFrame(pilotos)
    df['inicio_safra'] = pd.to_datetime(df['inicio_safra'], format='%Y-%m-%d')
    df['fim_safra'] = pd.to_datetime(df['fim_safra'], format='%Y-%m-%d')
    df['duracao_safra'] = (df['fim_safra'] - df['inicio_safra']).dt.days
    df['media_hectares_dia'] = df['hectares'] / df['duracao_safra']
    df['media_hectares_dia'] = df['media_hectares_dia'].round(2)

    st.write(df)

    st.pyplot(gerar_grafico(df))

# Dados iniciais
pilotos = [
    {'piloto': 'ARIMATEIA', 'inicio_safra': '2024-02-01', 'fim_safra': '2024-05-31', 'hectares': 1430.9},
    {'piloto': 'SANIEL', 'inicio_safra': '2023-12-01', 'fim_safra': '2024-05-31', 'hectares': 4842.64},
    {'piloto': 'ALISSION', 'inicio_safra': '2023-12-01', 'fim_safra': '2024-05-31', 'hectares': 4120.94},
    {'piloto': 'NAILSON', 'inicio_safra': '2023-12-01', 'fim_safra': '2024-05-31', 'hectares': 4095.58},
    {'piloto': 'FERNANDO', 'inicio_safra': '2024-03-01', 'fim_safra': '2024-05-31', 'hectares': 3476.85},
    {'piloto': 'WELINGTON', 'inicio_safra': '2024-05-01', 'fim_safra': '2024-05-31', 'hectares': 387.5}
]

if __name__ == '__main__':
    main()
