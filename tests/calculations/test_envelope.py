from app.services.calculations.electrical import calculate_voltage_drop
def test_audit_envelope():
 d=calculate_voltage_drop(50,40,25,400).to_dict()
 for k in ['inputs','formula','units','assumptions','result','check_status','source','version']:assert k in d and d[k] is not None
