class DividendCalculator:
    def __init__(
        self,
        duration: int,
        initial_investment: float = 0.0,
        extra_monthly_investment: float = 0.0,
        stock_price: float = 29.35,
        annual_stock_growth: float = 0.05,
        trade_commission: float = 0.001,
        dividend_yield: float = 0.035,
        annual_dividend_growth: float = 0.09,
        dividend_tax: float = 0.154,
        dividend_frequency: int = 4,
        reinvest_dividend: bool = True,
        currency_exchange_rate: float = 1400,
        currency_exchange_fee: float = 0.005,
    ) -> None:
        if not duration > 0:
            raise ValueError("duration must be positive")

        float_args = [
            "annual_stock_growth",
            "dividend_yield",
            "trade_commission",
            "annual_dividend_growth",
            "dividend_tax",
            "currency_exchange_fee",
        ]
        if not 0 < annual_stock_growth < 1:
            raise ValueError("annual_stock_growth must between (0, 1)")
        for name in float_args:
            if not 0 < eval(name) < 1:
                raise ValueError(f"{name} must between (0, 1)")
        if not stock_price > 0:
            raise ValueError("stock_price must greater than 0")

        self._a_m = extra_monthly_investment
        self._d = duration
        self._a_init = initial_investment
        self._p_stock = stock_price
        self._r_stock = annual_stock_growth
        self._commission = trade_commission
        self._y_divd = dividend_yield
        self._r_divd = annual_dividend_growth
        self._tax = dividend_tax
        self._freq = dividend_frequency
        self._reinvest = reinvest_dividend
        self._currency = currency_exchange_rate
        self._currency_fee = currency_exchange_fee

    def _krw_to_usd(
        self,
        krw: float,
        currency: float,
        currency_fee: float,
    ) -> float:
        return (krw / currency) * (1 - currency_fee)

    def _initialize(self):
        a_init = self._a_init
        a_init_usd = self._krw_to_usd(a_init, self._currency, self._currency_fee)
        a_init_usd *= (1 - self._commission)
        p_stock = self._p_stock
        total_stock = a_init_usd / p_stock
        return {
            "month": 0,
            "investment": a_init_usd,
            "total_investment": a_init_usd,
            "num_stock": total_stock,
            "stock_bought": total_stock,
            "stock_price": p_stock,
            "dividend_yield": self._y_divd,
            "dividend_income": 0.0,
            "dividend_income_after_tax": 0.0,
        }

    def get_dividend_income(
        self,
        num_stock: float,
        stock_price: float,
        dividend_yield: float,
    ) -> list[float]:
        unit_price = stock_price * dividend_yield / self._freq
        dividend_income = unit_price * num_stock
        dividend_income_after_tax = dividend_income * (1 - self._tax)
        return [dividend_income, dividend_income_after_tax]

    def simulate(self):
        d = self._d
        y_divd = self._y_divd

        result = [self._initialize()]
        for month in range(1, d+1):
            prev = result[-1]

            # monthly investment amount
            a_m = self._krw_to_usd(self._a_m, self._currency, self._currency_fee)
            a_m *= (1 - self._commission)

            # calculate dividend
            if (month % 12) % 3 == 0:
                a_divd, a_divd_tax = self.get_dividend_income(
                    num_stock=prev["num_stock"],
                    stock_price=prev["stock_price"],
                    dividend_yield=y_divd,
                )
            else:
                a_divd = a_divd_tax = 0

            # apply monthly stock growth
            r_stock_m = (1 + self._r_stock)**(1/12) - 1
            p_stock = prev["stock_price"] * (1 + r_stock_m)

            # buy stock
            a_total = a_m + a_divd_tax if self._reinvest else a_m
            num_stock = a_total / p_stock

            result.append({
                "month": month,
                "investment": prev["investment"] * (1+r_stock_m) + a_m,
                "total_investment": prev["total_investment"] * (1+r_stock_m) + a_total,
                "num_stock": prev["num_stock"] + num_stock,
                "stock_bought": num_stock,
                "stock_price": p_stock,
                "dividend_yield": y_divd,
                "dividend_income": a_divd,
                "dividend_income_after_tax": a_divd_tax,
            })

            # annual dividend growth
            if month % 12 == 0:
                y_divd *= (1 + self._r_divd)

        return result
