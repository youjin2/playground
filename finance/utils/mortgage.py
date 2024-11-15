import math
from abc import ABCMeta
from abc import abstractmethod


class BasePayment(metaclass=ABCMeta):
    @staticmethod
    def _safe_exp(base, exponent):
        return math.exp(exponent*math.log(base))

    @abstractmethod
    def get_monthly_payment(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_monthly_principal_payment(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_monthly_interest_payment(self, *args, **kwargs):
        pass

    @abstractmethod
    def simulate(self, *args, **kwargs):
        pass


class LevelPayment(BasePayment):
    def __init__(
        self,
        loan_amount: float,
        annual_interest: float,
        duration: int,
        extra_monthly_payment: float = 0,
        *args,
        **kwargs,
    ) -> None:
        if not duration > 0:
            raise ValueError("duration must be positive")
        if not 0 < annual_interest < 1:
            raise ValueError("interest must between (0, 1)")

        self._A = loan_amount
        self._r_y = annual_interest
        self._d = duration
        self._a_e = extra_monthly_payment

    def get_monthly_payment(
        self,
        month: int,
        loan_amount: float = None,
        duration: int = None
    ) -> float:
        if not month > 0:
            raise ValueError("month must be positive")

        A = self._A if loan_amount is None else loan_amount
        d = self._d if duration is None else duration

        r_m = self._r_y / 12
        exp = self._safe_exp(base=1+r_m, exponent=d)

        return A * r_m * exp / (exp - 1)

    def get_monthly_principal_payment(
        self,
        month: int,
        loan_amount: float = None,
        duration: int = None,
    ) -> float:
        if not month > 0:
            raise ValueError("month must be positive")

        A = self._A if loan_amount is None else loan_amount
        d = self._d if duration is None else duration

        r_m = self._r_y / 12
        exp = self._safe_exp(base=1+r_m, exponent=d)
        first_month = A * r_m / (exp - 1)

        return first_month * (1+r_m)**(month-1)

    def get_monthly_interest_payment(
        self,
        month: int,
        loan_amount: float = None,
        duration: int = None,
    ) -> float:
        if not month > 0:
            raise ValueError("month must be positive")

        A = self._A if loan_amount is None else loan_amount
        d = self._d if duration is None else duration

        total = self.get_monthly_payment(month, loan_amount=A, duration=d)
        principal = self.get_monthly_principal_payment(month, loan_amount=A, duration=d)

        return total - principal

    def simulate(self):
        A = self._A
        d = self._d
        a_e = self._a_e
        result = [
            {
                "month": 0,
                "loan_amount": A / 10000,
                "principal_payment": 0,
                "interest_payment": 0,
                "total_payment": 0,
                "extra_payment": 0,
            }
        ]
        elapsed = 1
        while A > 0 and elapsed <= d:
            total = self.get_monthly_payment(month=1, loan_amount=A, duration=d-elapsed+1)
            principal = self.get_monthly_principal_payment(month=1, loan_amount=A, duration=d-elapsed+1)
            interest = total - principal
            principal_total = principal + a_e

            if A > principal_total:
                principal_paid = principal
                extra_paid = a_e
                A -= principal_total
            else:
                principal_paid = min(A, principal)
                extra_paid = A - principal_paid
                A = 0

            result.append(
                {
                    "month": elapsed,
                    "loan_amount": A / 10000,
                    "principal_payment": principal_paid / 10000,
                    "interest_payment": interest / 10000,
                    "total_payment": total / 10000,
                    "extra_payment": extra_paid / 10000,
                }
            )

            elapsed += 1
        return result


class MortgageLoan:
    _loan_type = {
        "level_payment": LevelPayment,
    }

    def __init__(
        self,
        loan_amount: float,
        annual_interest: float,
        duration: int,
        extra_monthly_payment: float = 0,
        scenario: str = "level_payment",
        *args,
        **kwargs,
    ) -> None:
        available_types = list(self._loan_type.keys())
        if scenario not in available_types:
            raise TypeError(f"scenario must be one of {available_types}")

        self._simulator = self._loan_type[scenario](
            loan_amount=loan_amount,
            annual_interest=annual_interest,
            duration=duration,
            extra_monthly_payment=extra_monthly_payment,
            *args,
            **kwargs,
        )

        for attr_name in dir(self._simulator):
            attr = getattr(self._simulator, attr_name)
            if callable(attr) and not attr_name.startswith("__"):
                setattr(self, attr_name, attr)

    # def __getattr__(self, name):
    #     return getattr(self._simulator, name)
