import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageDraw
import os
import hashlib
import json
from zipfile import ZipFile
from datetime import datetime

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
        zipf.write('fazendas.json')

# Função para recuperar backup dos dados
def recuperar_backup(arquivo):
    with ZipFile(arquivo, 'r') as zipf:
        zipf.extractall()

# Função principal do aplicativo
def main():
    st.set_page_config(page_title="PILOTOS DS DRONES", page_icon=":drone:", layout="wide")
    st.title('PILOTOS DS DRONES')

    # Arquivos de dados
    arquivo_pilotos = 'pilotos.json'
    arquivo_cores = 'cores.json'
    arquivo_usuarios = 'usuarios.json'
    arquivo_fotos = 'fotos.json'
    arquivo_safra = 'safra.json'
    arquivo_fazendas = 'fazendas.json'

    # Carregar dados do JSON
    pilotos = carregar_dados(arquivo_pilotos)
    cores = carregar_dados(arquivo_cores)
    usuarios = carregar_dados(arquivo_usuarios)
    fotos = carregar_dados(arquivo_fotos)
    safra = carregar_dados(arquivo_safra)
    fazendas = carregar_dados(arquivo_fazendas)

    if not usuarios:
        usuarios['admin'] = {
            'senha': gerar_hash_senha('admin123'),
            'tipo': 'Administrador'
        }

    # Adicionar o logotipo da empresa na barra lateral
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)

    # Página de login
    if 'usuario_logado' not in st.session_state:
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
    else:
        st.sidebar.success(f"Bem-vindo, {st.session_state['usuario_logado']}!")

        if st.sidebar.button("Sair da Conta"):
            del st.session_state['usuario_logado']
            del st.session_state['painel']
            st.experimental_rerun()

    if 'usuario_logado' in st.session_state:
        # Cadastro de novos pilotos pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Cadastrar Novo Piloto"):
                new_pilot_username = st.text_input("Nome do Novo Piloto")
                new_pilot_password = st.text_input("Senha do Novo Piloto", type="password")
                register_pilot_button = st.button("Cadastrar Piloto")

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
                            st.success(f"Piloto {new_pilot_username} cadastrado com sucesso!")
                        else:
                            st.error("Piloto já existe")
                    else:
                        st.error("Por favor, insira um nome de usuário e uma senha")

        # Cadastro de fazendas pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Cadastrar Nova Fazenda"):
                new_farm_name = st.text_input("Nome da Nova Fazenda")
                new_farm_hectares = st.number_input("Total de Hectares da Fazenda", min_value=0.0, format="%.2f")
                register_farm_button = st.button("Cadastrar Fazenda")

                if register_farm_button:
                    if new_farm_name and new_farm_hectares:
                        if new_farm_name not in fazendas:
                            fazendas[new_farm_name] = {
                                'total_hectares': new_farm_hectares,
                                'dados_aplicacao': []
                            }
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Fazenda {new_farm_name} cadastrada com sucesso!")
                        else:
                            st.error("Fazenda já existe")
                    else:
                        st.error("Por favor, insira um nome e o total de hectares da fazenda")

        # Remover piloto pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Remover Piloto"):
                remove_pilot_username = st.selectbox("Selecione o Piloto para Remover", list(pilotos.keys()))
                remove_pilot_button = st.button("Remover Piloto")

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
                        st.success(f"Piloto {remove_pilot_username} removido com sucesso!")
                    else:
                        st.error("Piloto não encontrado")

        # Remover fazenda pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Remover Fazenda"):
                remove_farm_name = st.selectbox("Selecione a Fazenda para Remover", list(fazendas.keys()))
                remove_farm_button = st.button("Remover Fazenda")

                if remove_farm_button:
                    if remove_farm_name in fazendas:
                        del fazendas[remove_farm_name]
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success(f"Fazenda {remove_farm_name} removida com sucesso!")
                    else:
                        st.error("Fazenda não encontrada")

        # Painel do Administrador
        if st.session_state['painel'] == "Administrador":
            st.title("Painel do Administrador")

            # Modificar cores dos pilotos
            with st.sidebar.expander("Modificar Cores dos Pilotos"):
                for piloto in pilotos:
                    nova_cor = st.color_picker(f"Cor do {piloto}", value=cores.get(piloto, '#00ff00'))
                    cores[piloto] = nova_cor
                salvar_dados(arquivo_cores, cores)

            # Organizar a seção de Dados da Safra
            st.subheader("Dados da Safra")
            with st.expander("Adicionar Dados da Safra"):
                safra['pilotos'] = safra.get('pilotos', {})
                st.session_state.novo_piloto = st.text_input("Nome do Piloto", value=st.session_state.get('novo_piloto', ""))
                inicio_safra = st.date_input("Data de Início da Safra")
                fim_safra = st.date_input("Data de Fim da Safra")
                hectares = st.number_input("Total de Hectares", min_value=0.0, format="%.2f")
                if st.button("Adicionar Piloto e Dados da Safra"):
                    if st.session_state.novo_piloto and str(inicio_safra) and str(fim_safra):
                        safra['pilotos'][st.session_state.novo_piloto] = {
                            'inicio': str(inicio_safra),
                            'fim': str(fim_safra),
                            'hectares': hectares
                        }
                        salvar_dados(arquivo_safra, safra)
                        st.success(f"Dados da safra para {st.session_state.novo_piloto} adicionados com sucesso!")
                        st.session_state.novo_piloto = ""
                    else:
                        st.error("Por favor, preencha todos os campos.")

            with st.expander("Editar Dados da Safra"):
                pilotos_safra = list(safra['pilotos'].keys())
                if pilotos_safra:
                    piloto_selecionado = st.selectbox("Selecione o Piloto para Editar", pilotos_safra)
                    if piloto_selecionado:
                        novo_inicio_safra = st.date_input("Nova Data de Início", pd.to_datetime(safra['pilotos'][piloto_selecionado]['inicio']))
                        novo_fim_safra = st.date_input("Nova Data de Fim", pd.to_datetime(safra['pilotos'][piloto_selecionado]['fim']))
                        novo_hectares = st.number_input("Novo Total de Hectares", min_value=0.0, format="%.2f", value=safra['pilotos'][piloto_selecionado]['hectares'])
                        if st.button("Salvar Alterações"):
                            safra['pilotos'][piloto_selecionado]['inicio'] = str(novo_inicio_safra)
                            safra['pilotos'][piloto_selecionado]['fim'] = str(novo_fim_safra)
                            safra['pilotos'][piloto_selecionado]['hectares'] = novo_hectares
                            salvar_dados(arquivo_safra, safra)
                            st.success(f"Dados da safra para {piloto_selecionado} atualizados com sucesso!")

            with st.expander("Remover Dados da Safra"):
                if pilotos_safra:
                    piloto_remover = st.selectbox("Selecione o Piloto para Remover os Dados", pilotos_safra)
                    if st.button("Remover Dados da Safra"):
                        if piloto_remover in safra['pilotos']:
                            del safra['pilotos'][piloto_remover]
                            salvar_dados(arquivo_safra, safra)
                            st.success(f"Dados da safra do piloto {piloto_remover} removidos com sucesso!")
                        else:
                            st.error("Piloto não encontrado na safra")

            # Mostrar gráficos e listas
            st.subheader('Dados de Todos os Pilotos')
            if pilotos:
                df_total = pd.DataFrame()
                for piloto, dados in pilotos.items():
                    if dados:
                        df_piloto = pd.DataFrame(dados)
                        if 'data' in df_piloto.columns:
                            df_piloto['data'] = pd.to_datetime(df_piloto['data'])
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
                    st.subheader('Estatísticas por Piloto')
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

            # Mostrar dados das fazendas
            st.subheader("Dados das Fazendas")
            if fazendas:
                df_fazendas = pd.DataFrame()
                for fazenda, dados in fazendas.items():
                    for aplicacao in dados['dados_aplicacao']:
                        aplicacao['fazenda'] = fazenda
                        df_fazendas = pd.concat([df_fazendas, pd.DataFrame([aplicacao])])

                if not df_fazendas.empty:
                    df_fazendas['data'] = pd.to_datetime(df_fazendas['data'])  # Certificar que a coluna 'data' está no formato datetime

                    st.write("Dados agregados das fazendas:")
                    st.write(df_fazendas)

                    # Mostrar todas as fazendas cadastradas com o total de hectares
                    st.subheader("Lista de Fazendas Cadastradas")
                    lista_fazendas = pd.DataFrame.from_dict(fazendas, orient='index')
                    st.write(lista_fazendas[['total_hectares']])

                    # Gráfico das fazendas
                    fig, ax = plt.subplots(figsize=(10, 6))
                    for fazenda, dados in fazendas.items():
                        df_fazenda = pd.DataFrame(dados['dados_aplicacao'])
                        if not df_fazenda.empty:
                            df_fazenda['data'] = pd.to_datetime(df_fazenda['data'])
                            ax.bar(df_fazenda['data'].dt.strftime('%Y-%m-%d'), df_fazenda['hectares'], label=fazenda)

                    ax.set_title('Total de Hectares por Fazenda')
                    ax.set_ylabel('Total de Hectares')
                    ax.set_xlabel('Data')
                    ax.legend(title="Fazendas")
                    fig.autofmt_xdate()
                    st.pyplot(fig)

    # Criar backup dos dados
    with st.sidebar.expander("Backup de Dados"):
        if st.button("Criar Backup"):
            criar_backup()
            with open('backup.zip', 'rb') as file:
                st.download_button(
                    label="Baixar Backup",
                    data=file,
                    file_name="backup.zip",
                    mime="application/zip"
                )
                st.success("Backup criado com sucesso!")

    # Recuperar backup dos dados
    with st.sidebar.expander("Recuperar Backup de Dados"):
        backup_upload = st.file_uploader("Escolha um arquivo de backup", type=["zip"])
        if backup_upload is not None:
            with open("temp_backup.zip", "wb") as f:
                f.write(backup_upload.getbuffer())
            recuperar_backup("temp_backup.zip")
            st.success("Backup recuperado com sucesso! Por favor, recarregue a página.")

    # Visualização diária por piloto
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Administrador":
        st.subheader("Visualização Diária por Piloto")
        hoje = datetime.today().strftime('%Y-%m-%d')
        st.write(f"Dados de aplicação diária para {hoje}")

        if pilotos:
            df_hoje = pd.DataFrame()
            for piloto, dados in pilotos.items():
                df_piloto = pd.DataFrame(dados)
                if 'data' in df_piloto.columns:
                    df_piloto['data'] = pd.to_datetime(df_piloto['data'])
                    df_hoje_piloto = df_piloto[df_piloto['data'] == pd.to_datetime(hoje)]
                    if not df_hoje_piloto.empty:
                        df_hoje_piloto['piloto'] = piloto
                        df_hoje = pd.concat([df_hoje, df_hoje_piloto])

            if not df_hoje.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                for piloto in df_hoje['piloto'].unique():
                    df_piloto = df_hoje[df_hoje['piloto'] == piloto]
                    ax.bar(df_piloto['piloto'], df_piloto['hectares'], label=piloto, color=cores.get(piloto, 'blue'))

                ax.set_title('Total de Hectares Aplicado Hoje')
                ax.set_ylabel('Total de Hectares')
                ax.set_xlabel('Piloto')
                ax.legend(title="Pilotos")

                for i, v in enumerate(df_hoje['hectares']):
                    ax.text(i, v, round(v, 2), ha='center', va='bottom')

                st.pyplot(fig)
            else:
                st.write("Nenhum dado de aplicação para hoje.")
        else:
            st.write("Nenhum dado de piloto disponível.")

    # Painel do Piloto
    if 'usuario_logado' in st.session_state and st.session_state['painel'] == "Piloto":
        st.sidebar.title('Painel do Piloto')
        st.sidebar.success(f'Logado como {st.session_state["usuario_logado"]}')
        st.write(f'Piloto atual: {st.session_state["usuario_logado"]}')

        # Entrada de Hectares
        with st.sidebar.expander("Entrada de Hectares"):
            data = st.date_input('Data')
            hectares = st.number_input('Hectares', min_value=0.0, format="%.2f")
            fazenda = st.selectbox('Fazenda', list(fazendas.keys()))

            if st.button('Adicionar Hectares'):
                piloto_atual = st.session_state["usuario_logado"]
                if piloto_atual and fazenda:
                    dados_piloto = pilotos[piloto_atual]
                    datas_existentes = [dado['data'] for dado in dados_piloto]
                    if str(data) not in datas_existentes:
                        pilotos[piloto_atual].append({'data': str(data), 'hectares': hectares, 'fazenda': fazenda})
                        fazendas[fazenda]['dados_aplicacao'].append({'data': str(data), 'hectares': hectares, 'piloto': piloto_atual})
                        salvar_dados(arquivo_pilotos, pilotos)
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success(f'{hectares} hectares adicionados para {piloto_atual} em {data} na fazenda {fazenda}')
                        st.write(f'{hectares} hectares adicionados para {piloto_atual} em {data} na fazenda {fazenda}')
                    else:
                        st.error('Já existe uma entrada para essa data. Por favor, edite a entrada existente.')
                else:
                    st.error('Erro ao identificar o piloto ou a fazenda.')

        # Editar dados de hectares
        with st.sidebar.expander("Editar Dados de Hectares"):
            dados_piloto = pilotos.get(st.session_state["usuario_logado"], [])
            if dados_piloto:
                df_piloto = pd.DataFrame(dados_piloto)
                if 'fazenda' not in df_piloto.columns:
                    st.error('Nenhum dado de fazenda disponível.')
                else:
                    selected_date = st.selectbox('Selecione a data para editar', df_piloto['data'])
                    new_date = st.date_input('Nova data', pd.to_datetime(selected_date))
                    new_hectares = st.number_input('Novo valor de Hectares', min_value=0.0, format="%.2f")
                    new_fazenda = st.selectbox('Nova Fazenda', list(fazendas.keys()), index=list(fazendas.keys()).index(df_piloto[df_piloto['data'] == selected_date]['fazenda'].values[0]))
                    if st.button('Salvar Alterações'):
                        for dado in pilotos[st.session_state["usuario_logado"]]:
                            if dado['data'] == selected_date:
                                dado['data'] = str(new_date)
                                dado['hectares'] = new_hectares
                                dado['fazenda'] = new_fazenda
                        salvar_dados(arquivo_pilotos, pilotos)
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success('Dados atualizados com sucesso!')

        # Remover dados de hectares por data
        with st.sidebar.expander("Remover Dados de Hectares"):
            if dados_piloto:
                df_piloto = pd.DataFrame(dados_piloto)
                selected_date_remove = st.selectbox('Selecione a data para remover', df_piloto['data'])
                if st.button('Remover Dados'):
                    pilotos[st.session_state["usuario_logado"]] = [dado for dado in pilotos[st.session_state["usuario_logado"]] if dado['data'] != selected_date_remove]
                    fazendas = {fazenda: {'total_hectares': dados['total_hectares'], 'dados_aplicacao': [dado for dado in dados['dados_aplicacao'] if dado['data'] != selected_date_remove]} for fazenda, dados in fazendas.items()}
                    salvar_dados(arquivo_pilotos, pilotos)
                    salvar_dados(arquivo_fazendas, fazendas)
                    st.success('Dados removidos com sucesso!')

        # Alterar nome e senha do piloto
        with st.sidebar.expander("Alterar Nome e Senha"):
            novo_nome = st.text_input('Novo Nome de Usuário')
            nova_senha = st.text_input('Nova Senha', type='password')
            alterar_dados_button = st.button('Alterar Dados')

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
                        st.success('Dados alterados com sucesso!')
                    else:
                        st.error('Nome de usuário já existe.')
                else:
                    st.error('Por favor, preencha todos os campos.')

        # Upload de foto de perfil
        with st.sidebar.expander("Foto de Perfil"):
            uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"])
            if uploaded_file is not None:
                bytes_data = uploaded_file.read()
                foto_path = f'foto_{st.session_state["usuario_logado"]}.png'
                with open(foto_path, 'wb') as f:
                    f.write(bytes_data)
                fotos[st.session_state["usuario_logado"]] = foto_path
                salvar_dados(arquivo_fotos, fotos)
                st.success('Foto de perfil atualizada com sucesso!')

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

            # Mostrar mensagem motivacional
            if media_hectares_dia < 40:
                st.warning("Você não bateu a meta diária de 40 hectares. Vamos melhorar!")
            elif media_hectares_dia == 40:
                st.info("Você bateu a meta diária de 40 hectares! Vamos continuar assim e melhorar ainda mais!")
            else:
                st.success("Parabéns! Você superou a meta diária de 40 hectares! Continue com o ótimo trabalho!")

            st.subheader(f"Total de Hectares Aplicados: {hectares_totais}")
            st.subheader(f"Média de Hectares por Dia: {media_hectares_dia}")
            st.subheader(f"Total de Dias Trabalhados: {total_dias}")
        else:
            st.write("Nenhum dado disponível para este piloto.")

if __name__ == "__main__":
    main()
