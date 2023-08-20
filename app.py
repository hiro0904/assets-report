# 環境構築
import pandas as pd
import yfinance as yf
from datetime import timedelta, datetime
import streamlit as st
import pytz

# csvファイル読み込み
def read_csv(filename):
    data = pd.read_csv(filename)
    return data


def convert_usd_to_jpy(amount_usd):
    # USD/JPYの為替レートを取得
    ticker = yf.Ticker("USDJPY=X")  # Yahoo FinanceでのUSD/JPYのティッカーシンボル
    exchange_rate = ticker.history(period="1d")["Close"][0]

    # ドルを円に変換
    amount_jpy = amount_usd * exchange_rate
    return amount_jpy


# 利益を計算する
def calculate_closing_price(ticker, purchase_price, quantity):
    end_date = pd.Timestamp.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=1)

    ticker_data = yf.download(ticker, start=start_date, end=end_date)
    if ticker_data.empty:
        st.write(f"No data found for {ticker} on {start_date}.")
        return None

    closing_price = ticker_data["Close"].iloc[0]

    return closing_price


def calculate_profit_rate(ticker, purchase_price):
    end_date = pd.Timestamp.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=1)

    ticker_data = yf.download(ticker, start=start_date, end=end_date)
    if ticker_data.empty:
        st.write(f"No data found for {ticker} on {start_date}.")
        return None

    closing_price = ticker_data["Close"].iloc[0]
    profit_rate = ((closing_price / purchase_price) - 1) * 100

    return profit_rate


def get_annual_dividends(ticker, quantity):
    end_date = datetime.now(pytz.utc).date() - timedelta(days=1)
    start_date = end_date.replace(year=end_date.year - 1)
    dividends = yf.Ticker(ticker).dividends.loc[start_date:end_date]
    # st.write(dividends)
    annual_dividend = sum(dividends.values)
    return annual_dividend


# ドルから円にする


def main():
    st.title("フォートポリオ分析")

    output_data = {
        "ticker": [],
        "getPrice": [],
        "quantity": [],
        "nowPrice": [],
        "assetValue": [],
        "profit": [],
        "profitRatio": [],
        "annualDividend": [],
        "dividendYield": [],
    }
    uploaded_file = st.file_uploader("CSVファイルを選択してください", type=["csv"])

    if uploaded_file is not None:
        # CSVファイルをDataFrameとして読み込む
        data = pd.read_csv(uploaded_file)

    st.warning("ticker,getPrice,quantity の要素のみのcsvファイルを用意して下さい")
    st.header("損益状況を表示します")
    for index, row in data.iterrows():
        ticker = row["ticker"]
        purchase_price = row["getPrice"]
        quantity = row["quantity"]
        closing_price = calculate_closing_price(ticker, purchase_price, quantity)
        assertValue = purchase_price * quantity
        profit = profit = (closing_price - purchase_price) * quantity
        profit_rate = calculate_profit_rate(ticker, purchase_price)
        # output用に記入
        output_data["ticker"].append(ticker)
        output_data["getPrice"].append(purchase_price)
        output_data["quantity"].append(quantity)
        output_data["nowPrice"].append(closing_price)
        output_data["assetValue"].append(assertValue)
        output_data["profit"].append(profit)
        output_data["profitRatio"].append(profit_rate)
        profitJPY = convert_usd_to_jpy(profit)
        if profit is not None:
            st.subheader(
                f"Ticker: {ticker}  Profit: {profit:.2f} USD ({profitJPY:.2f}YN)   ratio {profit_rate:.2f}"
            )

    st.header("直近1年間の配当金を表示します")
    for index, row in data.iterrows():
        ticker = row["ticker"]
        purchase_price = row["getPrice"]
        quantity = row["quantity"]
        oneDividend = get_annual_dividends(ticker, quantity)
        annual_dividend = oneDividend * quantity
        dividend_yield = (oneDividend / purchase_price) * 100
        # output用に記入
        output_data["annualDividend"].append(annual_dividend)
        output_data["dividendYield"].append(dividend_yield)

        if profit is not None:
            st.subheader(
                f"Ticker: {ticker} Annual Dividend {annual_dividend:.2f} dividendYield {dividend_yield:.2f}%"
            )
    df = pd.DataFrame(output_data)

    sumProfit = sum(output_data["profit"])
    sumProfitJPY = convert_usd_to_jpy(sumProfit)
    sumProfitRatio = (sum(output_data["profit"]) / sum(output_data["assetValue"])) * 100
    sumDividend = sum(output_data["annualDividend"])
    sumDividendJPY = convert_usd_to_jpy(sumDividend)
    sumDividendYield = (sumDividend / sum(output_data["assetValue"])) * 100
    st.header(f"sum  profit {sumProfit:.2f} ({sumProfitJPY:.2f}YN) %")
    st.header(f"ProfitRatio {sumProfitRatio:.2f}%")
    st.header(f"Dividends {sumDividend} ({sumDividendJPY:.2f}YN) %")
    st.header(f"DividendYield{sumDividendYield:.2f} %")

    # DataFrameをCSVファイルに書き込む
    if st.button("Download CSV"):
        csv_filename = "outputData.csv"
        df.to_csv(csv_filename, index=False)
        st.download_button(
            label="Download CSV file",
            data=df.to_csv().encode("utf-8"),
            file_name=csv_filename,
            mime="text/csv",
        )


if __name__ == "__main__":
    main()

