from flask.globals import current_app
from database import MouseEvent, Request, db, TrackingCode
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import desc, func, asc, and_
from datetime import timedelta
from collections import defaultdict
import dateutil
bp = Blueprint("main", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
@login_required
def index():
    codes = TrackingCode.query.all()
    return render_template("home.html", user=current_user, codes=codes)


@bp.route("create-code", methods=["POST"])
@login_required
def create_code():
    code = request.form.get('code', '').strip()
    if not code:
        flash("That code must not be empty")
        return redirect(url_for("main.index"))
    found = TrackingCode.query.filter(
        TrackingCode.code == code
    ).first()
    if found:
        flash("That code already exists")
        return redirect(url_for("main.index"))
    tracking_code = TrackingCode()
    tracking_code.code = code
    tracking_code.user_id = current_user.id
    db.session.add(tracking_code)
    db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("delete-code/<id>", methods=["POST"])
@login_required
def delete_code(id):
    tracking_code = TrackingCode.query.get(int(id))
    if tracking_code:
        db.session.delete(tracking_code)
        db.session.commit()
    return redirect(url_for("main.index"))


@bp.route("result/<code>", methods=["GET"])
@login_required
def get_result(code):

    query = db.session.query(Request, func.count(MouseEvent.id)).join(MouseEvent, MouseEvent.request_hash_id == Request.hash_id, isouter=True).filter(
        Request.tracking_code == code
    )

    start_date = request.args.get('start_date')
    if start_date:
        start_date = dateutil.parser.parse(start_date)
        if start_date:
            query = query.filter(Request.time >= start_date)
    end_date = request.args.get('end_date')
    if end_date:
        end_date = dateutil.parser.parse(end_date)
        if end_date:
            query = query.filter(Request.time <= end_date)

    raw_data = query.order_by(desc(Request.time)).group_by(Request).all()

    requests_without_mouse_events = sum(count == 0 for _, count in raw_data)
    requests = [r for r, _  in raw_data]
    detected_by_user_agent = sum(r.user_agent_inconsistency != False for r in requests)

    series_too_short = sum(count <= 3 and count > 0 for _, count in raw_data)
    d = defaultdict()
    for r in requests:
        zone_id = r.zone_id.strip() if r.zone_id else r.zone_id
        if not zone_id in d:
            d[zone_id] = defaultdict(list)

        d[zone_id][r.ip_address].append(r)

    data = []

    for zone_id in d:
        if not d[zone_id]:
            continue
        group = d[zone_id]
        speeds = []
        bot_count = []
        bad_referer_count = []
        for ip_address in group:
            if not group[ip_address]:
                continue
            sub_group = group[ip_address]
            sub_group.sort(key=lambda r: r.time)
            ranges = []
            for i in sub_group:
                if len(ranges) == 0:
                    ranges.append({
                        'start': i.time,
                        'end': i.time,
                        'count': 0
                    })

                if (i.time - ranges[-1]['end']).total_seconds() > 120:
                    ranges.append({
                        'start': i.time,
                        'end': i.time,
                        'count': 1
                    })
                else:
                    ranges[-1]['end'] = i.time
                    ranges[-1]['count'] = ranges[-1]['count'] + 1
            count = 0
            speed = 0
            for time_range in ranges:
                if time_range['count']:
                    speed = speed + \
                        round((time_range['end'] - time_range['start']
                               ).total_seconds() / time_range['count'], 2)
                    count = count + 1

            if speed == 0 and len(sub_group) > 1:
                speed = round(
                    (sub_group[-1].time - sub_group[0].time).total_seconds() / (len(sub_group) - 1))
                count = 1
            speeds.append(speed/count)

            bot_count.append(sum(r.is_bot() == True for r in sub_group))
            bad_referer_count.append(
                sum((r.bad_referer == True) for r in sub_group))
        data.append({
            "zone_id": str(zone_id),
            "count": sum([len(group[key]) for key in group]),
            "speed": round(sum(speeds) / len(speeds), 2) if len(speeds) > 0 else 0,
            "bot_count": sum(bot_count),
            "bad_referer_count": sum(bad_referer_count)
        })


    time_query = ''
    if len(requests):
        if not start_date:
            start_date = min(requests, key=lambda r: r.time).time
        if not end_date:
            end_date = max(requests, key=lambda r: r.time).time
    time_query = "{} - {}".format(
        start_date.strftime("%Y-%m-%d %H:%M:%S"),
        end_date.strftime("%Y-%m-%d %H:%M:%S")

    )
    current_app.logger.info(time_query)
    return render_template(
        "result.html",
        detected_by_user_agent=detected_by_user_agent,
        series_too_short=series_too_short,
        requests_without_mouse_events=requests_without_mouse_events,
        code=code,
        data=data,
        time_query=time_query
    )


@bp.route("requests/<code>", methods=["GET"])
@bp.route("requests/<code>/<int:page>", methods=["GET"])
@login_required
def get_request(code, page=1):
    per_page = 10
    zone_id = request.args.get('zone_id')
    if zone_id is not None:
        requests = (
            Request.query.filter(
                and_(
                    Request.tracking_code == code,
                    Request.zone_id == zone_id,
                )
            )
            .order_by(desc(Request.time))
            .paginate(page, per_page, error_out=False)
        )
    else:
        requests = (
            Request.query.filter(Request.tracking_code == code)
            .order_by(desc(Request.time))
            .paginate(page, per_page, error_out=False)
        )

    return render_template(
        "requests.html",
        requests=requests,
        code=code,
        zone_id=zone_id
    )


@bp.route("request/<hash_id>", methods=["GET"])
@login_required
def show_request(hash_id):
    r = Request.query.filter(Request.hash_id == hash_id).first_or_404()
    same_ip = Request.query.filter(
        and_(
            Request.time > (r.time - timedelta(days=1)),
            Request.ip_address == r.ip_address,
            Request.tracking_code == r.tracking_code,

        )).order_by(asc(Request.time)).all()

    data = []
    for i in same_ip:
        if len(data) == 0:
            data.append({
                'start': i.time,
                'end': i.time,
                'count': 0
            })

        if (i.time - data[-1]['end']).total_seconds() > 120:
            data.append({
                'start': i.time,
                'end': i.time,
                'count': 1
            })
        else:
            data[-1]['end'] = i.time
            data[-1]['count'] = data[-1]['count'] + 1

    for time_range in data:
        time_range['speed'] = round((time_range['end'] - time_range['start']).total_seconds(
        ) / time_range['count'], 2) if time_range['count'] else 0

    return render_template("request.html", r=r, data=data)
