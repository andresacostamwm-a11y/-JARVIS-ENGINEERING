from app.models import AuditEvent
def write_audit(db,action,resource_type,resource_id=None,user_id=None,org_id=None,detail=None):
 e=AuditEvent(action=action,resource_type=resource_type,resource_id=resource_id,user_id=user_id,org_id=org_id,detail=detail or {});db.add(e);db.commit();db.refresh(e);return e
