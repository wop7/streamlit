import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

st.title("Análise do Dataset")
st.write("Bem-vindo ao Streamlit!")

# Carregar dados de tickers
acao_brasil = pd.read_csv('statusinvest-busca-avancada-acao.csv', sep=';')

# Função para baixar os dados históricos com barra de progresso
def baixar_dados(tickers):
    dados_historicos = {}
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, ticker in enumerate(tickers):
        status_text.text(f"Processando ações: {ticker} ({idx + 1}/{len(tickers)})")
        acao = yf.Ticker(ticker + '.SA')

        # Dados históricos dos últimos 5 anos
        historico = acao.history(period="5y")
        historico["Ticker"] = ticker  # Adicionar o ticker como coluna
        dados_historicos[ticker] = historico

        # Atualizar barra de progresso
        progress_bar.progress((idx + 1) / len(tickers))

    status_text.text("Processamento concluído!")
    progress_bar.empty()

    # Converter os dados históricos em um único DataFrame
    data = pd.concat(dados_historicos.values())
    data = data.reset_index()
    data.rename(columns={"index": "Date"}, inplace=True)
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    return data

# Variável para armazenar os dados baixados
if "dados_historicos" not in st.session_state:
    st.session_state["dados_historicos"] = None

# Botão para baixar os dados
if st.button("Baixar Cotações"):
    with st.spinner("Baixando dados, por favor aguarde..."):
        tickers = acao_brasil['TICKER'].unique()[:5]
        st.session_state["dados_historicos"] = baixar_dados(tickers)
    st.success("Download concluído!")

# Exibir os dados e gráficos, se disponíveis
if st.session_state["dados_historicos"] is not None:
    data = st.session_state["dados_historicos"]
    
    # Filtro por ticker
    tickers_disponiveis = data["Ticker"].unique()
    ticker_selecionado = st.selectbox("Selecione o ticker:", options=tickers_disponiveis)
    dados_filtrados = data[data["Ticker"] == ticker_selecionado]

    st.write(f"Mostrando dados para o ticker: {ticker_selecionado}")
    st.dataframe(dados_filtrados)

    # Gráfico de linha para o fechamento ajustado
    fig, ax = plt.subplots()
    dtf = data[data['Ticker'] == ticker_selecionado]

    # Criando uma nova coluna para o ano e o mês
    dtf['YearMonth'] = dtf['Date'].dt.to_period('M')

    # Calculando a média mensal do valor de fechamento ajustado
    dtf_monthly = dtf.groupby('YearMonth')['Close'].mean().reset_index()
    dtf_monthly['YearMonth'] = dtf_monthly['YearMonth'].dt.to_timestamp()

    # Dividindo os valores de Close por 1000
    dtf_monthly['Close'] = dtf_monthly['Close'] / 1000

    # Criando o gráfico
    fig, ax = plt.subplots()
    dtf_monthly.plot(x="YearMonth", y="Close", ax=ax, title="Média Mensal do Preço de Fechamento - " + ticker_selecionado)
    ax.set_xlabel("Mês")
    ax.set_ylabel("Preço Médio de Fechamento (em Milhares)")
    st.pyplot(fig)
else:
    st.warning("Clique no botão acima para baixar os dados!")
