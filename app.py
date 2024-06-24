import streamlit as st
import pandas as pdimport streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
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
        zipf.write('ajudantes.json')

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
    arquivo_ajudantes = 'ajudantes.json'

    # Carregar dados do JSON
    pilotos = carregar_dados(arquivo_pilotos)
    cores = carregar_dados(arquivo_cores)
    usuarios = carregar_dados(arquivo_usuarios)
    fotos = carregar_dados(arquivo_fotos)
    safra = carregar_dados(arquivo_safra)
    fazendas = carregar_dados(arquivo_fazendas)
    ajudantes = carregar_dados(arquivo_ajudantes)

    if não_usuarios:
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
                new_pilot_username = st.text_input("Nome do Novo Piloto", key="new_pilot_username")
                new_pilot_password = st.text_input("Senha do Novo Piloto", type="password", key="new_pilot_password")
                register_pilot_button = st.button("Cadastrar Piloto", key="register_pilot_button")

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
                            ajudantes[new_pilot_username] = None  # Sem ajudante inicialmente
                            salvar_dados(arquivo_usuarios, usuarios)
                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_cores, cores)
                            salvar_dados(arquivo_fotos, fotos)
                            salvar_dados(arquivo_ajudantes, ajudantes)
                            st.success(f"Piloto {new_pilot_username} cadastrado com sucesso!")
                        else:
                            st.error("Piloto já existe")
                    else:
                        st.error("Por favor, insira um nome de usuário e uma senha")

        # Cadastro de novos ajudantes pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Cadastrar Novo Ajudante"):
                new_ajudante_username = st.text_input("Nome do Novo Ajudante", key="new_ajudante_username")
                new_ajudante_password = st.text_input("Senha do Novo Ajudante", type="password", key="new_ajudante_password")
                register_ajudante_button = st.button("Cadastrar Ajudante", key="register_ajudante_button")

                if register_ajudante_button:
                    if new_ajudante_username and new_ajudante_password:
                        if new_ajudante_username not in usuarios:
                            usuarios[new_ajudante_username] = {
                                'senha': gerar_hash_senha(new_ajudante_password),
                                'tipo': 'Ajudante'
                            }
                            pilotos[new_ajudante_username] = []
                            cores[new_ajudante_username] = '#ff0000'  # Vermelho
                            fotos[new_ajudante_username] = None
                            salvar_dados(arquivo_usuarios, usuarios)
                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_cores, cores)
                            salvar_dados(arquivo_fotos, fotos)
                            st.success(f"Ajudante {new_ajudante_username} cadastrado com sucesso!")
                        else:
                            st.error("Ajudante já existe")
                    else:
                        st.error("Por favor, insira um nome de usuário e uma senha")

        # Cadastro de fazendas e pastos pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Cadastrar Nova Fazenda"):
                new_farm_name = st.text_input("Nome da Nova Fazenda", key="new_farm_name")
                pastos = []
                numero_pastos = st.number_input("Número de Pastos", min_value=1, max_value=20, step=1, key="numero_pastos")
                for i in range(int(numero_pastos)):
                    pasto_name = st.text_input(f"Nome do Pasto {i + 1}", key=f"pasto_name_{i}")
                    pasto_hectares = st.number_input(f"Hectares do Pasto {i + 1}", min_value=0.0, format="%.2f", key=f"pasto_hectares_{i}")
                    pastos.append((pasto_name, pasto_hectares))
                if st.button("Cadastrar Fazenda", key="register_farm_button"):
                    if new_farm_name and all(pasto[0] and pasto[1] for pasto in pastos):
                        if new_farm_name not in fazendas:
                            fazendas[new_farm_name] = {
                                'pastos': {pasto[0]: {'tamanho': pasto[1], 'dados_aplicacao': []} for pasto in pastos}
                            }
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Fazenda {new_farm_name} cadastrada com sucesso!")
                        else:
                            st.error("Fazenda já existe")
                    else:
                        st.error("Por favor, insira um nome para a fazenda e todos os pastos com seus hectares")

        # Associar pilotos às fazendas
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Associar Piloto à Fazenda"):
                selected_pilot = st.selectbox("Selecione o Piloto", list(usuarios.keys()), key="selected_pilot")
                selected_farm = st.selectbox("Selecione a Fazenda", list(fazendas.keys()), key="selected_farm_association")
                if st.button("Associar Piloto à Fazenda", key="associate_pilot_farm_button"):
                    if selected_pilot and selected_farm:
                        if 'fazendas' not in usuarios[selected_pilot]:
                            usuarios[selected_pilot]['fazendas'] = []
                        if selected_farm not in usuarios[selected_pilot]['fazendas']:
                            usuarios[selected_pilot]['fazendas'].append(selected_farm)
                            salvar_dados(arquivo_usuarios, usuarios)
                            st.success(f"Piloto {selected_pilot} associado à fazenda {selected_farm} com sucesso!")
                        else:
                            st.error("Piloto já está associado a esta fazenda")
                    else:
                        st.error("Por favor, selecione um piloto e uma fazenda")

        # Associar ajudantes aos pilotos
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Associar Ajudante ao Piloto"):
                selected_pilot_for_ajudante = st.selectbox("Selecione o Piloto", list(usuarios.keys()), key="selected_pilot_for_ajudante")
                available_ajudantes = [user for user, data in usuarios.items() if data['tipo'] == 'Ajudante' and user not in ajudantes.values()]
                selected_ajudante = st.selectbox("Selecione o Ajudante", available_ajudantes, key="selected_ajudante")
                if st.button("Associar Ajudante ao Piloto", key="associate_ajudante_pilot_button"):
                    if selected_pilot_for_ajudante and selected_ajudante:
                        ajudantes[selected_pilot_for_ajudante] = selected_ajudante
                        salvar_dados(arquivo_ajudantes, ajudantes)
                        st.success(f"Ajudante {selected_ajudante} associado ao piloto {selected_pilot_for_ajudante} com sucesso!")
                    else:
                        st.error("Por favor, selecione um piloto e um ajudante")

        # Alterar associação de pilotos às fazendas
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Alterar Associação de Pilotos às Fazendas"):
                selected_farm_to_edit_assoc = st.selectbox("Selecione a Fazenda para Editar", list(fazendas.keys()), key="selected_farm_to_edit_assoc")
                if selected_farm_to_edit_assoc:
                    pilotos_associados = [usuario for usuario, dados in usuarios.items() if 'fazendas' in dados e selected_farm_to_edit_assoc in dados['fazendas']]
                    pilotos_nao_associados = [usuario for usuario in usuarios se usuario not in pilotos_associados e usuario != 'admin']
                    piloto_remover = st.selectbox("Selecione o Piloto para Remover da Fazenda", pilotos_associados, key="piloto_remover_assoc")
                    piloto_adicionar = st.selectbox("Selecione o Piloto para Adicionar à Fazenda", pilotos_nao_associados, key="piloto_adicionar_assoc")

                    if st.button("Remover Piloto da Fazenda", key="remove_pilot_from_farm_button_assoc"):
                        if piloto_remover in usuarios e selected_farm_to_edit_assoc in usuarios[piloto_remover]['fazendas']:
                            usuarios[piloto_remover]['fazendas'].remove(selected_farm_to_edit_assoc)
                            salvar_dados(arquivo_usuarios, usuarios)
                            st.success(f"Piloto {piloto_remover} removido da fazenda {selected_farm_to_edit_assoc} com sucesso!")

                    if st.button("Adicionar Piloto à Fazenda", key="add_pilot_to_farm_button_assoc"):
                        if piloto_adicionar in usuarios:
                            if 'fazendas' not in usuarios[piloto_adicionar]:
                                usuarios[piloto_adicionar]['fazendas'] = []
                            if selected_farm_to_edit_assoc not in usuarios[piloto_adicionar]['fazendas']:
                                usuarios[piloto_adicionar]['fazendas'].append(selected_farm_to_edit_assoc)
                                salvar_dados(arquivo_usuarios, usuarios)
                                st.success(f"Piloto {piloto_adicionar} adicionado à fazenda {selected_farm_to_edit_assoc} com sucesso!")
                            else:
                                st.error("Piloto já está associado a esta fazenda")
                        else:
                            st.error("Piloto não encontrado")

        # Alterar fazendas e pastos
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Alterar Fazendas e Pastos"):
                selected_farm_to_edit = st.selectbox("Selecione a Fazenda para Editar", list(fazendas.keys()), key="selected_farm_to_edit")
                if selected_farm_to_edit:
                    farm_data = fazendas[selected_farm_to_edit]
                    new_farm_name = st.text_input("Novo Nome da Fazenda", value=selected_farm_to_edit, key="new_farm_name_edit")
                    if st.button("Renomear Fazenda", key="rename_farm_button"):
                        if new_farm_name:
                            fazendas[new_farm_name] = fazendas.pop(selected_farm_to_edit)
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Fazenda renomeada para {new_farm_name}")

                    for pasto em list(fazendas[selected_farm_to_edit]['pastos'].keys()):
                        pasto_data = fazendas[selected_farm_to_edit]['pastos'][pasto]
                        new_pasto_name = st.text_input(f"Novo Nome do Pasto ({pasto})", value=pasto, key=f"new_pasto_name_{pasto}")
                        new_pasto_hectares = st.number_input(f"Novo Tamanho do Pasto ({pasto})", value=pasto_data.get('tamanho', 0.0), min_value=0.0, format="%.2f", key=f"new_pasto_hectares_{pasto}")
                        if st.button(f"Salvar Alterações do Pasto ({pasto})", key=f"save_pasto_changes_button_{pasto}"):
                            if new_pasto_name != pasto:
                                fazendas[selected_farm_to_edit]['pastos'][new_pasto_name] = fazendas[selected_farm_to_edit]['pastos'].pop(pasto)
                            fazendas[selected_farm_to_edit]['pastos'][new_pasto_name]['tamanho'] = new_pasto_hectares
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Pasto {pasto} atualizado com sucesso!")

                    novo_pasto_name = st.text_input("Nome do Novo Pasto", key="new_pasto_name_add")
                    novo_pasto_hectares = st.number_input("Tamanho do Novo Pasto (hectares)", min_value=0.0, format="%.2f", key="new_pasto_hectares_add")
                    if st.button("Adicionar Novo Pasto", key="add_new_pasto_button"):
                        if novo_pasto_name e novo_pasto_hectares:
                            if novo_pasto_name not in fazendas[selected_farm_to_edit]['pastos']:
                                fazendas[selected_farm_to_edit]['pastos'][novo_pasto_name] = {'tamanho': novo_pasto_hectares, 'dados_aplicacao': []}
                                salvar_dados(arquivo_fazendas, fazendas)
                                st.success(f"Pasto {novo_pasto_name} adicionado com sucesso!")
                            else:
                                st.error("Pasto já existe")

                    pasto_to_remove = st.selectbox("Selecione o Pasto para Remover", list(fazendas[selected_farm_to_edit]['pastos'].keys()), key="pasto_to_remove")
                    if st.button("Remover Pasto", key="remove_pasto_button"):
                        if pasto_to_remove em fazendas[selected_farm_to_edit]['pastos']:
                            del fazendas[selected_farm_to_edit]['pastos'][pasto_to_remove]
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Pasto {pasto_to_remove} removido com sucesso!")

        # Painel do Administrador
        if st.session_state['painel'] == "Administrador":
            st.title("Painel do Administrador")

            # Mostrar lista de pilotos e ajudantes
            with st.expander("Lista de Pilotos e Ajudantes"):
                st.subheader("Pilotos")
                for piloto em [user for user, data in usuarios.items() if data['tipo'] == 'Piloto']:
                    if st.checkbox(piloto, key=f"checkbox_piloto_{piloto}"):
                        st.write(f"**Fazendas Associadas:** {', '.join(usuarios[piloto].get('fazendas', []))}")
                        st.write(f"**Ajudante:** {ajudantes.get(piloto, 'Nenhum ajudante associado')}")

                        if piloto em pilotos:
                            df_piloto = pd.DataFrame(pilotos[piloto])
                            if não df_piloto.empty:
                                st.write("**Dados de Aplicações:**")
                                st.write(df_piloto)
                            else:
                                st.write("Nenhum dado de aplicação disponível.")

                st.subheader("Ajudantes")
                for ajudante em [user for user, data in usuarios.items() if data['tipo'] == 'Ajudante']:
                    if st.checkbox(ajudante, key=f"checkbox_ajudante_{ajudante}"):
                        st.write("**Dados de Aplicações:**")
                        if ajudante em pilotos:
                            df_ajudante = pd.DataFrame(pilotos[ajudante])
                            if não df_ajudante.empty:
                                st.write(df_ajudante)
                            else:
                                st.write("Nenhum dado de aplicação disponível.")
                        else:
                            st.write("Nenhum dado de aplicação disponível.")

            # Mostrar dados organizados por fazenda e piloto
            with st.expander("Lista de Fazendas"):
                if fazendas:
                    for fazenda, dados_fazenda em fazendas.items():
                        total_hectares_fazenda = sum(pasto['tamanho'] for pasto em dados_fazenda['pastos'].values())
                        if st.checkbox(f"{fazenda} ({total_hectares_fazenda} hectares)", key=f"checkbox_{fazenda}"):
                            for pasto, dados_pasto em dados_fazenda['pastos'].items():
                                with st.expander(f"Pasto: {pasto} ({dados_pasto['tamanho']} hectares)"):
                                    if dados_pasto['dados_aplicacao']:
                                        df_pasto = pd.DataFrame(dados_pasto['dados_aplicacao'])
                                        st.write(df_pasto)
                                    else:
                                        st.write("Nenhuma aplicação registrada para este pasto.")
            
            # Modificar cores dos pilotos
            with st.sidebar.expander("Modificar Cores dos Pilotos"):
                for piloto em pilotos:
                    nova_cor = st.color_picker(f"Cor do {piloto}", value=cores.get(piloto, '#00ff00'), key=f"color_picker_{piloto}")
                    cores[piloto] = nova_cor
                salvar_dados(arquivo_cores, cores)

            # Exibir gráficos de dados de todos os pilotos
            with st.expander('Dados de Todos os Pilotos'):
                if pilotos:
                    df_total = pd.DataFrame()
                    for piloto, dados em pilotos.items():
                        if dados:
                            df_piloto = pd.DataFrame(dados)
                            if 'data' em df_piloto.columns:
                                df_piloto['data'] = pd.to_datetime(df_piloto['data'])
                            df_piloto['piloto'] = piloto
                            df_total = pd.concat([df_total, df_piloto])

                    if não df_total.empty:
                        st.write("Dados agregados dos pilotos:")
                        st.write(df_total)

                        fig, axs = plt.subplots(3, 1, figsize=(10, 18), sharex=True)

                        # Total de hectares
                        total_hectares = df_total.groupby('piloto')['hectares'].sum()
                        axs[0].bar(total_hectares.index, total_hectares.values, color=[cores[piloto] for piloto em total_hectares.index])
                        axs[0].set_title('Total de Hectares Aplicado')
                        axs[0].set_ylabel('Total de Hectares')
                        for i, v em enumerate(total_hectares.values):
                            axs[0].text(i, v, round(v, 2), ha='center', va='bottom')

                        # Média de hectares por dia
                        media_hectares = df_total.groupby('piloto')['hectares'].mean()
                        axs[1].bar(media_hectares.index, media_hectares.values, color=[cores[piloto] for piloto em media_hectares.index])
                        axs[1].set_title('Média de Hectares por Dia')
                        axs[1].set_ylabel('Média de Hectares')
                        for i, v em enumerate(media_hectares.values):
                            axs[1].text(i, v, round(v, 2), ha='center', va='bottom')

                        # Total de dias
                        total_dias = df_total.groupby('piloto')['data'].count()
                        axs[2].bar(total_dias.index, total_dias.values, color=[cores[piloto] for piloto em total_dias.index])
                        axs[2].set_title('Total de Dias de Aplicação')
                        axs[2].set_ylabel('Total de Dias')
                        for i, v em enumerate(total_dias.values):
                            axs[2].text(i, v, round(v, 2), ha='center', va='bottom')

                        for ax em axs:
                            ax.set_xlabel('Pilotos')
                            ax.set_xticks(range(len(total_hectares.index)))
                            ax.set_xticklabels(total_hectares.index, rotation=45, ha='right')

                        fig.tight_layout()
                        st.pyplot(fig)

                        # Adicionar logomarca ao gráfico (com a opção de escolher uma logo diferente)
                        logo_upload = st.file_uploader("Carregar nova logomarca para o gráfico", type=["png", "jpg", "jpeg"], key="logo_upload")
                        logo_image = None
                        if logo_upload is not None:
                            logo_image = Image.open(logo_upload)

                        if logo_image is None e os.path.exists(logo_path):
                            logo_image = Image.open(logo_path)

                        if logo_image is not None:
                            buf_final = adicionar_logomarca(fig, logo_image)
                            st.image(buf_final)

                        # Botão para baixar o gráfico
                        if logo_image is not None:
                            st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico_com_logomarca.png", mime="image/png", key="download_graphic_button")
                        else:
                            buf = salvar_grafico(fig)
                            st.download_button(label="Baixar Gráfico", data=buf, file_name="grafico.png", mime="image/png", key="download_graphic_button_no_logo")

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
                
                else:
                    st.write("Nenhum dado de piloto disponível.")

                # Visualização diária por piloto
                st.subheader("Visualização Diária por Piloto")
                hoje = datetime.today().strftime('%Y-%m-%d')
                st.write(f"Dados de aplicação diária para {hoje}")

                if pilotos:
                    df_hoje = pd.DataFrame()
                    for piloto, dados em pilotos.items():
                        df_piloto = pd.DataFrame(dados)
                        if 'data' em df_piloto.columns:
                            df_piloto['data'] = pd.to_datetime(df_piloto['data'])
                            df_hoje_piloto = df_piloto[df_piloto['data'] == pd.to_datetime(hoje)]
                            if não df_hoje_piloto.empty:
                                df_hoje_piloto['piloto'] = piloto
                                df_hoje = pd.concat([df_hoje, df_hoje_piloto])

                    if não df_hoje.empty:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        for piloto em df_hoje['piloto'].unique():
                            df_piloto = df_hoje[df_hoje['piloto'] == piloto]
                            ax.bar(df_piloto['piloto'], df_piloto['hectares'], label=piloto, color=cores.get(piloto, 'blue'))

                        ax.set_title('Total de Hectares Aplicado Hoje')
                        ax.set_ylabel('Total de Hectares')
                        ax.set_xlabel('Piloto')
                        ax.legend(title="Pilotos")

                        for i, v em enumerate(df_hoje['hectares']):
                            ax.text(i, v, round(v, 2), ha='center', va='bottom')

                        st.pyplot(fig)
                    else:
                        st.write("Nenhum dado de aplicação para hoje.")
                else:
                    st.write("Nenhum dado de piloto disponível.")

        # Remover piloto pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Remover Piloto"):
                remove_pilot_username = st.selectbox("Selecione o Piloto para Remover", list(pilotos.keys()), key="remove_pilot_username")
                remove_pilot_button = st.button("Remover Piloto", key="remove_pilot_button")

                if remove_pilot_button:
                    if remove_pilot_username em usuarios:
                        del usuarios[remove_pilot_username]
                        del pilotos[remove_pilot_username]
                        del cores[remove_pilot_username]
                        del fotos[remove_pilot_username]
                        if remove_pilot_username em ajudantes:
                            del ajudantes[remove_pilot_username]
                        for pilot, helper em list(ajudantes.items()):
                            if helper == remove_pilot_username:
                                del ajudantes[pilot]
                        salvar_dados(arquivo_usuarios, usuarios)
                        salvar_dados(arquivo_pilotos, pilotos)
                        salvar_dados(arquivo_cores, cores)
                        salvar_dados(arquivo_fotos, fotos)
                        salvar_dados(arquivo_ajudantes, ajudantes)
                        st.success(f"Piloto {remove_pilot_username} removido com sucesso!")
                    else:
                        st.error("Piloto não encontrado")

        # Remover fazenda pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Remover Fazenda"):
                remove_farm_name = st.selectbox("Selecione a Fazenda para Remover", list(fazendas.keys()), key="remove_farm_name")
                remove_farm_button = st.button("Remover Fazenda", key="remove_farm_button")

                if remove_farm_button:
                    if remove_farm_name em fazendas:
                        del fazendas[remove_farm_name]
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success(f"Fazenda {remove_farm_name} removida com sucesso!")
                    else:
                        st.error("Fazenda não encontrada")

        # Criar backup dos dados
        with st.sidebar.expander("Backup de Dados"):
            if st.button("Criar Backup", key="create_backup_button"):
                criar_backup()
                with open('backup.zip', 'rb') as file:
                    st.download_button(
                        label="Baixar Backup",
                        data=file,
                        file_name="backup.zip",
                        mime="application/zip",
                        key="download_backup_button"
                    )
                    st.success("Backup criado com sucesso!")

        # Recuperar backup dos dados
        with st.sidebar.expander("Recuperar Backup de Dados"):
            backup_upload = st.file_uploader("Escolha um arquivo de backup", type=["zip"], key="backup_upload")
            if backup_upload is not None:
                with open("temp_backup.zip", "wb") as f:
                    f.write(backup_upload.getbuffer())
                recuperar_backup("temp_backup.zip")
                st.success("Backup recuperado com sucesso! Por favor, recarregue a página.")

    # Painel do Piloto e Ajudante
    if 'usuario_logado' em st.session_state and st.session_state['painel'] in ["Piloto", "Ajudante"]:
        st.sidebar.title(f'Painel do {st.session_state["painel"]}')
        st.sidebar.success(f'Logado como {st.session_state["usuario_logado"]}')
        st.write(f'{st.session_state["painel"]} atual: {st.session_state["usuario_logado"]}')

        if st.session_state['painel'] == "Piloto":
            # Entrada de Hectares
            with st.sidebar.expander("Entrada de Hectares"):
                data = st.date_input('Data', key="data_hectares")
                hectares = st.number_input('Hectares', min_value=0.0, format="%.2f", key="hectares_input")
                fazenda = st.selectbox('Fazenda', usuarios[st.session_state['usuario_logado']].get('fazendas', []), key="fazenda_input")
                pasto = st.selectbox('Pasto', list(fazendas[fazenda]['pastos'].keys()) if fazenda in fazendas else [], key="pasto_input")

                if st.button('Adicionar Hectares', key="add_hectares_button"):
                    piloto_atual = st.session_state["usuario_logado"]
                    if piloto_atual and fazenda and pasto:
                        dados_piloto = pilotos[piloto_atual]
                        datas_existentes = [dado['data'] for dado em dados_piloto]
                        if str(data) not in datas_existentes:
                            pilotos[piloto_atual].append({'data': str(data), 'hectares': hectares, 'fazenda': fazenda, 'pasto': pasto})
                            fazendas[fazenda]['pastos'][pasto]['dados_aplicacao'].append({'data': str(data), 'hectares': hectares, 'piloto': piloto_atual})

                            # Registrar hectares para o ajudante
                            ajudante = ajudantes.get(piloto_atual)
                            if ajudante:
                                if ajudante not in pilotos:
                                    pilotos[ajudante] = []
                                pilotos[ajudante].append({'data': str(data), 'hectares': hectares, 'fazenda': fazenda, 'pasto': pasto})

                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_fazendas, fazendas)
                            salvar_dados(arquivo_ajudantes, ajudantes)
                            st.success(f'{hectares} hectares adicionados para {piloto_atual} em {data} na fazenda {fazenda} no pasto {pasto}')
                            st.write(f'{hectares} hectares adicionados para {piloto_atual} em {data} na fazenda {fazenda} no pasto {pasto}')
                        else:
                            st.error('Já existe uma entrada para essa data. Por favor, edite a entrada existente.')
                    else:
                        st.error('Erro ao identificar o piloto, fazenda ou pasto.')

        # Exibir dados do piloto ou ajudante
        st.title(f'Dados do {st.session_state["painel"]}: {st.session_state["usuario_logado"]}')
        foto_piloto = fotos.get(st.session_state["usuario_logado"])
        if foto_piloto and os.path.exists(foto_piloto):
            st.image(foto_piloto, caption="Foto de Perfil", use_column_width=False, width=150)

        dados_usuario = pilotos.get(st.session_state["usuario_logado"], [])

        if dados_usuario:
            df_usuario = pd.DataFrame(dados_usuario)
            st.write(df_usuario)

            hectares_totais = df_usuario['hectares'].sum()
            media_hectares_dia = df_usuario['hectares'].mean()
            total_dias = df_usuario['data'].nunique()

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
            st.write("Nenhum dado disponível para este usuário.")

        # Editar dados de hectares
        if st.session_state['painel'] == "Piloto":
            with st.sidebar.expander("Editar Dados de Hectares"):
                dados_piloto = pilotos.get(st.session_state["usuario_logado"], [])
                if dados_piloto:
                    df_piloto = pd.DataFrame(dados_piloto)
                    if 'fazenda' não em df_piloto.columns:
                        st.error('Nenhum dado de fazenda disponível.')
                    else:
                        selected_date = st.selectbox('Selecione a data para editar', df_piloto['data'], key="edit_selected_date")
                        new_date = st.date_input('Nova data', pd.to_datetime(selected_date), key="edit_new_date")
                        new_hectares = st.number_input('Novo valor de Hectares', min_value=0.0, format="%.2f", key="edit_new_hectares")
                        new_fazenda = st.selectbox('Nova Fazenda', usuarios[st.session_state["usuario_logado"]].get('fazendas', []), index=list(fazendas.keys()).index(df_piloto[df_piloto['data'] == selected_date]['fazenda'].values[0]), key="edit_new_fazenda")
                        new_pasto = st.selectbox('Novo Pasto', list(fazendas[new_fazenda]['pastos'].keys()), index=list(fazendas[new_fazenda]['pastos'].keys()).index(df_piloto[df_piloto['data'] == selected_date]['pasto'].values[0]), key="edit_new_pasto")
                        if st.button('Salvar Alterações', key="save_hectares_changes_button"):
                            for dado em pilotos[st.session_state["usuario_logado"]]:
                                if dado['data'] == selected_date:
                                    dado['data'] = str(new_date)
                                    dado['hectares'] = new_hectares
                                    dado['fazenda'] = new_fazenda
                                    dado['pasto'] = new_pasto
                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success('Dados atualizados com sucesso!')

            # Remover dados de hectares por data
            with st.sidebar.expander("Remover Dados de Hectares"):
                if dados_piloto:
                    df_piloto = pd.DataFrame(dados_piloto)
                    selected_date_remove = st.selectbox('Selecione a data para remover', df_piloto['data'], key="remove_selected_date")
                    if st.button('Remover Dados', key="remove_hectares_button"):
                        pilotos[st.session_state["usuario_logado"]] = [dado for dado em pilotos[st.session_state["usuario_logado"]] if dado['data'] != selected_date_remove]
                        for fazenda em fazendas.values():
                            for pasto em fazenda['pastos'].values():
                                pasto['dados_aplicacao'] = [dado for dado em pasto['dados_aplicacao'] if dado['data'] != selected_date_remove]
                        salvar_dados(arquivo_pilotos, pilotos)
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success('Dados removidos com sucesso!')

            # Alterar nome e senha do piloto
            with st.sidebar.expander("Alterar Nome e Senha"):
                novo_nome = st.text_input('Novo Nome de Usuário', key="new_username")
                nova_senha = st.text_input('Nova Senha', type='password', key="new_password")
                alterar_dados_button = st.button('Alterar Dados', key="change_credentials_button")

                if alterar_dados_button:
                    if novo_nome and nova_senha:
                        if novo_nome não em usuarios or novo_nome == st.session_state["usuario_logado"]:
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
                uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"], key="profile_picture_upload")
                if uploaded_file is not None:
                    bytes_data = uploaded_file.read()
                    foto_path = f'foto_{st.session_state["usuario_logado"]}.png'
                    with open(foto_path, 'wb') as f:
                        f.write(bytes_data)
                    fotos[st.session_state["usuario_logado"]] = foto_path
                    salvar_dados(arquivo_fotos, fotos)
                    st.success('Foto de perfil atualizada com sucesso!')

if __name__ == "__main__":
    main()

import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
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
        zipf.write('ajudantes.json')

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
    arquivo_ajudantes = 'ajudantes.json'

    # Carregar dados do JSON
    pilotos = carregar_dados(arquivo_pilotos)
    cores = carregar_dados(arquivo_cores)
    usuarios = carregar_dados(arquivo_usuarios)
    fotos = carregar_dados(arquivo_fotos)
    safra = carregar_dados(arquivo_safra)
    fazendas = carregar_dados(arquivo_fazendas)
    ajudantes = carregar_dados(arquivo_ajudantes)

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
                new_pilot_username = st.text_input("Nome do Novo Piloto", key="new_pilot_username")
                new_pilot_password = st.text_input("Senha do Novo Piloto", type="password", key="new_pilot_password")
                register_pilot_button = st.button("Cadastrar Piloto", key="register_pilot_button")

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
                            ajudantes[new_pilot_username] = None  # Sem ajudante inicialmente
                            salvar_dados(arquivo_usuarios, usuarios)
                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_cores, cores)
                            salvar_dados(arquivo_fotos, fotos)
                            salvar_dados(arquivo_ajudantes, ajudantes)
                            st.success(f"Piloto {new_pilot_username} cadastrado com sucesso!")
                        else:
                            st.error("Piloto já existe")
                    else:
                        st.error("Por favor, insira um nome de usuário e uma senha")

        # Cadastro de novos ajudantes pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Cadastrar Novo Ajudante"):
                new_ajudante_username = st.text_input("Nome do Novo Ajudante", key="new_ajudante_username")
                new_ajudante_password = st.text_input("Senha do Novo Ajudante", type="password", key="new_ajudante_password")
                register_ajudante_button = st.button("Cadastrar Ajudante", key="register_ajudante_button")

                if register_ajudante_button:
                    if new_ajudante_username and new_ajudante_password:
                        if new_ajudante_username not in usuarios:
                            usuarios[new_ajudante_username] = {
                                'senha': gerar_hash_senha(new_ajudante_password),
                                'tipo': 'Ajudante'
                            }
                            pilotos[new_ajudante_username] = []
                            cores[new_ajudante_username] = '#ff0000'  # Vermelho
                            fotos[new_ajudante_username] = None
                            salvar_dados(arquivo_usuarios, usuarios)
                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_cores, cores)
                            salvar_dados(arquivo_fotos, fotos)
                            st.success(f"Ajudante {new_ajudante_username} cadastrado com sucesso!")
                        else:
                            st.error("Ajudante já existe")
                    else:
                        st.error("Por favor, insira um nome de usuário e uma senha")

        # Cadastro de fazendas e pastos pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Cadastrar Nova Fazenda"):
                new_farm_name = st.text_input("Nome da Nova Fazenda", key="new_farm_name")
                new_farm_link = st.text_input("Link do Google Earth da Fazenda", key="new_farm_link")
                pastos = []
                numero_pastos = st.number_input("Número de Pastos", min_value=1, max_value=20, step=1, key="numero_pastos")
                for i in range(int(numero_pastos)):
                    pasto_name = st.text_input(f"Nome do Pasto {i + 1}", key=f"pasto_name_{i}")
                    pasto_hectares = st.number_input(f"Hectares do Pasto {i + 1}", min_value=0.0, format="%.2f", key=f"pasto_hectares_{i}")
                    pastos.append((pasto_name, pasto_hectares))
                if st.button("Cadastrar Fazenda", key="register_farm_button"):
                    if new_farm_name and new_farm_link and all(pasto[0] and pasto[1] for pasto in pastos):
                        if new_farm_name not in fazendas:
                            fazendas[new_farm_name] = {
                                'link': new_farm_link,
                                'pastos': {pasto[0]: {'tamanho': pasto[1], 'dados_aplicacao': []} for pasto in pastos}
                            }
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Fazenda {new_farm_name} cadastrada com sucesso!")
                        else:
                            st.error("Fazenda já existe")
                    else:
                        st.error("Por favor, insira um nome para a fazenda, link do Google Earth e todos os pastos com seus hectares")

        # Associar pilotos às fazendas
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Associar Piloto à Fazenda"):
                selected_pilot = st.selectbox("Selecione o Piloto", list(usuarios.keys()), key="selected_pilot")
                selected_farm = st.selectbox("Selecione a Fazenda", list(fazendas.keys()), key="selected_farm_association")
                if st.button("Associar Piloto à Fazenda", key="associate_pilot_farm_button"):
                    if selected_pilot and selected_farm:
                        if 'fazendas' not in usuarios[selected_pilot]:
                            usuarios[selected_pilot]['fazendas'] = []
                        if selected_farm not in usuarios[selected_pilot]['fazendas']:
                            usuarios[selected_pilot]['fazendas'].append(selected_farm)
                            salvar_dados(arquivo_usuarios, usuarios)
                            st.success(f"Piloto {selected_pilot} associado à fazenda {selected_farm} com sucesso!")
                        else:
                            st.error("Piloto já está associado a esta fazenda")
                    else:
                        st.error("Por favor, selecione um piloto e uma fazenda")

        # Associar ajudantes aos pilotos
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Associar Ajudante ao Piloto"):
                selected_pilot_for_ajudante = st.selectbox("Selecione o Piloto", list(usuarios.keys()), key="selected_pilot_for_ajudante")
                available_ajudantes = [user for user, data in usuarios.items() if data['tipo'] == 'Ajudante' and user not in ajudantes.values()]
                selected_ajudante = st.selectbox("Selecione o Ajudante", available_ajudantes, key="selected_ajudante")
                if st.button("Associar Ajudante ao Piloto", key="associate_ajudante_pilot_button"):
                    if selected_pilot_for_ajudante and selected_ajudante:
                        ajudantes[selected_pilot_for_ajudante] = selected_ajudante
                        salvar_dados(arquivo_ajudantes, ajudantes)
                        st.success(f"Ajudante {selected_ajudante} associado ao piloto {selected_pilot_for_ajudante} com sucesso!")
                    else:
                        st.error("Por favor, selecione um piloto e um ajudante")

        # Alterar associação de pilotos às fazendas
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Alterar Associação de Pilotos às Fazendas"):
                selected_farm_to_edit_assoc = st.selectbox("Selecione a Fazenda para Editar", list(fazendas.keys()), key="selected_farm_to_edit_assoc")
                if selected_farm_to_edit_assoc:
                    pilotos_associados = [usuario for usuario, dados in usuarios.items() if 'fazendas' in dados and selected_farm_to_edit_assoc in dados['fazendas']]
                    pilotos_nao_associados = [usuario for usuario in usuarios if usuario not in pilotos_associados and usuario != 'admin']
                    piloto_remover = st.selectbox("Selecione o Piloto para Remover da Fazenda", pilotos_associados, key="piloto_remover_assoc")
                    piloto_adicionar = st.selectbox("Selecione o Piloto para Adicionar à Fazenda", pilotos_nao_associados, key="piloto_adicionar_assoc")

                    if st.button("Remover Piloto da Fazenda", key="remove_pilot_from_farm_button_assoc"):
                        if piloto_remover in usuarios and selected_farm_to_edit_assoc in usuarios[piloto_remover]['fazendas']:
                            usuarios[piloto_remover]['fazendas'].remove(selected_farm_to_edit_assoc)
                            salvar_dados(arquivo_usuarios, usuarios)
                            st.success(f"Piloto {piloto_remover} removido da fazenda {selected_farm_to_edit_assoc} com sucesso!")

                    if st.button("Adicionar Piloto à Fazenda", key="add_pilot_to_farm_button_assoc"):
                        if piloto_adicionar in usuarios:
                            if 'fazendas' not in usuarios[piloto_adicionar]:
                                usuarios[piloto_adicionar]['fazendas'] = []
                            if selected_farm_to_edit_assoc not in usuarios[piloto_adicionar]['fazendas']:
                                usuarios[piloto_adicionar]['fazendas'].append(selected_farm_to_edit_assoc)
                                salvar_dados(arquivo_usuarios, usuarios)
                                st.success(f"Piloto {piloto_adicionar} adicionado à fazenda {selected_farm_to_edit_assoc} com sucesso!")
                            else:
                                st.error("Piloto já está associado a esta fazenda")
                        else:
                            st.error("Piloto não encontrado")

        # Alterar fazendas e pastos
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Alterar Fazendas e Pastos"):
                selected_farm_to_edit = st.selectbox("Selecione a Fazenda para Editar", list(fazendas.keys()), key="selected_farm_to_edit")
                if selected_farm_to_edit:
                    farm_data = fazendas[selected_farm_to_edit]
                    new_farm_name = st.text_input("Novo Nome da Fazenda", value=selected_farm_to_edit, key="new_farm_name_edit")
                    new_farm_link = st.text_input("Novo Link do Google Earth da Fazenda", value=farm_data.get('link', ''), key="new_farm_link_edit")
                    if st.button("Renomear Fazenda", key="rename_farm_button"):
                        if new_farm_name:
                            fazendas[new_farm_name] = fazendas.pop(selected_farm_to_edit)
                            fazendas[new_farm_name]['link'] = new_farm_link
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Fazenda renomeada para {new_farm_name}")

                    for pasto in list(fazendas[selected_farm_to_edit]['pastos'].keys()):
                        pasto_data = fazendas[selected_farm_to_edit]['pastos'][pasto]
                        new_pasto_name = st.text_input(f"Novo Nome do Pasto ({pasto})", value=pasto, key=f"new_pasto_name_{pasto}")
                        new_pasto_hectares = st.number_input(f"Novo Tamanho do Pasto ({pasto})", value=pasto_data.get('tamanho', 0.0), min_value=0.0, format="%.2f", key=f"new_pasto_hectares_{pasto}")
                        if st.button(f"Salvar Alterações do Pasto ({pasto})", key=f"save_pasto_changes_button_{pasto}"):
                            if new_pasto_name != pasto:
                                fazendas[selected_farm_to_edit]['pastos'][new_pasto_name] = fazendas[selected_farm_to_edit]['pastos'].pop(pasto)
                            fazendas[selected_farm_to_edit]['pastos'][new_pasto_name]['tamanho'] = new_pasto_hectares
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Pasto {pasto} atualizado com sucesso!")

                    novo_pasto_name = st.text_input("Nome do Novo Pasto", key="new_pasto_name_add")
                    novo_pasto_hectares = st.number_input("Tamanho do Novo Pasto (hectares)", min_value=0.0, format="%.2f", key="new_pasto_hectares_add")
                    if st.button("Adicionar Novo Pasto", key="add_new_pasto_button"):
                        if novo_pasto_name and novo_pasto_hectares:
                            if novo_pasto_name not in fazendas[selected_farm_to_edit]['pastos']:
                                fazendas[selected_farm_to_edit]['pastos'][novo_pasto_name] = {'tamanho': novo_pasto_hectares, 'dados_aplicacao': []}
                                salvar_dados(arquivo_fazendas, fazendas)
                                st.success(f"Pasto {novo_pasto_name} adicionado com sucesso!")
                            else:
                                st.error("Pasto já existe")

                    pasto_to_remove = st.selectbox("Selecione o Pasto para Remover", list(fazendas[selected_farm_to_edit]['pastos'].keys()), key="pasto_to_remove")
                    if st.button("Remover Pasto", key="remove_pasto_button"):
                        if pasto_to_remove in fazendas[selected_farm_to_edit]['pastos']:
                            del fazendas[selected_farm_to_edit]['pastos'][pasto_to_remove]
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success(f"Pasto {pasto_to_remove} removido com sucesso!")

        # Painel do Administrador
        if st.session_state['painel'] == "Administrador":
            st.title("Painel do Administrador")

            # Mostrar lista de pilotos e ajudantes
            with st.expander("Lista de Pilotos e Ajudantes"):
                st.subheader("Pilotos")
                for piloto in [user for user, data in usuarios.items() if data['tipo'] == 'Piloto']:
                    if st.checkbox(piloto, key=f"checkbox_piloto_{piloto}"):
                        st.write(f"**Fazendas Associadas:** {', '.join(usuarios[piloto].get('fazendas', []))}")
                        st.write(f"**Ajudante:** {ajudantes.get(piloto, 'Nenhum ajudante associado')}")

                        if piloto in pilotos:
                            df_piloto = pd.DataFrame(pilotos[piloto])
                            if not df_piloto.empty:
                                st.write("**Dados de Aplicações:**")
                                st.write(df_piloto)
                            else:
                                st.write("Nenhum dado de aplicação disponível.")

                st.subheader("Ajudantes")
                for ajudante in [user for user, data in usuarios.items() if data['tipo'] == 'Ajudante']:
                    if st.checkbox(ajudante, key=f"checkbox_ajudante_{ajudante}"):
                        st.write("**Dados de Aplicações:**")
                        if ajudante in pilotos:
                            df_ajudante = pd.DataFrame(pilotos[ajudante])
                            if not df_ajudante.empty:
                                st.write(df_ajudante)
                            else:
                                st.write("Nenhum dado de aplicação disponível.")
                        else:
                            st.write("Nenhum dado de aplicação disponível.")

            # Mostrar dados organizados por fazenda e piloto
            with st.expander("Lista de Fazendas"):
                if fazendas:
                    for fazenda, dados_fazenda in fazendas.items():
                        total_hectares_fazenda = sum(pasto['tamanho'] for pasto in dados_fazenda['pastos'].values())
                        if st.checkbox(f"{fazenda} ({total_hectares_fazenda} hectares)", key=f"checkbox_{fazenda}"):
                            # Link do Google Earth para a fazenda
                            fazenda_link = dados_fazenda.get('link', '')
                            st.markdown(f"[Ver Fazenda no Google Earth]({fazenda_link})", unsafe_allow_html=True)

                            for pasto, dados_pasto in dados_fazenda['pastos'].items():
                                with st.expander(f"Pasto: {pasto} ({dados_pasto['tamanho']} hectares)"):
                                    if dados_pasto['dados_aplicacao']:
                                        df_pasto = pd.DataFrame(dados_pasto['dados_aplicacao'])
                                        st.write(df_pasto)
                                    else:
                                        st.write("Nenhuma aplicação registrada para este pasto.")
            
            # Modificar cores dos pilotos
            with st.sidebar.expander("Modificar Cores dos Pilotos"):
                for piloto in pilotos:
                    nova_cor = st.color_picker(f"Cor do {piloto}", value=cores.get(piloto, '#00ff00'), key=f"color_picker_{piloto}")
                    cores[piloto] = nova_cor
                salvar_dados(arquivo_cores, cores)

            # Exibir gráficos de dados de todos os pilotos
            with st.expander('Dados de Todos os Pilotos'):
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
                        logo_upload = st.file_uploader("Carregar nova logomarca para o gráfico", type=["png", "jpg", "jpeg"], key="logo_upload")
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
                            st.download_button(label="Baixar Gráfico", data=buf_final, file_name="grafico_com_logomarca.png", mime="image/png", key="download_graphic_button")
                        else:
                            buf = salvar_grafico(fig)
                            st.download_button(label="Baixar Gráfico", data=buf, file_name="grafico.png", mime="image/png", key="download_graphic_button_no_logo")

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
                
                else:
                    st.write("Nenhum dado de piloto disponível.")

                # Visualização diária por piloto
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

        # Remover piloto pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Remover Piloto"):
                remove_pilot_username = st.selectbox("Selecione o Piloto para Remover", list(pilotos.keys()), key="remove_pilot_username")
                remove_pilot_button = st.button("Remover Piloto", key="remove_pilot_button")

                if remove_pilot_button:
                    if remove_pilot_username in usuarios:
                        del usuarios[remove_pilot_username]
                        del pilotos[remove_pilot_username]
                        del cores[remove_pilot_username]
                        del fotos[remove_pilot_username]
                        if remove_pilot_username in ajudantes:
                            del ajudantes[remove_pilot_username]
                        for pilot, helper in list(ajudantes.items()):
                            if helper == remove_pilot_username:
                                del ajudantes[pilot]
                        salvar_dados(arquivo_usuarios, usuarios)
                        salvar_dados(arquivo_pilotos, pilotos)
                        salvar_dados(arquivo_cores, cores)
                        salvar_dados(arquivo_fotos, fotos)
                        salvar_dados(arquivo_ajudantes, ajudantes)
                        st.success(f"Piloto {remove_pilot_username} removido com sucesso!")
                    else:
                        st.error("Piloto não encontrado")

        # Remover fazenda pelo administrador
        if st.session_state['painel'] == "Administrador":
            with st.sidebar.expander("Remover Fazenda"):
                remove_farm_name = st.selectbox("Selecione a Fazenda para Remover", list(fazendas.keys()), key="remove_farm_name")
                remove_farm_button = st.button("Remover Fazenda", key="remove_farm_button")

                if remove_farm_button:
                    if remove_farm_name in fazendas:
                        del fazendas[remove_farm_name]
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success(f"Fazenda {remove_farm_name} removida com sucesso!")
                    else:
                        st.error("Fazenda não encontrada")

        # Criar backup dos dados
        with st.sidebar.expander("Backup de Dados"):
            if st.button("Criar Backup", key="create_backup_button"):
                criar_backup()
                with open('backup.zip', 'rb') as file:
                    st.download_button(
                        label="Baixar Backup",
                        data=file,
                        file_name="backup.zip",
                        mime="application/zip",
                        key="download_backup_button"
                    )
                    st.success("Backup criado com sucesso!")

        # Recuperar backup dos dados
        with st.sidebar.expander("Recuperar Backup de Dados"):
            backup_upload = st.file_uploader("Escolha um arquivo de backup", type=["zip"], key="backup_upload")
            if backup_upload is not None:
                with open("temp_backup.zip", "wb") as f:
                    f.write(backup_upload.getbuffer())
                recuperar_backup("temp_backup.zip")
                st.success("Backup recuperado com sucesso! Por favor, recarregue a página.")

    # Painel do Piloto e Ajudante
    if 'usuario_logado' in st.session_state and st.session_state['painel'] in ["Piloto", "Ajudante"]:
        st.sidebar.title(f'Painel do {st.session_state["painel"]}')
        st.sidebar.success(f'Logado como {st.session_state["usuario_logado"]}')
        st.write(f'{st.session_state["painel"]} atual: {st.session_state["usuario_logado"]}')

        if st.session_state['painel'] == "Piloto":
            # Entrada de Hectares
            with st.sidebar.expander("Entrada de Hectares"):
                data = st.date_input('Data', key="data_hectares")
                hectares = st.number_input('Hectares', min_value=0.0, format="%.2f", key="hectares_input")
                fazenda = st.selectbox('Fazenda', usuarios[st.session_state['usuario_logado']].get('fazendas', []), key="fazenda_input")
                pasto = st.selectbox('Pasto', list(fazendas[fazenda]['pastos'].keys()) if fazenda in fazendas else [], key="pasto_input")

                if st.button('Adicionar Hectares', key="add_hectares_button"):
                    piloto_atual = st.session_state["usuario_logado"]
                    if piloto_atual and fazenda and pasto:
                        dados_piloto = pilotos[piloto_atual]
                        datas_existentes = [dado['data'] for dado in dados_piloto]
                        if str(data) not in datas_existentes:
                            pilotos[piloto_atual].append({'data': str(data), 'hectares': hectares, 'fazenda': fazenda, 'pasto': pasto})
                            fazendas[fazenda]['pastos'][pasto]['dados_aplicacao'].append({'data': str(data), 'hectares': hectares, 'piloto': piloto_atual})

                            # Registrar hectares para o ajudante
                            ajudante = ajudantes.get(piloto_atual)
                            if ajudante:
                                if ajudante not in pilotos:
                                    pilotos[ajudante] = []
                                pilotos[ajudante].append({'data': str(data), 'hectares': hectares, 'fazenda': fazenda, 'pasto': pasto})

                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_fazendas, fazendas)
                            salvar_dados(arquivo_ajudantes, ajudantes)
                            st.success(f'{hectares} hectares adicionados para {piloto_atual} em {data} na fazenda {fazenda} no pasto {pasto}')
                            st.write(f'{hectares} hectares adicionados para {piloto_atual} em {data} na fazenda {fazenda} no pasto {pasto}')
                        else:
                            st.error('Já existe uma entrada para essa data. Por favor, edite a entrada existente.')
                    else:
                        st.error('Erro ao identificar o piloto, fazenda ou pasto.')

        # Exibir dados do piloto ou ajudante
        st.title(f'Dados do {st.session_state["painel"]}: {st.session_state["usuario_logado"]}')
        foto_piloto = fotos.get(st.session_state["usuario_logado"])
        if foto_piloto and os.path.exists(foto_piloto):
            st.image(foto_piloto, caption="Foto de Perfil", use_column_width=False, width=150)

        dados_usuario = pilotos.get(st.session_state["usuario_logado"], [])

        if dados_usuario:
            df_usuario = pd.DataFrame(dados_usuario)
            st.write(df_usuario)

            hectares_totais = df_usuario['hectares'].sum()
            media_hectares_dia = df_usuario['hectares'].mean()
            total_dias = df_usuario['data'].nunique()

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
            st.write("Nenhum dado disponível para este usuário.")

        # Editar dados de hectares
        if st.session_state['painel'] == "Piloto":
            with st.sidebar.expander("Editar Dados de Hectares"):
                dados_piloto = pilotos.get(st.session_state["usuario_logado"], [])
                if dados_piloto:
                    df_piloto = pd.DataFrame(dados_piloto)
                    if 'fazenda' not in df_piloto.columns:
                        st.error('Nenhum dado de fazenda disponível.')
                    else:
                        selected_date = st.selectbox('Selecione a data para editar', df_piloto['data'], key="edit_selected_date")
                        new_date = st.date_input('Nova data', pd.to_datetime(selected_date), key="edit_new_date")
                        new_hectares = st.number_input('Novo valor de Hectares', min_value=0.0, format="%.2f", key="edit_new_hectares")
                        new_fazenda = st.selectbox('Nova Fazenda', usuarios[st.session_state["usuario_logado"]].get('fazendas', []), index=list(fazendas.keys()).index(df_piloto[df_piloto['data'] == selected_date]['fazenda'].values[0]), key="edit_new_fazenda")
                        new_pasto = st.selectbox('Novo Pasto', list(fazendas[new_fazenda]['pastos'].keys()), index=list(fazendas[new_fazenda]['pastos'].keys()).index(df_piloto[df_piloto['data'] == selected_date]['pasto'].values[0]), key="edit_new_pasto")
                        if st.button('Salvar Alterações', key="save_hectares_changes_button"):
                            for dado in pilotos[st.session_state["usuario_logado"]]:
                                if dado['data'] == selected_date:
                                    dado['data'] = str(new_date)
                                    dado['hectares'] = new_hectares
                                    dado['fazenda'] = new_fazenda
                                    dado['pasto'] = new_pasto
                            salvar_dados(arquivo_pilotos, pilotos)
                            salvar_dados(arquivo_fazendas, fazendas)
                            st.success('Dados atualizados com sucesso!')

            # Remover dados de hectares por data
            with st.sidebar.expander("Remover Dados de Hectares"):
                if dados_piloto:
                    df_piloto = pd.DataFrame(dados_piloto)
                    selected_date_remove = st.selectbox('Selecione a data para remover', df_piloto['data'], key="remove_selected_date")
                    if st.button('Remover Dados', key="remove_hectares_button"):
                        pilotos[st.session_state["usuario_logado"]] = [dado for dado in pilotos[st.session_state["usuario_logado"]] if dado['data'] != selected_date_remove]
                        for fazenda in fazendas.values():
                            for pasto in fazenda['pastos'].values():
                                pasto['dados_aplicacao'] = [dado for dado in pasto['dados_aplicacao'] if dado['data'] != selected_date_remove]
                        salvar_dados(arquivo_pilotos, pilotos)
                        salvar_dados(arquivo_fazendas, fazendas)
                        st.success('Dados removidos com sucesso!')

            # Alterar nome e senha do piloto
            with st.sidebar.expander("Alterar Nome e Senha"):
                novo_nome = st.text_input('Novo Nome de Usuário', key="new_username")
                nova_senha = st.text_input('Nova Senha', type='password', key="new_password")
                alterar_dados_button = st.button('Alterar Dados', key="change_credentials_button")

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
                uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg"], key="profile_picture_upload")
                if uploaded_file is not None:
                    bytes_data = uploaded_file.read()
                    foto_path = f'foto_{st.session_state["usuario_logado"]}.png'
                    with open(foto_path, 'wb') as f:
                        f.write(bytes_data)
                    fotos[st.session_state["usuario_logado"]] = foto_path
                    salvar_dados(arquivo_fotos, fotos)
                    st.success('Foto de perfil atualizada com sucesso!')

if __name__ == "__main__":
    main()
