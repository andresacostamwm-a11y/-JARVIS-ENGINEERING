from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Calculation, User
from app.schemas.common import CalcRequestElectricalVD, CalcRequestPump, CalcRequestEnergy
from app.api.deps import get_current_user, require_min_role
from app.models.entities import Role
from app.services.calculations.electrical import (
    calculate_voltage_drop,
    calculate_three_phase_power,
    calculate_cable_ampacity_check,
)
from app.services.calculations.hydraulic import (
    calculate_pump_power,
    calculate_darcy_weisbach_head_loss,
    calculate_flow_from_velocity,
)
from app.services.calculations.energy import (
    calculate_cooling_load_basic,
    calculate_chiller_cop,
    calculate_energy_cost,
)
from app.services.audit import write_audit

router = APIRouter()


def _persist(db: Session, user: User, calc_result, project_id: UUID | None) -> Calculation:
    row = Calculation(
        org_id=user.org_id,
        project_id=project_id,
        discipline=calc_result.discipline,
        calc_type=calc_result.calc_type,
        name=calc_result.name,
        inputs=calc_result.inputs,
        formula=calc_result.formula,
        units=calc_result.units,
        assumptions=calc_result.assumptions,
        result=calc_result.result,
        check_status=calc_result.check_status,
        check_notes=calc_result.check_notes,
        source=calc_result.source,
        version=calc_result.version,
        engine_module=calc_result.engine_module,
        created_by=user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    write_audit(
        db,
        action="calculate",
        resource_type="calculation",
        resource_id=str(row.id),
        user_id=user.id,
        org_id=user.org_id,
        detail={"calc_type": row.calc_type, "check": row.check_status},
    )
    return row


@router.get("")
def list_calculations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Calculation)
    if user.org_id:
        q = q.filter(Calculation.org_id == user.org_id)
    rows = q.order_by(Calculation.created_at.desc()).limit(100).all()
    return [
        {
            "id": str(r.id),
            "discipline": r.discipline,
            "calc_type": r.calc_type,
            "name": r.name,
            "inputs": r.inputs,
            "formula": r.formula,
            "units": r.units,
            "assumptions": r.assumptions,
            "result": r.result,
            "check_status": r.check_status,
            "check_notes": r.check_notes,
            "source": r.source,
            "version": r.version,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.post("/electrical")
def calc_electrical(
    body: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    subtype = body.get("subtype", "voltage_drop")
    persist = body.get("persist", True)
    project_id = body.get("project_id")
    try:
        if subtype == "voltage_drop":
            result = calculate_voltage_drop(
                current_a=float(body["current_a"]),
                length_m=float(body["length_m"]),
                conductor_area_mm2=float(body["conductor_area_mm2"]),
                voltage_v=float(body["voltage_v"]),
                phases=int(body.get("phases", 3)),
                material=body.get("material", "copper"),
                power_factor=float(body.get("power_factor", 0.85)),
            )
        elif subtype == "three_phase_power":
            result = calculate_three_phase_power(
                voltage_ll_v=float(body["voltage_ll_v"]),
                current_a=float(body["current_a"]),
                power_factor=float(body.get("power_factor", 0.9)),
                efficiency=float(body.get("efficiency", 1.0)),
            )
        elif subtype == "cable_ampacity_check":
            result = calculate_cable_ampacity_check(
                load_current_a=float(body["load_current_a"]),
                cable_ampacity_a=float(body["cable_ampacity_a"]),
                continuous_load=bool(body.get("continuous_load", True)),
                safety_factor=float(body.get("safety_factor", 1.25)),
            )
        else:
            raise HTTPException(400, f"Unknown subtype: {subtype}")
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(400, str(e))
    if body.get("name"):
        result.name = body["name"]
    out = result.to_dict()
    if persist and user.org_id:
        row = _persist(db, user, result, UUID(project_id) if project_id else None)
        out["id"] = str(row.id)
    return out


@router.post("/hydraulic")
def calc_hydraulic(
    body: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    subtype = body.get("subtype", "pump_power")
    persist = body.get("persist", True)
    project_id = body.get("project_id")
    try:
        if subtype == "pump_power":
            result = calculate_pump_power(
                flow_m3_h=float(body["flow_m3_h"]),
                head_m=float(body["head_m"]),
                efficiency=float(body.get("efficiency", 0.75)),
                density_kg_m3=float(body.get("density_kg_m3", 998.0)),
            )
        elif subtype == "darcy_weisbach_head_loss":
            result = calculate_darcy_weisbach_head_loss(
                flow_m3_h=float(body["flow_m3_h"]),
                length_m=float(body["length_m"]),
                diameter_m=float(body["diameter_m"]),
                friction_factor=float(body.get("friction_factor", 0.02)),
                density_kg_m3=float(body.get("density_kg_m3", 998.0)),
            )
        elif subtype == "flow_from_velocity":
            result = calculate_flow_from_velocity(
                velocity_m_s=float(body["velocity_m_s"]),
                diameter_m=float(body["diameter_m"]),
            )
        else:
            raise HTTPException(400, f"Unknown subtype: {subtype}")
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(400, str(e))
    if body.get("name"):
        result.name = body["name"]
    out = result.to_dict()
    if persist and user.org_id:
        row = _persist(db, user, result, UUID(project_id) if project_id else None)
        out["id"] = str(row.id)
    return out


@router.post("/energy")
def calc_energy(
    body: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    subtype = body.get("subtype", "cooling_load_basic")
    persist = body.get("persist", True)
    project_id = body.get("project_id")
    try:
        if subtype == "cooling_load_basic":
            result = calculate_cooling_load_basic(
                airflow_m3_h=float(body["airflow_m3_h"]),
                delta_t_k=float(body["delta_t_k"]),
                sensible_fraction=float(body.get("sensible_fraction", 1.0)),
            )
        elif subtype == "chiller_cop":
            result = calculate_chiller_cop(
                cooling_capacity_kw=float(body["cooling_capacity_kw"]),
                power_input_kw=float(body["power_input_kw"]),
            )
        elif subtype == "energy_cost":
            result = calculate_energy_cost(
                power_kw=float(body["power_kw"]),
                hours=float(body["hours"]),
                tariff_per_kwh=float(body["tariff_per_kwh"]),
            )
        else:
            raise HTTPException(400, f"Unknown subtype: {subtype}")
    except (KeyError, ValueError, TypeError) as e:
        raise HTTPException(400, str(e))
    if body.get("name"):
        result.name = body["name"]
    out = result.to_dict()
    if persist and user.org_id:
        row = _persist(db, user, result, UUID(project_id) if project_id else None)
        out["id"] = str(row.id)
    return out
