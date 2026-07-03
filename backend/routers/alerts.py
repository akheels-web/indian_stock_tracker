"""Alerts API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from database import get_db
from models import Alert, AlertSeverity, AlertType
from schemas import AlertResponse, AlertStats

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    is_active: Optional[bool] = None,
    is_read: Optional[bool] = None,
    stock_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get alerts with filters"""
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)
    if stock_id:
        query = query.filter(Alert.stock_id == stock_id)

    alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()

    return [
        {
            "id": a.id,
            "stock_id": a.stock_id,
            "stock_symbol": a.stock.symbol,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "trigger_price": a.trigger_price,
            "is_read": a.is_read,
            "is_acknowledged": a.is_acknowledged,
            "is_active": a.is_active,
            "created_at": a.created_at,
        }
        for a in alerts
    ]


@router.get("/stats", response_model=AlertStats)
def get_alert_stats(db: Session = Depends(get_db)):
    """Get alert statistics"""
    from sqlalchemy import func

    total = db.query(Alert).count()
    unread = db.query(Alert).filter(Alert.is_read == False).count()
    critical = db.query(Alert).filter(Alert.severity == AlertSeverity.CRITICAL).count()
    high = db.query(Alert).filter(Alert.severity == AlertSeverity.HIGH).count()

    by_type = {}
    type_counts = db.query(Alert.alert_type, func.count(Alert.id)).group_by(Alert.alert_type).all()
    for at, count in type_counts:
        by_type[at.value] = count

    return AlertStats(
        total_alerts=total,
        unread_count=unread,
        critical_count=critical,
        high_count=high,
        by_type=by_type,
    )


@router.post("/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark alert as read"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    db.commit()
    return {"message": "Alert marked as read"}


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge and dismiss alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_acknowledged = True
    alert.is_active = False
    alert.resolved_at = datetime.now()
    db.commit()
    return {"message": "Alert acknowledged"}


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolve an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_active = False
    alert.resolved_at = datetime.now()
    db.commit()
    return {"message": "Alert resolved"}


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted"}
