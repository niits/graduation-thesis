import pickle
from datetime import datetime, timedelta

import pandas as pd
from app import create_celery_app
from database import MouseEvent, PredictEnum, Request, db
from detection.mouse_events.feature_extract import extract_feature
from sqlalchemy import and_
from xgboost import XGBClassifier

celery = create_celery_app()


def run_celery():
    celery.worker_main(["", "-B"])


@celery.task(ignore_result=True)
def detect_bots():
    print("Detection: ")

    predict_data = []
    predict_requests = []
    not_extracted_request = []
    requests = Request.query.filter(
        and_(
            Request.time > (datetime.now() - timedelta(minutes=10)),
            Request.predict_result == PredictEnum.not_predicted,
        )
    ).all()
    print("Requests count: {num}".format(num=len(requests)))
    for r in requests:
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
            print(
                "Mouse event series of request {hash_id} is too short".format(
                    hash_id=r.hash_id
                )
            )
            not_extracted_request.append(r.hash_id)
            continue

    print(not_extracted_request)
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

    return not_extracted_request
