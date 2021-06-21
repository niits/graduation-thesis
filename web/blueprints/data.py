import json
from datetime import datetime
from sqlalchemy.sql.expression import literal, func, and_
import pytz
from database import MouseEvent, Request, db, PredictEnum, BadReferrerPattern, DataCenterIpRange, TrackingCode
from detection.fingerprint.check_fingerprint import (
    check_fingerprint,
    check_user_agent_inconsistency,
)
from flask import Blueprint, jsonify, request

bp = Blueprint("data", __name__, url_prefix="/data")


@bp.route("fingerprint", methods=["POST"])
def post_fingerprint():
    data = json.loads(request.data)["data"]

    code = TrackingCode.query.filter(
            TrackingCode.code == data["tracking_code"]
        ).first()
    if not code:
        code = TrackingCode()
        code.code = data["tracking_code"]
        db.session.add(code)
        db.session.commit()
    r = Request.query.filter_by(hash_id=data["hash_id"]).first()
    if r is None:
        r = Request()
        r.hash_id = data["hash_id"]

        predetermined = data["predetermined"]
        if not (predetermined in PredictEnum.list()):
            predetermined = PredictEnum.not_predicted
        r.ip_address = request.environ.get(
            "HTTP_X_REAL_IP", request.remote_addr)
        r.predetermined_predict_result = predetermined
        r.tracking_code = str(data["tracking_code"]).strip()
        r.zone_id = str(data["zone_id"]).strip()

        r.path = data["path"]

        r.time = datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()
        r.user_agent = request.headers["User-Agent"]

    r.referer = data["fingerprint"]['referrer']
    escaped_url = func.replace(func.replace(func.replace(BadReferrerPattern.pattern, "\\", "\\\\"),
                                            "%", "\\%"),
                               "_", "\\_")
    matches = BadReferrerPattern.query.where(
        literal(r.referer).like("%" + escaped_url + "%", escape="\\")).all()

    r.bad_referer = len(matches) > 0

    fingerprint = check_fingerprint(
        data["fingerprint"], r, request.environ["REMOTE_ADDR"], request.headers
    )
    r.fingerprint_uploaded = True
    r.user_agent_inconsistency = fingerprint["user_agent_inconsistency"]

    ranges = DataCenterIpRange.query.filter(
        and_(
            DataCenterIpRange.hostmax >= r.ip_address,
            DataCenterIpRange.hostmin <= r.ip_address
        )
    ).all()
    r.data_center_ip_address = json.dumps(
        ranges[0].vendor if len(ranges)else [])

    r.exist_bot_attributes = fingerprint["exist_bot_attributes"]
    r.os_inconsistency = fingerprint["os_inconsistency"]
    r.browner_inconsistency = fingerprint["browner_inconsistency"]
    r.resolution_inconsistency = fingerprint["resolution_inconsistency"]
    r.language_inconsistency = fingerprint["language_inconsistency"]

    db.session.add(r)
    db.session.commit()

    return jsonify({"is_bot": False}), 200


@bp.route("mouse_events", methods=["POST"])
def post_mouse():
    data = json.loads(request.data)["data"]
    code = TrackingCode.query.filter(
            TrackingCode.code == data["tracking_code"]
        ).first()
    if not code:
        code = TrackingCode()
        code.code = data["tracking_code"]
        db.session.add(code)
        db.session.commit()
    r = Request.query.filter(Request.hash_id == data["hash_id"]).first()
    if r is None:
        r = Request()
        r.hash_id = data["hash_id"]

        predetermined = data["predetermined"]
        if not (predetermined in PredictEnum.list()):
            predetermined = PredictEnum.not_predicted
        r.ip_address = request.environ.get(
            "HTTP_X_REAL_IP", request.remote_addr)
        r.predetermined_predict_result = predetermined
        r.tracking_code = data["tracking_code"]
        r.user_agent_inconsistency = check_user_agent_inconsistency(
            {"userAgent": r.user_agent}, r
        )
        r.path = data["path"]
        r.zone_id = data["zone_id"]

        r.time = datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()
        r.user_agent = request.headers["User-Agent"]
        db.session.add(r)
        db.session.commit()
    events = []
    for event in data["events"]:
        e = MouseEvent()
        e.request_hash_id = data["hash_id"]
        e.x_client = event["x_client"]
        e.y_client = event["y_client"]
        e.x_window = event["x_window"]
        e.y_window = event["y_window"]
        e.event = event["event"]
        e.timestamp = event["timestamp"]
        events.append(e)
    db.session.bulk_save_objects(events)
    db.session.commit()
    return jsonify({"is_bot": False}), 200
