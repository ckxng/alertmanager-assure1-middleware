"""alertmanager webhook to assure1 middleware API
"""
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, make_response
from pprint import pformat
from requests import post

load_dotenv()

app = Flask(__name__)
app.config.from_mapping(
    ASSURE1_ENDPOINT=os.environ.get("ASSURE1_ENDPOINT")
)

@app.route("/alert", methods=["POST"])
def alert():
    """recieve an alert from prometheus and forward it to assure1"""
    incoming = None
    if not request.is_json:
        app.logger.debug("recieved non-json payload")
        return make_response(jsonify({
            "error": "Must set Content-Type: application/json"
        }), 400)
    try:
        app.logger.debug("recieved alert payload: %s"%request.data)
        incoming = request.get_json()

    except Exception as e:
        app.logger.error(e)
        return make_response(jsonify({
            "error": "Cannot parse alert"
        }), 500)

    alerts_ok = 0
    alerts_err = 0 

    # send to assure1
    app.logger.debug("parsed incoming data object: %s",pformat(incoming))
    app.logger.debug("number of alerts: %s"%len(incoming.get("alerts")))
    for alert in incoming.get("alerts", []):
        app.logger.debug("parsing alert: %s"%pformat(alert))
        try:
            labels = alert.get("labels")
    
            severity = "4" # warning
            if alert.get("status") == "resolved":
                severity = "0" # ok
            elif labels.get("severity") == "page" or labels.get("severity") == "critical":
                severity = "5" # critical
    
            payload = {
                "node": labels.get("instance", "no node"),
                "team": labels.get("team", "no team"),
                "severity": severity,
                "summary": labels.get("summary", "no summary"),
                "sop_link": labels.get("sop_link", "no sop link"),
                "category": labels.get("category", "no category")
            }

            app.logger.debug("ready to send: %s"%pformat(payload))

            r = post(app.config.get("ASSURE1_ENDPOINT"), data=payload)
            app.logger.debug("response status: %s"%r.status_code)

            alerts_ok = alerts_ok + 1

        except Exception as e:
            # somehow make a note that this happened
            # and give an error back later
            app.logger.error("a single alert could not be handled")
            app.logger.error(e)
            alerts_err = alerts_err + 1


    return make_response(jsonify({
        "result": "ok",
        "alerts_ok": alerts_ok,
        "alerts_err": alerts_err
    }), 200)

if __name__ == "__main__":
    app.run()

