from operator import or_
import pickle
from xgboost import XGBClassifier

import pandas as pd
from database import MouseEvent, PredictEnum, Request, db
from detection.mouse_events.feature_extract import extract_feature
from flask import Blueprint, current_app
from sqlalchemy import asc, and_
from datetime import timedelta

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("predict")
def predict():
    not_extracted_request = []
    requests = Request.query.filter(
        Request.predict_result == PredictEnum.not_predicted
    ).all()
    # current_app.logger.info("Total {num} request, batch size = 300".format(num=len(requests)))

    for step in range(len(requests) // 300 + 1):
        # current_app.logger.info("Process batch {num}".format(num=step))

        start = step * 300
        end = min((step + 1) * 300, len(requests))

        predict_data = []
        predict_requests = []
        for i, r in enumerate(requests[start:end]):
            # current_app.logger.info(
            #     "Process {i} request of batch {step}".format(i=i, step=step)
            # )
            data = (
                MouseEvent.query.filter(MouseEvent.request_hash_id == r.hash_id)
                .with_entities(
                    MouseEvent.x_client, MouseEvent.y_client, MouseEvent.timestamp - r.time
                )
                .all()
            )
            df = pd.DataFrame(data, columns=["x_client", "y_client", "timestamp"])

            df["timestamp"] = (
                pd.to_timedelta(df["timestamp"]).dt.total_seconds()
            )
            try:
                features = extract_feature(df)
                predict_data.append(features)
                predict_requests.append(r)
            except ValueError as error:
                # print(
                #     "Mouse event series of request {hash_id} is too short".format(
                #         hash_id=r.hash_id
                #     )
                # )
                not_extracted_request.append(r)
                continue

        df = pd.DataFrame(data=predict_data, columns=['Góc di chuyển trung bình', 'Tốc độ trung bình', 'Độ lệch chuẩn của tốc độ', 'Độ cong trung bình',
                                            'Tính hiệu quả', 'Tính đều đặn', 'Số lần đổi góc di chuyển', 'Số quãng nghỉ', 'Số sự kiện', 'Thời lượng'])

        if len(predict_data) > 0:
            loaded_model = pickle.load(open("models/finalized_model.sav", "rb"))
            predict_results = loaded_model.predict(df)
            for i, result in enumerate(predict_results):
                predict_requests[i].predict_result = (
                    PredictEnum.not_bot if result else PredictEnum.bot
                )
                db.session.add(predict_requests[i])
            db.session.commit()
        current_app.logger.info(len(not_extracted_request))
        for r in not_extracted_request:
            sample_ip_and_zone = Request.query.filter(
                and_(
                    or_(
                        Request.time > (r.time - timedelta(minutes=30)),
                        Request.time < (r.time + timedelta(minutes=30))
                    ),
                    Request.zone_id == r.zone_id,
                    Request.tracking_code == r.tracking_code,

                )).order_by(asc(Request.time)).all()

            if len(sample_ip_and_zone) > 2:
                speed = round((sample_ip_and_zone[-1].time - sample_ip_and_zone[0].time).total_seconds() / (len(sample_ip_and_zone) - 1))
                if speed < 2:
                    r.detected = True
                    db.session.add(r)
                current_app.logger.info(speed)
            db.session.commit()
    return {}


@bp.route("export")
def export():
    import pandas as pd
    import os

    requests = Request.query.all()
    if not os.path.exists("data/bot"):
        os.makedirs("data/bot")
    if not os.path.exists("data/not_predicted"):
        os.makedirs("data/not_predicted")
    if not os.path.exists("data/not_bot"):
        os.makedirs("data/not_bot")
    for r in requests:
        data = (
            MouseEvent.query.filter(MouseEvent.request_hash_id == r.hash_id)
            .with_entities(
                MouseEvent.x_client, MouseEvent.y_client, MouseEvent.timestamp - r.time
            )
            .all()
        )
        if len(data) > 3:
            df = pd.DataFrame(data, columns=["x_client", "y_client", "timestamp"])

            df["timestamp"] = (
                pd.to_timedelta(df["timestamp"]).dt.total_seconds()
            )
            df.to_csv(
                "data/{folder}/{hash_id}.csv".format(
                    folder=r.predetermined_predict_result.value, hash_id=r.hash_id
                ),
                index=False,
                header=True,
            )

    return "success"
