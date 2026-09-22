from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Drawing, DrawingNode, DrawingEdge, User
from app.schemas.common import DrawingCreate, DrawingUpdate
from app.api.deps import get_current_user, require_min_role
from app.models.entities import Role
from app.services.audit import write_audit

router = APIRouter()


def _drawing_json(d: Drawing) -> dict:
    return {
        "id": str(d.id),
        "org_id": str(d.org_id),
        "project_id": str(d.project_id) if d.project_id else None,
        "name": d.name,
        "drawing_type": d.drawing_type,
        "schema_version": d.schema_version,
        "viewport": d.viewport or {},
        "is_demo": d.is_demo,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        "nodes": [
            {
                "id": str(n.id),
                "node_key": n.node_key,
                "node_type": n.node_type,
                "label": n.label,
                "position": {"x": n.position_x, "y": n.position_y},
                "asset_id": str(n.asset_id) if n.asset_id else None,
                "data": n.data or {},
            }
            for n in d.nodes
        ],
        "edges": [
            {
                "id": str(e.id),
                "edge_key": e.edge_key,
                "source": e.source_key,
                "target": e.target_key,
                "label": e.label,
                "edge_type": e.edge_type,
                "data": e.data or {},
            }
            for e in d.edges
        ],
    }


@router.get("")
def list_drawings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Drawing)
    if user.org_id:
        q = q.filter(Drawing.org_id == user.org_id)
    return [_drawing_json(d) for d in q.order_by(Drawing.updated_at.desc()).all()]


@router.post("", status_code=201)
def create_drawing(
    body: DrawingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    if not user.org_id:
        raise HTTPException(400, "User has no organization")
    d = Drawing(
        org_id=user.org_id,
        project_id=body.project_id,
        name=body.name,
        drawing_type=body.drawing_type,
        viewport=body.viewport,
        is_demo=False,
    )
    db.add(d)
    db.flush()
    for n in body.nodes:
        db.add(
            DrawingNode(
                drawing_id=d.id,
                node_key=n.node_key,
                node_type=n.node_type,
                label=n.label,
                position_x=n.position_x,
                position_y=n.position_y,
                asset_id=n.asset_id,
                data=n.data,
            )
        )
    for e in body.edges:
        db.add(
            DrawingEdge(
                drawing_id=d.id,
                edge_key=e.edge_key,
                source_key=e.source_key,
                target_key=e.target_key,
                label=e.label,
                edge_type=e.edge_type,
                data=e.data,
            )
        )
    db.commit()
    db.refresh(d)
    write_audit(
        db,
        action="create",
        resource_type="drawing",
        resource_id=str(d.id),
        user_id=user.id,
        org_id=user.org_id,
    )
    return _drawing_json(d)


@router.get("/{drawing_id}")
def get_drawing(drawing_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not d:
        raise HTTPException(404, "Drawing not found")
    return _drawing_json(d)


@router.put("/{drawing_id}")
def update_drawing(
    drawing_id: UUID,
    body: DrawingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(Role.ENGINEER)),
):
    d = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not d:
        raise HTTPException(404, "Drawing not found")
    if body.name is not None:
        d.name = body.name
    if body.viewport is not None:
        d.viewport = body.viewport
    if body.nodes is not None:
        db.query(DrawingNode).filter(DrawingNode.drawing_id == d.id).delete()
        for n in body.nodes:
            db.add(
                DrawingNode(
                    drawing_id=d.id,
                    node_key=n.node_key,
                    node_type=n.node_type,
                    label=n.label,
                    position_x=n.position_x,
                    position_y=n.position_y,
                    asset_id=n.asset_id,
                    data=n.data,
                )
            )
    if body.edges is not None:
        db.query(DrawingEdge).filter(DrawingEdge.drawing_id == d.id).delete()
        for e in body.edges:
            db.add(
                DrawingEdge(
                    drawing_id=d.id,
                    edge_key=e.edge_key,
                    source_key=e.source_key,
                    target_key=e.target_key,
                    label=e.label,
                    edge_type=e.edge_type,
                    data=e.data,
                )
            )
    db.commit()
    db.refresh(d)
    write_audit(
        db,
        action="update",
        resource_type="drawing",
        resource_id=str(d.id),
        user_id=user.id,
        org_id=user.org_id,
    )
    return _drawing_json(d)


@router.get("/{drawing_id}/export.json")
def export_json(drawing_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not d:
        raise HTTPException(404, "Drawing not found")
    import json

    payload = _drawing_json(d)
    return Response(
        content=json.dumps(payload, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{d.name}.jarvis.json"'},
    )


@router.get("/{drawing_id}/export.svg")
def export_svg(drawing_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Export a simple SVG representation derived from JARVIS Drawing JSON (source of truth remains JSON)."""
    d = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not d:
        raise HTTPException(404, "Drawing not found")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">',
        "<rect width=\"100%\" height=\"100%\" fill=\"#0f172a\"/>",
        f'<text x="20" y="30" fill="#94a3b8" font-family="sans-serif" font-size="14">{d.name} (JARVIS Drawing)</text>',
    ]
    node_pos = {n.node_key: (n.position_x, n.position_y) for n in d.nodes}
    for e in d.edges:
        if e.source_key in node_pos and e.target_key in node_pos:
            x1, y1 = node_pos[e.source_key]
            x2, y2 = node_pos[e.target_key]
            parts.append(
                f'<line x1="{x1+60}" y1="{y1+20}" x2="{x2}" y2="{y2+20}" stroke="#38bdf8" stroke-width="2"/>'
            )
    for n in d.nodes:
        x, y = n.position_x, n.position_y
        parts.append(
            f'<rect x="{x}" y="{y}" width="120" height="40" rx="6" fill="#1e293b" stroke="#64748b"/>'
        )
        parts.append(
            f'<text x="{x+8}" y="{y+25}" fill="#e2e8f0" font-family="sans-serif" font-size="12">{n.label[:18]}</text>'
        )
    parts.append("</svg>")
    svg = "\n".join(parts)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'attachment; filename="{d.name}.svg"'},
    )
