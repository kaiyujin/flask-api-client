from flask import *
import requests
from datetime import timedelta
import logging
import uuid

app = Flask(__name__)
# session
app.permanent_session_lifetime = timedelta(days=6)
app.secret_key = 'hogehoge'
# log
app.logger.setLevel(logging.DEBUG)
log_handler = logging.FileHandler("flask.log")
log_handler.setLevel(logging.DEBUG)
app.logger.addHandler(log_handler)


@app.route("/", methods=["GET"])
def index():
    values = {"domain": "",
              "apiKey": "",
              "clientId": "",
              "clientSecret": ""
              }
    app.logger.info("session token: " + str(session.get("token")))
    return render_template('index.html', data=values)


@app.route("/auth", methods=["POST"])
def auth():
    url = "https://" + request.form.get("domain") + "/auth/token"
    headers = {"content-type": "application/json",
               "x-api-key": request.form.get("apiKey")}
    data = {"clientId": request.form.get("clientId"),
            "clientSecret": request.form.get("clientSecret")}
    res = requests.post(url=url, headers=headers, json=data)
    app.logger.info("res: " + str(res.json()))
    session.permanent = True
    session["token"] = res.json()["accessToken"]
    session["protocolDomain"] = "https://" + request.form.get("domain")
    session["apiKey"] = request.form.get("apiKey")
    return redirect("/shops")


@app.route("/shops", methods=["GET"])
def shops():
    res = requests.get(url=session["protocolDomain"] + "/shops", headers=get_headers())
    app.logger.info("response: " + str(res.json()))
    return render_template('shops.html', data=res.json(), data_text=json.dumps(res.json()))


@app.route("/products", methods=["GET"])
def products():
    params = {"externalShopId": request.args.get("id")}
    res = requests.get(url=session["protocolDomain"] + "/products", headers=get_headers(), params=params)
    app.logger.info("response: " + str(res.json()))
    return render_template('products.html', data=res.json(), data_text=json.dumps(res.json()))


@app.route("/stocks", methods=["GET"])
def stocks():
    params = {"externalProductId": request.args.get("id"),
              "stockPeriodFrom": request.args.get("stockPeriodFrom"),
              "stockPeriodTo": request.args.get("stockPeriodTo")
              }
    res = requests.get(url=session["protocolDomain"] + "/stocks", headers=get_headers(), params=params)
    app.logger.info("response: " + str(res.json()))
    return render_template('stocks.html', data=res.json(), data_text=json.dumps(res.json()))


@app.route("/reserve", methods=["POST"])
def reserve():
    data = {"externalProductId": request.form.get("externalProductId"),
            "useDate": request.form.get("useDate"),
            }
    if request.form.get("useTime"):
        data["useTime"] = request.form.get("useTime")
    prices = [{"quantity": request.form.get("quantity1"), "price": request.form.get("price1")}]
    if request.form.get("quantity2") and request.form.get("price2"):
        prices.append({"quantity": request.form.get("quantity2"), "price": request.form.get("price2")})
    orderer = {"firstName": request.form.get("firstName"), "lastName": request.form.get("lastName")}
    if request.form.get("email"):
        orderer['email'] = request.form.get("email")
    if request.form.get("phoneNumber"):
        orderer['phoneNumber'] = request.form.get("phoneNumber")
    data['prices'] = prices
    data['orderer'] = orderer
    res = requests.post(url=session["protocolDomain"] + "/orders/reserve", headers=get_headers(), json=data)
    app.logger.info("response: " + str(res.json()))
    return render_template('reserved.html', data=res.json(), data_text=json.dumps(res.json()))


@app.route("/release", methods=["POST"])
def release():
    data = {"tentativeOrderId": request.form.get("tentativeOrderId")}
    res = requests.patch(url=session["protocolDomain"] + "/orders/release", headers=get_headers(), json=data)
    app.logger.info("response: " + str(res.json()))
    return render_template('released.html', data=res.json(), data_text=json.dumps(res.json()))


@app.route("/commit", methods=["POST"])
def commit():
    data = {"tentativeOrderId": request.form.get("tentativeOrderId"),
            "externalOrderId": str(uuid.uuid4())
            }
    res = requests.post(url=session["protocolDomain"] + "/orders/commit", headers=get_headers(), json=data)
    app.logger.info("response: " + str(res.json()))
    return render_template('commited.html', data=res.json(), data_text=json.dumps(res.json()))


@app.route("/cancel", methods=["POST"])
def cancel():
    data = {"externalOrderId": request.form.get("externalOrderId")}
    res = requests.patch(url=session["protocolDomain"] + "/orders/cancel", headers=get_headers(), json=data)
    app.logger.info("response: " + str(res.json()))
    return render_template('canceled.html', data=res.json(), data_text=json.dumps(res.json()))


def get_headers():
    return {"content-type": "application/json",
            "x-api-key": session["apiKey"],
            "authorization": "Bearer " + session["token"]
            }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
