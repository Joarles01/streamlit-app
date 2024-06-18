import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw
import os
import hashlib
import json
from zipfile import ZipFile  # Certificar que a importação está correta

# Função para carregar dados do arquivo JSON
def carregar_dados(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r') as f:
            return json.load(f)
    else:
        return {}

# Função para salvar dados no arquivo JSON
def salvar_dados(nome_arquivo, dados):
    with open(nome_arquivo, 'w') as f:
        json.dump(dados, f, indent=4)

# Função para gerar um hash de senha
def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para verificar se o hash da senha fornecida corresponde ao hash armazenado
def verificar_senha(senha, hash_senha):
    return gerar_hash_senha(senha) == hash_senha

# Função para adicionar logomarca ao gráfico
def adicionar_logomarca(fig, logo_image):
    st.write("Adicionando logomarca ao gráfico...")
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    imagem_grafico = Image.open(buf)

    largura_logo, altura_logo = logo_image.size
    largura_nova = 100
    altura_nova = int((altura_logo / largura_logo) * largura_nova)
    logo_image = logo_image.resize((largura_nova, altura_nova), Image.LANCZOS)

    posicao_logo = (imagem_grafico.width - largura_nova - 10, imagem_grafico.height - altura_nova - 10)
    imagem_grafico.paste(logo_image, posicao_logo, logo_image)

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

# Função para criar backup dos dados
def criar_backup():
    with ZipFile('backup.zip', 'w') as zipf:
        zipf.write('pilotos.json')
        zipf.write('cores.json')
        zipf.write('usuarios.json')
        zipf.write('fotos.json')
        zipf.write('safra.json')

# Função para recuperar backup dos dados
def recuperar_backup(arquivo):
    with ZipFile(arquivo, 'r') as zipf:
        zipf.extractall()

# Função principal do aplicativo
def main():
    st.set_page_config(page_title="PILOTOS DS DRONES", page_icon=":drone:", layout="wide")
    st.title('PILOTOS DS DRONES')
    st.write("Iniciando aplicação...")

    # Arquivos de dados
    arquivo_pilotos = 'pilotos.json'
    arquivo_cores = 'cores.json'
    arquivo_usuarios = 'usuarios.json'
    arquivo_fotos = 'fotos.json'
    arquivo_safra = 'safra.json'

    # Carregar dados do JSON
    pilotos = carregar_dados(arquivo_pilotos)
    cores = carregar_dados(arquivo_cores)
    usuarios = carregar_dados(arquivo_usuarios)
    fotos = carregar_dados(arquivo_fotos)
    safra = carregar_dados(arquivo_safra)

    if not usuarios:
        usuarios['admin'] = {
            'senha': gerar_hash_senha('admin123'),
            'tipo': 'Administrador'
        }

    # Adicionar o logotipo da empresa na barra lateral
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)
        st.write("Logotipo carregado.")
    else:
        st.sidebar.write("Logotipo não encontrado. Verifique o caminho do arquivo.")
        st.write("Logotipo não encontrado.")

    # Página de login
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if username in usuarios:
            stored_password_hash = usuarios[username]['senha']
            if verificar_senha(password, stored_password_hash):
                st.session_state['usuario_logado'] = username
                st.session_state['painel'] = usuarios[username]['tipo']
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
                if new_pilot_username not in usuarios:
                    usuarios[new_pilot_username] = {
                        'senha': gerar_hash_senha(new_pilot_password),
                        'tipo': 'Piloto'
                    }
                    pilotos[new_pilot_username] = []
                    cores[new_pilot_username] = '#00ff00'  # Verde
                    fotos[new_pilot_username] = None
                    salvar_dados(arquivo_usuarios, usuarios)
                    salvar_dados(arquivo_pilotos, pilotos)
                    salvar_dados(arquivo_cores, cores)
                    salvar_dados(arquivo_fotos, fotos)
                    st.sidebar.success(f"Piloto {new_pilot_username} cadastrado com sucesso!")
                else:
                    st.sidebar.error("Piloto já existe")
            else:
                st.sidebar.error("Por favor, insira um nome de usuário e uma senha")

    # Remover piloto pelo administrador
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Administrador":
        st.sidebar.title("Remover Piloto")
        remove_pilot_username = st.sidebar.selectbox("Selecione o Piloto para Remover", list(pilotos.keys()))
        remove_pilot_button = st.sidebar.button("Remover Piloto")

        if remove_pilot_button:
            if remove_pilot_username in usuarios:
                del usuarios[remove_pilot_username]
                del pilotos[remove_pilot_username]
                del cores[remove_pilot_username]
                del fotos[remove_pilot_username]
                salvar_dados(arquivo_usuarios, usuarios)
                salvar_dados(arquivo_pilotos, pilotos)
                salvar_dados(arquivo_cores, cores)
                salvar_dados(arquivo_fotos, fotos)
                st.sidebar.success(f"Piloto {remove_pilot_username} removido com sucesso!")
            else:
                st.sidebar.error("Piloto não encontrado")

    # Painel do Administrador
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Administrador":
        st.title("Painel do Administrador")

        # Modificar cores dos pilotos
        st.sidebar.title("Modificar Cores dos Pilotos")
        for piloto in pilotos:
            nova_cor = st.sidebar.color_picker(f"Cor do {piloto}", value=cores.get(piloto, '#00ff00'))
            cores[piloto] = nova_cor

        salvar_dados(arquivo_cores, cores)

        # Adicionar dados da safra
        st.sidebar.title("Adicionar Dados da Safra")
        inicio_safra = st.sidebar.date_input("Data de Início da Safra")
        fim_safra = st.sidebar.date_input("Data de Fim da Safra")
        hectares_safra = st.sidebar.number_input("Total de Hectares da Safra", min_value=0.0, format="%.2f")

        # Adicionar dados por piloto
        safra['pilotos'] = {}
        for piloto in pilotos:
            hectares = st.sidebar.number_input(f"Hectares do piloto {piloto}", min_value=0.0, format="%.2f", key=f"hectares_{piloto}")
            dias_trabalho = st.sidebar.number_input(f"Dias de trabalho do piloto {piloto}", min_value=0, format="%d", key=f"dias_{piloto}")
            safra['pilotos'][piloto] = {'hectares': hectares, 'dias': dias_trabalho}

        adicionar_safra_button = st.sidebar.button("Adicionar Dados da Safra")

        if adicionar_safra_button:
            safra['inicio'] = str(inicio_safra)
            safra['fim'] = str(fim_safra)
            safra['hectares'] = hectares_safra
            dias_safra = (fim_safra - inicio_safra).days
            media_hectares_safra = hectares_safra / dias_safra if dias_safra > 0 else 0
            safra['dias'] = dias_safra
            safra['media'] = media_hectares_safra
            salvar_dados(arquivo_safra, safra)
            st.sidebar.success("Dados da safra adicionados com sucesso!")

        # Mostrar gráfico agregando dados de todos os pilotos
        st.title('Dados de Todos os Pilotos')
        
        if pilotos:
            df_total = pd.DataFrame()
            for piloto, dados in pilotos.items():
                if dados:
                    df_piloto = pd.DataFrame(dados)
                    df_piloto['piloto'] = piloto
                    df_total = pd.concat([df_total, df_piloto])

            if not df_total.empty:
                st.write("Dados agregados dos pilotos:")
                st.write(df_total)

                fig, axs = plt.subplots(3, 1, figsize=(10, 18), sharex=True)

                # Total de hectares
                total_hectares = df_total.groupby('piloto')['hectares'].sum()
                axs[0].bar(total_hectares.index, total_hectares.values, color=[cores[piloto] for piloto in total_hectares.index])
                axs[0].set_title('Total de Hectares Aplicado')
                axs[0].set_ylabel('Total de Hectares')
                for i, v in enumerate(total_hectares.values):
                    axs[0].text(i, v, round(v, 2), ha='center', va='bottom')

                # Média de hectares por dia
                media_hectares = df_total.groupby('piloto')['hectares'].mean()
                axs[1].bar(media_hectares.index, media_hectares.values, color=[cores[piloto] for piloto in media_hectares.index])
                axs[1].set_title('Média de Hectares por Dia')
                axs[1].set_ylabel('Média de Hectares')
                for i, v in enumerate(media_hectares.values):
                    axs[1].text(i, v, round(v, 2), ha='center', va='bottom')

                # Total de dias
                total_dias = df_total.groupby('piloto')['data'].count()
                axs[2].bar(total_dias.index, total_dias.values, color=[cores[piloto] for piloto in total_dias.index])
                axs[2].set_title('Total de Dias de Aplicação')
                axs[2].set_ylabel('Total de Dias')
                for i, v in enumerate(total_dias.values):
                    axs[2].text(i, v, round(v, 2), ha='center', va='bottom')

                for ax in axs:
                    ax.set_xlabel('Pilotos')
                    ax.set_xticks(range(len(total_hectares.index)))
                    ax.set_xticklabels(total_hectares.index, rotation=45, ha='right')

                fig.tight_layout()
                st.pyplot(fig)

                # Adicionar logomarca ao gráfico (com a opção de escolher uma logo diferente)
                logo_upload = st.file_uploader("Carregar nova logomarca para o gráfico", type=["png", "jpg", "jpeg"])
                logo_image = None
                if logo_upload is not None:
                    logo_image = Image.open(logo_upload)

                if logo_image is None and os.path.exists(logo_path):
                    logo_image = Image.open(logo_path)

                if logo_image is not None:
                    buf_final = adicionar_logomarca(fig, logo_image)
                    st.image(buf_final)

                # Botão para baixar o gráfico
                if logo_image is not None:
                    st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico_com_logomarca.png", mime="image/png")
                else:
                    buf = salvar_grafico(fig)
                    st.download_button(label="Baixar Gráfico", data=buf, file_name="grafico.png", mime="image/png")

                # Mostrar estatísticas por piloto
                st.title('Estatísticas por Piloto')
                stats = df_total.groupby('piloto').agg(
                    inicio=pd.NamedAgg(column='data', aggfunc='min'),
                    fim=pd.NamedAgg(column='data', aggfunc='max'),
                    total_hectares=pd.NamedAgg(column='hectares', aggfunc='sum'),
                    media_hectares_dia=pd.NamedAgg(column='hectares', aggfunc='mean'),
                    total_dias=pd.NamedAgg(column='data', aggfunc='count')
                ).reset_index()
                st.write(stats)
                
                # Mostrar o total de hectares aplicados por todos os pilotos
                total_hectares_todos = df_total['hectares'].sum()
                st.subheader(f"Total de Hectares Aplicados por Todos os Pilotos: {total_hectares_todos}")

        else:
            st.write("Nenhum dado de piloto disponível.")

        # Mostrar dados da safra
        st.title("Dados da Safra")
        if safra:
            st.write(f"Início: {safra['inicio']}")
            st.write(f"Fim: {safra['fim']}")
            st.write(f"Total de Hectares: {safra['hectares']}")
            st.write(f"Média de Hectares por Dia: {safra['media']}")
            st.write(f"Total de Dias: {safra['dias']}")

            # Gráfico da safra
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(['Safra'], [safra['hectares']], color='blue', alpha=0.6)
            ax.set_ylabel('Hectares')
            ax.set_title('Dados da Safra')
            ax.text(0, safra['hectares'], round(safra['hectares'], 2), ha='center', va='bottom')
            st.pyplot(fig)

            # Adicionar dados dos pilotos no gráfico da safra
            if 'pilotos' in safra:
                fig, axs = plt.subplots(3, 1, figsize=(10, 18), sharex=True)

                # Total de hectares por piloto
                total_hectares_piloto = pd.Series({piloto: dados['hectares'] for piloto, dados in safra['pilotos'].items()})
                axs[0].bar(total_hectares_piloto.index, total_hectares_piloto.values, color='blue', alpha=0.6)
                axs[0].set_title('Total de Hectares por Piloto')
                axs[0].set_ylabel('Total de Hectares')
                for i, v in enumerate(total_hectares_piloto.values):
                    axs[0].text(i, v, round(v, 2), ha='center', va='bottom')

                # Média de hectares por dia por piloto
                media_hectares_piloto = pd.Series({piloto: dados['hectares'] / dados['dias'] if dados['dias'] > 0 else 0 for piloto, dados in safra['pilotos'].items()})
                axs[1].bar(media_hectares_piloto.index, media_hectares_piloto.values, color='blue', alpha=0.6)
                axs[1].set_title('Média de Hectares por Dia por Piloto')
                axs[1].set_ylabel('Média de Hectares')
                for i, v in enumerate(media_hectares_piloto.values):
                    axs[1].text(i, v, round(v, 2), ha='center', va='bottom')

                # Total de dias por piloto
                total_dias_piloto = pd.Series({piloto: dados['dias'] for piloto, dados in safra['pilotos'].items()})
                axs[2].bar(total_dias_piloto.index, total_dias_piloto.values, color='blue', alpha=0.6)
                axs[2].set_title('Total de Dias por Piloto')
                axs[2].set_ylabel('Total de Dias')
                for i, v in enumerate(total_dias_piloto.values):
                    axs[2].text(i, v, round(v, 2), ha='center', va='bottom')

                for ax in axs:
                    ax.set_xlabel('Pilotos')
                    ax.set_xticks(range(len(total_hectares_piloto.index)))
                    ax.set_xticklabels(total_hectares_piloto.index, rotation=45, ha='right')

                fig.tight_layout()
                st.pyplot(fig)

        # Criar backup dos dados
        st.sidebar.title("Backup de Dados")
        if st.sidebar.button("Criar Backup"):
            criar_backup()
            with open('backup.zip', 'rb') as file:
                st.sidebar.download_button(
                    label="Baixar Backup",
                    data=file,
                    file_name="backup.zip",
                    mime="application/zip"
                )
                st.sidebar.success("Backup criado com sucesso!")

        # Recuperar backup dos dados
        st.sidebar.title("Recuperar Backup de Dados")
        backup_upload = st.sidebar.file_uploader("Escolha um arquivo de backup", type=["zip"])
        if backup_upload is not None:
            with open("temp_backup.zip", "wb") as f:
                f.write(backup_upload.getbuffer())
            recuperar_backup("temp_backup.zip")
            st.sidebar.success("Backup recuperado com sucesso! Por favor, recarregue a página.")

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
                dados_piloto = pilotos[piloto_atual]
                datas_existentes = [dado['data'] for dado in dados_piloto]
                if str(data) not in datas_existentes:
                    pilotos[piloto_atual].append({'data': str(data), 'hectares': hectares})
                    salvar_dados(arquivo_pilotos, pilotos)
                    st.sidebar.success(f'{hectares} hectares adicionados para {piloto_atual} em {data}')
                    st.write(f'{hectares} hectares adicionados para {piloto_atual} em {data}')
                else:
                    st.sidebar.error('Já existe uma entrada para essa data. Por favor, edite a entrada existente.')
            else:
                st.sidebar.error('Erro ao identificar o piloto.')

        # Editar dados de hectares
        st.sidebar.subheader('Editar Dados de Hectares')
        dados_piloto = pilotos.get(st.session_state["usuario_logado"], [])
        if dados_piloto:
            df_piloto = pd.DataFrame(dados_piloto)
            selected_date = st.sidebar.selectbox('Selecione a data para editar', df_piloto['data'])
            new_date = st.sidebar.date_input('Nova data', pd.to_datetime(selected_date))
            new_hectares = st.sidebar.number_input('Novo valor de Hectares', min_value=0.0, format="%.2f")
            if st.sidebar.button('Salvar Alterações'):
                for dado in pilotos[st.session_state["usuario_logado"]]:
                    if dado['data'] == selected_date:
                        dado['data'] = str(new_date)
                        dado['hectares'] = new_hectares
                salvar_dados(arquivo_pilotos, pilotos)
                st.sidebar.success('Dados atualizados com sucesso!')

        # Remover dados de hectares por data
        st.sidebar.subheader('Remover Dados de Hectares')
        if dados_piloto:
            selected_date_remove = st.sidebar.selectbox('Selecione a data para remover', df_piloto['data'])
            if st.sidebar.button('Remover Dados'):
                pilotos[st.session_state["usuario_logado"]] = [dado for dado in pilotos[st.session_state["usuario_logado"]] if dado['data'] != selected_date_remove]
                salvar_dados(arquivo_pilotos, pilotos)
                st.sidebar.success('Dados removidos com sucesso!')

        # Alterar nome e senha do piloto
        st.sidebar.subheader('Alterar Nome e Senha')
        novo_nome = st.sidebar.text_input('Novo Nome de Usuário')
        nova_senha = st.sidebar.text_input('Nova Senha', type='password')
        alterar_dados_button = st.sidebar.button('Alterar Dados')

        if alterar_dados_button:
            if novo_nome and nova_senha:
                if novo_nome not in usuarios or novo_nome == st.session_state["usuario_logado"]:
                    usuarios[novo_nome] = {
                        'senha': gerar_hash_senha(nova_senha),
                        'tipo': 'Piloto'
                    }
                    pilotos[novo_nome] = pilotos.pop(st.session_state["usuario_logado"])
                    cores[novo_nome] = cores.pop(st.session_state["usuario_logado"])
                    fotos[novo_nome] = fotos.pop(st.session_state["usuario_logado"])
                    if novo_nome != st.session_state["usuario_logado"]:
                        del usuarios[st.session_state["usuario_logado"]]
                    st.session_state["usuario_logado"] = novo_nome
                    salvar_dados(arquivo_usuarios, usuarios)
                    salvar_dados(arquivo_pilotos, pilotos)
                    salvar_dados(arquivo_cores, cores)
                    salvar_dados(arquivo_fotos, fotos)
                    st.sidebar.success('Dados alterados com sucesso!')
                else:
                    st.sidebar.error('Nome de usuário já existe.')
            else:
                st.sidebar.error('Por favor, preencha todos os campos.')

        # Upload de foto de perfil
        st.sidebar.subheader('Foto de Perfil')
        uploaded_file = st.sidebar.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            foto_path = f'foto_{st.session_state["usuario_logado"]}.png'
            with open(foto_path, 'wb') as f:
                f.write(bytes_data)
            fotos[st.session_state["usuario_logado"]] = foto_path
            salvar_dados(arquivo_fotos, fotos)
            st.sidebar.success('Foto de perfil atualizada com sucesso!')

        # Mostrar mensagem motivacional
        st.title(f'Dados do Piloto: {st.session_state["usuario_logado"]}')
        foto_piloto = fotos.get(st.session_state["usuario_logado"])
        if foto_piloto and os.path.exists(foto_piloto):
            st.image(foto_piloto, caption="Foto de Perfil", use_column_width=False, width=150)

        dados_piloto = pilotos.get(st.session_state["usuario_logado"], [])

        if dados_piloto:
            df_piloto = pd.DataFrame(dados_piloto)
            st.write(df_piloto)

            hectares_totais = df_piloto['hectares'].sum()
            media_hectares_dia = df_piloto['hectares'].mean()
            total_dias = df_piloto['data'].nunique()

            if media_hectares_dia < 40:
                st.warning("Você não bateu a meta diária de 40 hectares. Vamos melhorar!")
            elif media_hectares_dia == 40:
                st.info("Você bateu a meta diária de 40 hectares! Vamos continuar assim e melhorar ainda mais!")
            else:
                st.success("Parabéns! Você superou a meta diária de 40 hectares! Continue com o ótimo trabalho!")

            st.subheader(f"Total de Hectares Aplicados: {hectares_totais}")
        else:
            st.write("Nenhum dado disponível para este piloto.")

if __name__ == "__main__":
    main()
