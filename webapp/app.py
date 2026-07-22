
from flask import Flask, render_template
from keycloak import KeycloakOpenID
import os

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Balances (accounts) of users (in euros)
users_balances = {
    "admin": 120.00,
    "john":  17.53,
}

keycloak_openid = KeycloakOpenID(server_url=os.getenv("KEYCLOAK_URL"),
                                 realm_name=os.getenv("KEYCLOAK_REALM"),
                                 client_id=os.getenv("KEYCLOAK_BACKEND_CLIENT_ID"),
                                 client_secret_key=os.getenv("KEYCLOAK_BACKEND_CLIENT_SECRET"))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/account")
def api_account():
    # TODO
    return {"error": "This API endpoint is not implemented yet"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
