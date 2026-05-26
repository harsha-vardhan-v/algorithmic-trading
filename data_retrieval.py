import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from kiteconnect import KiteConnect

load_dotenv()
api_key = os.getenv("KITE_API_KEY")
access_token = os.getenv("KITE_ACCESS_TOKEN")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

def get_instument_token(symbol="CRUDEOILM", exchange="MCX"):
    # Download the complete dynamic instrument dump
    df_instruments = pd.DataFrame(kite.instruments(exchange))
    
    # Filter for Instrument symbol
    instrument = df_instruments[
        (df_instruments['name'] == symbol) & 
        (df_instruments['instrument_type'] == 'FUT')
    ].copy()

    if instrument.empty:
        raise ValueError(f"No active {symbol} contracts found on {exchange}.")

    # Sort by nearest expiry date to target the current-month contract
    instrument['expiry'] = pd.to_datetime(instrument['expiry'])
    instrument = instrument.sort_values(by='expiry').reset_index(drop=True)
    
    # Extract the token and trading symbol
    target_token = int(instrument.loc[0, 'instrument_token'])
    trading_symbol = instrument.loc[0, 'tradingsymbol']
    
    print(f"Found Active Contract: {trading_symbol} (Token: {target_token})")
    return target_token


def fetch_historical_data(instrument_token, years=5):
    to_date = datetime.now()
    from_date = to_date - timedelta(days=years * 365)
    
    print(f"Fetching daily data from {from_date.date()} to {to_date.date()}...")
    
    print(f"Fetching daily continuous data {from_date.date()} → {to_date.date()}")
    df = pd.DataFrame(kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval="day",
        continuous=True
    ))

    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df



mcx_instruments = [
    'CRUDEOILM', 'ALUMINI', 'CARDAMOM', 'ELECDMBL', 'GOLDGUINEA', 'GOLDPETAL', 'LEADMINI',
    'MENTHAOIL', 'NATGASMINI', 'ZINCMINI', 'SILVERMIC'
]

nfo_instruments = [
    'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'NIFTYNXT50'
]

cds_instruments = [
    'USDINR', 'EURINR', 'GBPINR', 'JPYINR'
]


def main():
    try:
        os.makedirs("cds", exist_ok=True)

        for symbol in cds_instruments:
            print(f"Processing {symbol}...")
        
        
            token = get_instument_token(symbol=symbol, exchange="CDS")
            print(f"Instrument Token: {token}")

            historical_df = fetch_historical_data(instrument_token=token, years=5)

            csv_path = os.path.join("cds", f"{symbol}_historical_data.csv")
            historical_df.to_csv(csv_path, index=False)

            print(f"Data for {symbol} saved to {csv_path}\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()