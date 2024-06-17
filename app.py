                total_dias = df_total.groupby('piloto')['data'].count()
                axs[2].bar(total_dias.index, total_dias.values, color=[cores[piloto] for piloto in total_dias.index])
                axs[2].set_title('Total de Dias de Aplicação')
                axs[2].set_ylabel('Total de Dias')
                for i, v in enumerate(total_dias.values):
                    axs[2].text(i, v, round(v, 2), ha='center', va='bottom')

                for ax in axs:
                    ax.set_xlabel('Pilotos')
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

                fig.tight_layout()
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
                pilotos[piloto_atual].append({'data': str(data), 'hectares': hectares})
                salvar_dados(arquivo_pilotos, pilotos)
                st.sidebar.success(f'{hectares} hectares adicionados para {piloto_atual} em {data}')
                st.write(f'{hectares} hectares adicionados para {piloto_atual} em {data}')
            else:
                st.sidebar.error('Erro ao identificar o piloto.')

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
            st.image(foto_piloto, caption="Foto de Perfil", use_column_width=True)

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
        else:
            st.write("Nenhum dado disponível para este piloto.")

if __name__ == "__main__":
    main()
