import streamlit as st
import requests
import pandas as pd
import altair as alt

# Configuração da URL do backend Flask
URL_BACKEND = "http://localhost:5000"

# Funções para interação com o backend
def obter_dispositivos():
    try:
        resposta = requests.get(f"{URL_BACKEND}/devices")
        if resposta.status_code == 200:
            return resposta.json()
        return []
    except requests.exceptions.RequestException:
        st.error("Não foi possível conectar ao servidor backend")
        return []

def adicionar_dispositivo(ip, nome, taxa_trafego):
    dados = {
        "ip": ip,
        "name": nome,
        "traffic_rate": float(taxa_trafego)
    }
    try:
        resposta = requests.post(f"{URL_BACKEND}/devices", json=dados)
        return resposta.status_code == 201
    except requests.exceptions.RequestException:
        st.error("Erro ao adicionar dispositivo")
        return False

def remover_dispositivo(id_dispositivo):
    try:
        resposta = requests.delete(f"{URL_BACKEND}/devices/{id_dispositivo}")
        return resposta.status_code == 200
    except requests.exceptions.RequestException:
        st.error("Erro ao remover dispositivo")
        return False

# Função para determinar o status do tráfego
def obter_status_trafego(taxa_trafego):
    if taxa_trafego > 60:
        return "Alto"
    elif taxa_trafego > 30:
        return "Moderado"
    return "Normal"

def limpar_formulario():
    st.session_state["ip"] = ""
    st.session_state["nome"] = ""
    st.session_state["taxa_trafego"] = 0.0
    st.session_state["dispositivos"] = obter_dispositivos()

# Interface do Streamlit
st.title("Monitoramento de Tráfego de Rede")

# Seção de registro de novo dispositivo
st.header("Registro de Dispositivo")
with st.form("formulario_dispositivo"):
    st.text_input("Endereço IP", placeholder="192.168.1.1", key="ip")
    st.text_input("Nome do Dispositivo", placeholder="Servidor A", key="nome")
    st.number_input("Taxa de Tráfego (Mbps)", step=0.5, key="taxa_trafego")
    ip = st.session_state.get("ip", "")
    nome = st.session_state.get("nome", "")
    taxa_trafego = st.session_state.get("taxa_trafego", 0.0)
    col1, col2 = st.columns(2)
    with col1:
        enviado = st.form_submit_button("Registrar")
    with col2:
        limpar = st.form_submit_button("Limpar Campos", on_click=limpar_formulario)

if enviado:
    dispositivos_existentes = obter_dispositivos()
    if ip and nome and taxa_trafego is not None:
        # Verifica se o IP é válido
        if not ip.count('.') == 3 or not all(0 <= int(parte) < 256 for parte in ip.split('.')):
            st.error("Endereço IP inválido")
        # Verifica se a taxa de tráfego é válida
        elif taxa_trafego < 0:
            st.error("Taxa de tráfego deve ser maior ou igual a 0")
        # Verifica se o dispositivo já existe
        elif any(d["ip"] == ip for d in dispositivos_existentes):
            st.error("Dispositivo já registrado")
        elif any(n["name"] == nome for n in dispositivos_existentes):
            st.error("Nome do dispositivo já registrado")
        # Se tudo estiver correto, adiciona o dispositivo
        else:
            if adicionar_dispositivo(ip, nome, taxa_trafego):
                st.success("Dispositivo registrado com sucesso!")
                st.session_state["dispositivos"] = obter_dispositivos()
                st.rerun()
            else:
                st.error("Falha ao registrar dispositivo")
    else:
        st.warning("Preencha todos os campos")

# Carregar dispositivos na sessão, se necessário
if "dispositivos" not in st.session_state:
    st.session_state["dispositivos"] = obter_dispositivos()

dispositivos = st.session_state["dispositivos"]

# Monta os dados para exibição na tabela e no gráfico
dados_df = []
for dispositivo in dispositivos:
    dados_df.append({
        "ID": dispositivo["id"],
        "Endereço IP": dispositivo["ip"],
        "Nome": dispositivo["name"],
        "Taxa de Tráfego (Mbps)": dispositivo["traffic_rate"],
        "Status": obter_status_trafego(dispositivo["traffic_rate"])  # Determina o status do tráfego
    })

df = pd.DataFrame(dados_df)

# Gráfico de tráfego
st.subheader("Visualização do Tráfego")

# Filtrar dados válidos (taxa >= 0)
if "Taxa de Tráfego (Mbps)" in df.columns and not df.empty:
    df_valido = df[df["Taxa de Tráfego (Mbps)"] > 0]
else:
    df_valido = pd.DataFrame()  # ou trate de outra forma


if not df_valido.empty:
    dados_grafico = df_valido[["Nome", "Taxa de Tráfego (Mbps)"]]

    # Adiciona uma coluna com a cor baseada na taxa
    def obter_cor(taxa):
        if taxa > 60:
            return "red"
        elif taxa > 30:
            return "yellow"
        else:
            return "green"

    dados_grafico["Cor"] = dados_grafico["Taxa de Tráfego (Mbps)"].apply(obter_cor)

    # Criar gráfico com Altair
    grafico = alt.Chart(dados_grafico).mark_bar().encode(
        x=alt.X("Nome:N", title="Dispositivo"),
        y=alt.Y("Taxa de Tráfego (Mbps):Q"),
        color=alt.Color("Cor:N", scale=None),
        tooltip=["Nome", "Taxa de Tráfego (Mbps)"]
    ).properties(height=400).interactive()

    st.altair_chart(grafico, use_container_width=True)
else:
    st.info("Nenhum dado de tráfego disponível para exibir no gráfico.")


if not df.empty:
    # Tabela de dispositivos registrados
    st.header("Dispositivos Registrados")

    # Cabeçalho da tabela
    colunas_cabecalho = st.columns([2, 2, 2, 2, 2])
    colunas_cabecalho[0].markdown("**Endereço IP**")
    colunas_cabecalho[1].markdown("**Nome**")
    colunas_cabecalho[2].markdown("**Tráfego (Mbps)**")
    colunas_cabecalho[3].markdown("**Status**")
    colunas_cabecalho[4].markdown("**Ação**")
    for indice, linha in df.iterrows():
        colunas = st.columns([2, 2, 2, 2, 2])
        colunas[0].write(linha["Endereço IP"])
        colunas[1].write(linha["Nome"])
        colunas[2].write(f"{linha['Taxa de Tráfego (Mbps)']:.1f}")
        
        # Exibe o status com cores diferentes
        status = linha["Status"]
        if status == "Alto":
            colunas[3].error(status)
        elif status == "Moderado":
            colunas[3].warning(status)
        else:
            colunas[3].success(status)
        
        # Botão para remover dispositivo
        if colunas[4].button("Remover", key=f"remover_{linha['ID']}"):
            if remover_dispositivo(linha["ID"]):
                st.success(f"Dispositivo {linha['Nome']} removido com sucesso!")
                st.session_state["dispositivos"] = obter_dispositivos()
                st.rerun()
            else:
                st.error("Falha ao remover dispositivo")
else:
    st.info("Nenhum dispositivo registrado ainda.")
