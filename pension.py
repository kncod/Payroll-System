class PensionCalculator:
    """Ethiopian pension contributions for private organizations."""

    def __init__(self, employee_rate: float = 0.07, employer_rate: float = 0.11) -> None:
        self.employee_rate = employee_rate
        self.employer_rate = employer_rate

    def calculate_employee_pension(self, salary: float) -> float:
        self._validate_salary(salary)
        return round(salary * self.employee_rate, 2)

    def calculate_employer_pension(self, salary: float) -> float:
        self._validate_salary(salary)
        return round(salary * self.employer_rate, 2)

    def calculate_total_pension(self, salary: float) -> float:
        return round(
            self.calculate_employee_pension(salary) + self.calculate_employer_pension(salary),
            2,
        )

    def _validate_salary(self, salary: float) -> None:
        if salary < 0:
            raise ValueError("Salary cannot be negative.")
