import enum
from sqlalchemy import Table, Column, Integer, ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

migrate = Migrate()
db = SQLAlchemy()


class PredictEnum(enum.Enum):
    not_predicted = "not_predicted"
    bot = "bot"
    not_bot = "not_bot"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Request(db.Model):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    hash_id = Column(String(256), nullable=False)
    ip_address = Column(String(256), nullable=False)
    referer = Column(String(512))
    bad_referer = Column(Boolean, default=False)
    path = Column(String(256), nullable=False)
    time = Column(DateTime)
    tracking_code = Column(String(256))
    zone_id = Column(String(256))

    click_time = Column(DateTime)

    user_agent = Column(String(256))
    detected = Column(Boolean, default=False)

    predetermined_predict_result = Column(
        Enum(PredictEnum), default=PredictEnum.not_predicted
    )
    predict_result = Column(Enum(PredictEnum), default=PredictEnum.not_predicted)

    fingerprint_uploaded = Column(Boolean, default=False)
    user_agent_inconsistency = Column(Boolean, default=False)
    data_center_ip_address = Column(String(256), default="[]")
    exist_bot_attributes = Column(String(256), default="[]")
    browner_inconsistency = Column(Boolean, default=False)
    os_inconsistency = Column(Boolean, default=False)
    language_inconsistency = Column(Boolean, default=False)
    resolution_inconsistency = Column(Boolean, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def is_bot(self):
        return (
            self.bad_referer == True
            or self.predict_result == PredictEnum.bot
            or (self.data_center_ip_address and self.data_center_ip_address != '[]')
            or (self.exist_bot_attributes and self.exist_bot_attributes != '[]')
            or self.browner_inconsistency
            or self.os_inconsistency
            or self.language_inconsistency
            or self.resolution_inconsistency
            or self.user_agent_inconsistency
        )


class MouseEvent(db.Model):
    __tablename__ = "mouse_events"
    id = Column(Integer, primary_key=True)
    request_hash_id = Column(String(256), nullable=False)
    x_client = Column(Integer)
    y_client = Column(Integer)
    x_window = Column(Integer)
    y_window = Column(Integer)
    event = Column(String(20))
    timestamp = Column(DateTime)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    password = Column(String(100))
    is_admin = Column(Boolean, default=False)
    codes = relationship("TrackingCode", back_populates="user")


class TrackingCode(db.Model):
    __tablename__ = "tracking_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="codes")


class BadReferrerPattern(db.Model):
    __tablename__ = "bad_referrer_pattern"
    id = Column(Integer, primary_key=True)
    pattern = Column(String(1052))


class DataCenterIpRange(db.Model):
    __tablename__ = "ip_ranges"
    id = Column(Integer, primary_key=True)
    cidr = Column(String(64))
    hostmin = Column(String(64))
    hostmax = Column(String(64))
    vendor = Column(String(64))