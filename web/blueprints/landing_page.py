from database import MouseEvent, Request, db, TrackingCode
from flask import Blueprint, render_template, current_app, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc, func
import uuid

bp = Blueprint("landing_page", __name__, url_prefix="/landing_page")


@bp.route("/", methods=["GET"])
def home():
    return render_template("landing_page/home.html")


@bp.route("/shop", methods=["GET"])
def shop():
    return render_template("landing_page/shop.html")
