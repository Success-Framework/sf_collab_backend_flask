from app.extensions import db
from app.models.planVersion import PlanVersion


def create_plan_version(
    plan_id,
    trigger_type,
    summary,
    health_score=None,
    health_status=None
):
    latest = (
        PlanVersion.query
        .filter_by(plan_id=plan_id)
        .order_by(PlanVersion.version_number.desc())
        .first()
    )

    next_version = 1 if not latest else latest.version_number + 1

    version = PlanVersion(
        plan_id=plan_id,
        version_number=next_version,
        trigger_type=trigger_type,
        summary=summary,
        health_score=health_score,
        health_status=health_status
    )

    db.session.add(version)
    db.session.commit()

    return version
