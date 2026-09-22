"""Every calc must expose the audit envelope fields."""
from app.services.calculations.electrical import calculate_voltage_drop
from app.services.calculations.hydraulic import calculate_pump_power
from app.services.calculations.energy import calculate_chiller_cop

REQUIRED = [
    "discipline",
    "calc_type",
    "name",
    "inputs",
    "formula",
    "units",
    "assumptions",
    "result",
    "check_status",
    "check_notes",
    "source",
    "version",
    "engine_module",
]


def test_envelope_fields():
    samples = [
        calculate_voltage_drop(50, 40, 25, 400),
        calculate_pump_power(100, 20, 0.8),
        calculate_chiller_cop(1000, 200),
    ]
    for s in samples:
        d = s.to_dict()
        for k in REQUIRED:
            assert k in d and d[k] is not None, f"missing {k} in {s.calc_type}"
