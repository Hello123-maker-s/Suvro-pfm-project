# investment/utils.py
import yfinance as yf
import datetime as dt
from decimal import Decimal, ROUND_HALF_UP

def calculate_compound_value(principal, annual_rate, start, end, investment_type, frequency=None):
    if not start or not end or annual_rate is None:
        return Decimal(principal)

    principal = Decimal(principal)
    annual_rate = Decimal(annual_rate)

    days = (end - start).days
    if days <= 0 or annual_rate == 0:
        return principal

    years = Decimal(days) / Decimal("365")

    type_based_freq = {
        'fd': 'Quarterly',
        'fixed deposit': 'Quarterly',
        'bond': 'Biannual',
        'rd': 'Monthly',
        'recurring deposit': 'Monthly',
        'stock': 'Yearly',
        'mutual fund': 'Yearly',
        'etf': 'Yearly',
        'crypto': 'Yearly',
        'pension': 'Yearly',
        'real estate': 'Yearly',
        'gold': 'Yearly',
        'other': 'Yearly',
    }

    freq_map = {
        'Monthly': Decimal('12'),
        'Quarterly': Decimal('4'),
        'Biannual': Decimal('2'),
        'Yearly': Decimal('1'),
    }

    inv_type = (investment_type or "").lower()
    final_freq = frequency or type_based_freq.get(inv_type, 'Yearly')
    comp_per_year = freq_map.get(final_freq, Decimal('1'))

    rate_per_period = (annual_rate / Decimal('100')) / comp_per_year
    periods = comp_per_year * years

    if 'rd' in inv_type:
        months = int(years * 12)
        if months <= 0:
            return principal
        monthly_rate = (annual_rate / Decimal('100')) / Decimal('12')
        value = principal * (((Decimal('1') + monthly_rate) ** months - 1) / monthly_rate)

    elif 'fd' in inv_type:
        value = principal * ((Decimal('1') + rate_per_period) ** periods)

    elif inv_type in ['stock', 'mutual fund', 'etf', 'crypto']:
        value = principal * ((Decimal('1') + (annual_rate / Decimal('100'))) ** years)

    elif 'bond' in inv_type:
        value = principal * ((Decimal('1') + rate_per_period) ** periods)

    elif inv_type in ['real estate', 'gold', 'pension']:
        value = principal * (Decimal('1') + (annual_rate / Decimal('100')) * years)

    else:
        value = principal * ((Decimal('1') + rate_per_period) ** periods)

    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _annualized_return(start_price, end_price, years):
    if start_price <= 0:
        return None
    return round(((end_price / start_price) ** (1 / years) - 1) * 100, 2)

def get_yahoo_return(symbol, years=5):
    
    end = dt.date.today()
    start = end - dt.timedelta(days=365 * years)
    try:
        data = yf.download(symbol, start=start, end=end, progress=False)
        if data.empty:
            return None
        start_price = float(data["Close"].iloc[0])
        end_price = float(data["Close"].iloc[-1])
        return _annualized_return(start_price, end_price, years)
    except Exception:
        return None

def get_expected_return_by_type(inv_type):
    t = (inv_type or "").lower()

    mapping = {
        "stock": lambda: get_yahoo_return("^NSEI"), 
        "etf": lambda: get_yahoo_return("NIFTYBEES.NS"),  
        "crypto": lambda: get_yahoo_return("BTC-INR"),
        "gold": lambda: get_yahoo_return("GOLDBEES.NS"),  
        "mutual fund": lambda: get_yahoo_return("^NSMIDCP"),  
        "bond": lambda: get_yahoo_return("ICICIB22.NS"),  
        "real estate": lambda: get_yahoo_return("EMBASSY.NS"), 
        
    }

    func = mapping.get(t)
    if not func:
        return None  

    rate = func()
    if rate is None:
        return None

    return rate
