import io
import matplotlib.pyplot as plt
import seaborn as sns
from database import MouseEvent, PredictEnum, Request, TrackingCode
from flask import Blueprint, Response, current_app, request
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix as cm
import numpy as np
bp = Blueprint("plot", __name__, url_prefix="/plot")


@bp.route("request/<hash_id>.png")
def plot_request(hash_id):
    events = MouseEvent.query.filter_by(
        request_hash_id=hash_id).order_by(MouseEvent.timestamp).all()
    fig = create_mouse_events_figure(events)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


@bp.route("/<group_type>/<hash_value>/attribute.png")
def plot_attribute(group_type, hash_value):
    if group_type == "by_user":
        codes = TrackingCode.query.filter(
            TrackingCode.user_id == int(hash_value),
        ).all()

        requests = Request.query.filter(
            Request.tracking_code.in_([c.code for c in codes]),
        ).all()
    elif group_type == "by_code":
        requests = Request.query.filter(
            Request.tracking_code == hash_value,
        ).all()
    else:
        requests = []
    fig = create_attribute_figure(requests)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


@bp.route("/<group_type>/<hash_value>/accuracy.png")
def plot_accuracy(group_type, hash_value):
    current_app.logger.info(group_type is not None)

    if group_type == "by_user":
        codes = TrackingCode.query.filter(
            TrackingCode.user_id == int(hash_value),
        ).all()

        requests = Request.query.all()
    elif group_type == "by_code":
        zone_id = request.args.get('zone_id')

        if zone_id is not None:
            requests = (
                Request.query.filter(
                    and_(
                        Request.tracking_code == hash_value,
                        Request.zone_id == zone_id,
                    )
                )
                .all()
            )
        else:

            requests = Request.query.filter(
                Request.tracking_code == hash_value,
            ).all()
    else:
        requests = []
    fig = create_accuracy_figure(requests)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")


def create_mouse_events_figure(events):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = [event.x_client for event in events]
    ys = [event.y_client for event in events]
    axis.scatter(xs, ys)
    axis.plot(xs, ys)
    return fig


def create_accuracy_figure(requests):
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.tight_layout()

    if len(requests) > 0:
        labels = ['Không là bot', 'Là bot']
        sizes = [
            sum(r.is_bot() != True for r in requests),
            sum(r.is_bot() == True for r in requests)

        ]
        explode = (0.1, 0)

        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
               shadow=True, startangle=90)
        ax.axis('equal')

    return fig


def create_attribute_figure(requests):

    bot_count = sum(r.is_bot() == True for r in requests)
    bad_referer = sum(r.bad_referer == True for r in requests)
    me_count = sum(r.predict_result == PredictEnum.bot for r in requests)
    os_count = sum(r.os_inconsistency == True for r in requests)
    fingerprint_count = sum((r.exist_bot_attributes and r.exist_bot_attributes != '[]') for r in requests)
    ua_count = sum(r.user_agent_inconsistency == True for r in requests)
    ip_count = sum((r.data_center_ip_address == True and r.data_center_ip_address != '[]') for r in requests)

    results = {
        'Số truy cập có đặc trưng của bot': [fingerprint_count, len(requests) - fingerprint_count],
        'Số truy cập truy cập từ Data Center': [ip_count, len(requests) - ip_count],
        'Số truy cập không xác minh được OS': [os_count, len(requests) - os_count],
        'Số truy cập không đồng nhất User Agent': [ua_count, len(requests) - ua_count],
        'Số truy cập phát hiện bởi cử chỉ chuột': [me_count, len(requests) - me_count],
        'Số truy cập có nguồn không tin cậy': [bad_referer, len(requests) - bad_referer],
        'Số lượt truy cập là bot': [bot_count, len(requests) - bot_count]
    }
    labels = list(results.keys())
    data = np.array(list(results.values()))

    data_cum = data.cumsum(axis=1)
    category_colors = [
        [0.89888504, 0.30549789, 0.20676663, 1.],
        [0.99707805, 0.9987697, 0.74502115, 1.]
    ]

    fig, ax = plt.subplots(figsize=(12, 3))
    fig.tight_layout()
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, color in enumerate(category_colors):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=color, color=color)
    plt.gcf().subplots_adjust(left=0.27)

    return fig
