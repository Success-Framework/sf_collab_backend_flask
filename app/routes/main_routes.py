from flask import Blueprint, current_app

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    endpoints = {}

    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        blueprint = rule.endpoint.split(".")[0]
        endpoints.setdefault(blueprint, set()).add(str(rule))

    return {
        "message": "Flask API is running",
        "version": "1.0.0",
        "endpoints": {
            bp: sorted(paths)
            for bp, paths in endpoints.items()
        }
    }
