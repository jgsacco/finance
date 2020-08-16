import pandas as pd
import datetime as dt
import pandas_datareader.data as web


def criar_tabela_precos(stocks, dia_atual, database):
    precos = pd.DataFrame()

    for stock in stocks:
        stock_price = pd.DataFrame([database[stock].iloc[dia_atual, 2], database[stock].iloc[dia_atual, 3]])
        precos = pd.concat([precos, stock_price], axis=1)

    precos.index = ["Open", "Close"]
    precos.columns = stocks
    precos = precos.transpose()
    precos['percent_change'] = (precos['Close'] - precos['Open']) / precos['Open'] + 1

    return precos


def criar_portfolio_inicial(stocks, n, dia_atual, database):
    print(dia_atual)
    base = criar_tabela_precos(stocks, dia_atual, database)
    base.sort_values(inplace=True, axis=0, by='percent_change', ascending=False)
    portfolio = base.head(n)
    return portfolio


def melhores_perfomances(portfolio, dia_atual, n, database):
    stocks = portfolio.index
    performance = criar_tabela_precos(stocks, dia_atual, database)
    performance.sort_values(inplace=True, axis=0, by='percent_change', ascending=False)
    melhores = performance.head(n)
    return melhores


def redistribuir_carteira(carteira, stock_num_change, stock_num_stay):
    total = 0
    for i in range(stock_num_change):
        local = i + stock_num_stay
        total += carteira[local]
    new_amount = total / stock_num_change
    for i in range(stock_num_change):
        local = i + stock_num_stay
        carteira[local] = new_amount
    return carteira


def atualizar_precos(portfolio, dia_atual, database):
    selecionados = portfolio.index.to_list()
    tabela_inter = criar_tabela_precos(selecionados, dia_atual, database)
    portfolio['Open'] = tabela_inter['Open']
    portfolio['Close'] = tabela_inter['Close']
    portfolio['percent_change'] = tabela_inter['percent_change']

    return portfolio


def create_initial_database(stocks, start_date, final_date):
    database = {}
    for stock in stocks:
        print(stock)
        database[stock] = (web.DataReader(stock, 'yahoo', start_date, final_date))
    return database


def main():
    portfolio_size = 10
    tickers = pd.read_excel('nasdaq.xlsx')
    stocks = tickers['Ticker'].to_list()
    #  stocks = ["MSFT", "AAPL", "AAL", "HSY", "DIS", "PBR", "FB"]
    stock_num_change = 1
    stock_num_stay = portfolio_size - stock_num_change
    start_date = dt.date(2019, 1, 1)
    final_date = dt.date(2019, 12, 31)

    database = create_initial_database(stocks, start_date, final_date)
    portfolio = criar_portfolio_inicial(stocks, portfolio_size, 0, database)  # portfólio inicial criado a partir dos
    # dados
    # do primeiro dia
    alocado = []  # criação da carteira de investimentos que alocará o dinheiro
    for k in range(portfolio_size):
        alocado.append(1)
    portfolio['Investido'] = alocado
    dias = 251
    i = 1

    while i < dias:
        selecionados = portfolio.index.to_list()  # começando a extrair as ações do portfólio anterior
        portfolio = atualizar_precos(portfolio, i, database)  # mantém a ordem anterior de ações mas atualiza os
        # crescimentos
        portfolio.sort_values(inplace=True, ascending=False, axis=0, by='percent_change')  # coloca as linhas em
        # ordem decrescente de crescimento
        alocado = portfolio['Investido'].to_list()
        alocado = redistribuir_carteira(alocado, stock_num_change, stock_num_stay)
        portfolio_changes = portfolio.loc[:, 'percent_change'].to_list()
        for j in range(portfolio_size):
            alocado[j] = alocado[j] * portfolio_changes[j]
        de_fora = []
        for this_one in stocks:
            is_there = False
            for j in range(len(selecionados)):
                if this_one == selecionados[j]:
                    is_there = True
            if not is_there:
                de_fora.append(this_one)
        stay = melhores_perfomances(portfolio, i, stock_num_stay, database)
        fora_precos = criar_tabela_precos(de_fora, i, database)
        best_two = melhores_perfomances(fora_precos, i, stock_num_change, database)
        portfolio = pd.concat([stay, best_two])
        portfolio['Investido'] = alocado
        i += 1
    resultado_final = 0
    alocado = portfolio['Investido'].to_list()
    for i in range(portfolio_size):
        resultado_final += alocado[i]
    resultado_final = ((resultado_final - portfolio_size) / portfolio_size) * 100
    print(resultado_final)


main()
