__version__ = "0.0.1"

from erpnext.controllers import taxes_and_totals
from .overrides.standard_system_rate import CustomTaxesAndTotals

# Force override
taxes_and_totals.calculate_taxes_and_totals = CustomTaxesAndTotals
