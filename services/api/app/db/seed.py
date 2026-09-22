"""DEMO seed data — clearly labeled."""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models import (
    Organization,
    User,
    Site,
    System,
    Asset,
    AssetRelation,
    Project,
    Drawing,
    DrawingNode,
    DrawingEdge,
    Document,
    DocumentChunk,
)
from app.models.entities import Role


def seed_demo(db: Session) -> None:
    existing = db.query(User).filter(User.email == "demo@jarvis.local").first()
    if existing:
        return

    org = Organization(name="DEMO — Planta Industrial Norte", slug="demo-planta-norte", is_demo=True)
    db.add(org)
    db.flush()

    demo_user = User(
        email="demo@jarvis.local",
        full_name="Demo Engineer",
        hashed_password=hash_password("demo1234"),
        role=Role.ENGINEER,
        org_id=org.id,
        is_demo=True,
    )
    admin = User(
        email="admin@jarvis.local",
        full_name="Demo Admin",
        hashed_password=hash_password("admin1234"),
        role=Role.ADMIN,
        org_id=org.id,
        is_demo=True,
    )
    db.add_all([demo_user, admin])
    db.flush()

    site = Site(
        org_id=org.id,
        name="DEMO — Sitio Principal",
        code="SITE-DEMO-01",
        location="Cancún, Q.Roo (DEMO)",
        is_demo=True,
        meta={"timezone": "America/Cancun"},
    )
    db.add(site)
    db.flush()

    sys_elec = System(site_id=site.id, name="DEMO — Eléctrico", discipline="electrical", is_demo=True)
    sys_hyd = System(site_id=site.id, name="DEMO — Hidráulico/HVAC", discipline="hydraulic", is_demo=True)
    sys_ctrl = System(site_id=site.id, name="DEMO — BMS/Controles", discipline="controls", is_demo=True)
    db.add_all([sys_elec, sys_hyd, sys_ctrl])
    db.flush()

    assets_spec = [
        ("CH-01", "Chiller Centrífugo 1", "chiller", sys_hyd.id, {"capacity_tr": 500, "refrigerant": "R-134a", "power_kw": 320}),
        ("CH-02", "Chiller Tornillo 2", "chiller", sys_hyd.id, {"capacity_tr": 350, "refrigerant": "R-134a", "power_kw": 240}),
        ("P-CHW-01", "Bomba Agua Helada 1", "pump", sys_hyd.id, {"flow_m3_h": 450, "head_m": 35, "power_kw": 55}),
        ("P-CHW-02", "Bomba Agua Helada 2", "pump", sys_hyd.id, {"flow_m3_h": 450, "head_m": 35, "power_kw": 55}),
        ("P-CW-01", "Bomba Agua de Condensación 1", "pump", sys_hyd.id, {"flow_m3_h": 600, "head_m": 25, "power_kw": 45}),
        ("P-CW-02", "Bomba Agua de Condensación 2", "pump", sys_hyd.id, {"flow_m3_h": 600, "head_m": 25, "power_kw": 45}),
        ("TR-01", "Transformador Principal", "transformer", sys_elec.id, {"kva": 2500, "voltage_pri_v": 23000, "voltage_sec_v": 480}),
        ("GEN-01", "Generador de Emergencia", "generator", sys_elec.id, {"kva": 1500, "fuel": "diesel", "voltage_v": 480}),
        ("PTAR-01", "Planta Tratamiento Aguas Residuales", "wwtp", sys_hyd.id, {"capacity_m3_d": 800}),
        ("BMS-01", "BMS Central (stub)", "bms", sys_ctrl.id, {"protocol": "BACnet/IP", "status": "COMING SOON full integration"}),
        ("CT-01", "Torre de Enfriamiento 1", "cooling_tower", sys_hyd.id, {"flow_m3_h": 650, "fan_kw": 30}),
        ("CT-02", "Torre de Enfriamiento 2", "cooling_tower", sys_hyd.id, {"flow_m3_h": 650, "fan_kw": 30}),
        ("AHU-01", "Unidad Manejadora de Aire 1", "ahu", sys_hyd.id, {"airflow_m3_h": 25000, "cooling_kw": 180}),
        ("AHU-02", "Unidad Manejadora de Aire 2", "ahu", sys_hyd.id, {"airflow_m3_h": 18000, "cooling_kw": 120}),
        ("MCC-01", "Centro de Control de Motores", "mcc", sys_elec.id, {"voltage_v": 480, "sections": 12}),
        ("UPS-01", "UPS Sala Eléctrica", "ups", sys_elec.id, {"kva": 120, "autonomy_min": 15}),
        ("VFD-P01", "Variador Bomba CHW-01", "vfd", sys_elec.id, {"kw": 55, "input_v": 480}),
        ("TK-CHW-01", "Tanque Expansión Agua Helada", "tank", sys_hyd.id, {"volume_m3": 12}),
        ("SWBD-01", "Tablero Principal Baja Tensión", "switchboard", sys_elec.id, {"amps": 4000, "voltage_v": 480}),
        ("METER-01", "Medidor de Energía Principal", "meter", sys_elec.id, {"protocol": "Modbus TCP"}),
    ]

    asset_map: dict[str, Asset] = {}
    for tag, name, atype, sys_id, specs in assets_spec:
        a = Asset(
            site_id=site.id,
            system_id=sys_id,
            tag=tag,
            name=f"DEMO — {name}",
            asset_type=atype,
            manufacturer="DEMO Vendor",
            model="DEMO-MODEL",
            status="operational",
            specs=specs,
            is_demo=True,
        )
        db.add(a)
        db.flush()
        asset_map[tag] = a

    relations = [
        ("TR-01", "SWBD-01", "feeds"),
        ("SWBD-01", "MCC-01", "feeds"),
        ("SWBD-01", "UPS-01", "feeds"),
        ("GEN-01", "SWBD-01", "feeds"),
        ("MCC-01", "VFD-P01", "feeds"),
        ("VFD-P01", "P-CHW-01", "drives"),
        ("CH-01", "P-CHW-01", "cooled_by"),
        ("CH-01", "P-CW-01", "rejects_heat_via"),
        ("P-CW-01", "CT-01", "feeds"),
        ("BMS-01", "CH-01", "controls"),
        ("BMS-01", "AHU-01", "controls"),
    ]
    for frm, to, rel in relations:
        db.add(
            AssetRelation(
                from_asset_id=asset_map[frm].id,
                to_asset_id=asset_map[to].id,
                relation_type=rel,
            )
        )

    project = Project(
        org_id=org.id,
        site_id=site.id,
        name="DEMO — Retrofit HVAC Fase 1",
        code="PRJ-DEMO-001",
        description="Proyecto DEMO de modernización de chillers y bombas. CAPEX estimado ilustrativo.",
        status="active",
        capex_estimate=1_250_000,
        currency="USD",
        is_demo=True,
        meta={"phase": 1},
    )
    db.add(project)
    db.flush()

    # Demo drawing (React Flow JSON source of truth)
    drawing = Drawing(
        org_id=org.id,
        project_id=project.id,
        name="DEMO — Esquema CHW Simplificado",
        drawing_type="schematic",
        schema_version="1.0",
        viewport={"x": 0, "y": 0, "zoom": 1},
        is_demo=True,
    )
    db.add(drawing)
    db.flush()

    nodes = [
        ("n1", "chiller", "CH-01", 80, 200, asset_map["CH-01"].id),
        ("n2", "pump", "P-CHW-01", 280, 120, asset_map["P-CHW-01"].id),
        ("n3", "pump", "P-CHW-02", 280, 280, asset_map["P-CHW-02"].id),
        ("n4", "ahu", "AHU-01", 520, 120, asset_map["AHU-01"].id),
        ("n5", "ahu", "AHU-02", 520, 280, asset_map["AHU-02"].id),
        ("n6", "tower", "CT-01", 80, 400, asset_map["CT-01"].id),
    ]
    for key, ntype, label, x, y, aid in nodes:
        db.add(
            DrawingNode(
                drawing_id=drawing.id,
                node_key=key,
                node_type=ntype,
                label=label,
                position_x=x,
                position_y=y,
                asset_id=aid,
                data={"demo": True},
            )
        )
    edges = [
        ("e1", "n1", "n2", "CHW supply"),
        ("e2", "n1", "n3", "CHW supply"),
        ("e3", "n2", "n4", "to AHU"),
        ("e4", "n3", "n5", "to AHU"),
        ("e5", "n1", "n6", "CW"),
    ]
    for key, src, tgt, label in edges:
        db.add(
            DrawingEdge(
                drawing_id=drawing.id,
                edge_key=key,
                source_key=src,
                target_key=tgt,
                label=label,
                edge_type="pipe",
                data={"demo": True},
            )
        )

    # Demo document + chunks for RAG
    doc = Document(
        org_id=org.id,
        site_id=site.id,
        title="DEMO — Manual Operación Chillers",
        filename="demo_chiller_manual.txt",
        content_type="text/plain",
        storage_key=f"demo/{org.id}/demo_chiller_manual.txt",
        size_bytes=0,
        status="ready",
        is_demo=True,
        created_by=demo_user.id,
        meta={"label": "DEMO"},
    )
    db.add(doc)
    db.flush()
    demo_text = (
        "DEMO DOCUMENT — Manual de operación de chillers. "
        "El chiller CH-01 tiene capacidad de 500 TR y refrigerante R-134a. "
        "Mantener ΔT de agua helada entre 5 y 7 K. "
        "La bomba P-CHW-01 debe operar a 450 m3/h con 35 m de cabeza. "
        "COP esperado a plena carga entre 4.5 y 5.5. "
        "Antes de arrancar verificar válvulas de aislamiento y nivel de aceite. "
        "PTAR-01 trata 800 m3/día. BMS-01 supervisa vía BACnet/IP (integración completa COMING SOON)."
    )
    doc.size_bytes = len(demo_text.encode())
    for i, chunk in enumerate([demo_text[j : j + 200] for j in range(0, len(demo_text), 180)]):
        db.add(DocumentChunk(document_id=doc.id, chunk_index=i, content=chunk, meta={"demo": True}))

    db.commit()
