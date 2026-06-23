from sqlalchemy.orm import Session
import models, schemas

def get_area(db: Session, area_id: int):
    return db.query(models.Area).filter(models.Area.id == area_id).first()

def get_areas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Area).offset(skip).limit(limit).all()

def create_area(db: Session, area: schemas.AreaCreate):
    db_area = models.Area(name=area.name, description=area.description)
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area

def delete_area(db: Session, area_id: int):
    area = get_area(db, area_id)
    if area:
        db.delete(area)
        db.commit()
    return area

def get_source(db: Session, source_id: int):
    return db.query(models.VideoSource).filter(models.VideoSource.id == source_id).first()

def get_sources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.VideoSource).offset(skip).limit(limit).all()

def create_source(db: Session, source: schemas.VideoSourceCreate):
    db_source = models.VideoSource(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def update_source(db: Session, source_id: int, source: schemas.VideoSourceCreate):
    db_source = get_source(db, source_id)
    if db_source:
        for key, value in source.model_dump().items():
            setattr(db_source, key, value)
        db.commit()
        db.refresh(db_source)
    return db_source

def delete_source(db: Session, source_id: int):
    source = get_source(db, source_id)
    if source:
        db.delete(source)
        db.commit()
    return source

def get_ppe_rules_by_area(db: Session, area_id: int):
    if not area_id:
        return []
    return db.query(models.PPERule).filter(models.PPERule.area_id == area_id).all()

def create_ppe_rule(db: Session, area_id: int, rule: schemas.PPERuleCreate):
    db_rule = models.PPERule(area_id=area_id, ppe_name=rule.ppe_name)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def delete_ppe_rule(db: Session, rule_id: int):
    rule = db.query(models.PPERule).filter(models.PPERule.id == rule_id).first()
    if rule:
        db.delete(rule)
        db.commit()
    return rule

def get_violations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Violation).order_by(models.Violation.timestamp.desc()).offset(skip).limit(limit).all()

def create_violation(db: Session, violation: schemas.ViolationCreate):
    db_violation = models.Violation(**violation.model_dump())
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation

def get_metrics(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DetectionMetrics).order_by(models.DetectionMetrics.timestamp.desc()).offset(skip).limit(limit).all()

def create_metrics(db: Session, metrics: schemas.DetectionMetrics):
    db_metrics = models.DetectionMetrics(**metrics.model_dump(exclude={'id', 'timestamp'}, exclude_none=True))
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics
