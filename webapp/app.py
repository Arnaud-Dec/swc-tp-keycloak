
from flask import Flask, render_template, request
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError
import os
import jwt

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Balances (accounts) of users (in euros)
users_balances = {
    "admin": 120.00,
    "admin-ad": 130.00,
    "john":  17.53,
}

server_url=os.getenv("KEYCLOAK_URL")

# keycloak_openid = KeycloakOpenID(server_url,
#                                  realm_name=os.getenv("KEYCLOAK_REALM"),
#                                  client_id=os.getenv("KEYCLOAK_BACKEND_CLIENT_ID"),
#                                  client_secret_key=os.getenv("KEYCLOAK_BACKEND_CLIENT_SECRET"))

jwks_client = jwt.PyJWKClient( server_url + "/realms/webapp/protocol/openid-connect/certs")

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/account")
def api_account():
    # a. Récupérer le JWT dans le header "Authorization" (format : "Bearer <token>")
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {"error": "Missing or invalid Authorization header"}, 401
    token = auth_header[len("Bearer "):]

    # b. Vérifier la validité du JWT en local
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(token, signing_key.key, algorithms=["RS256"], audience="account", issuer="http://localhost:8090/realms/webapp")
    except jwt.PyJWTError:
        return {"error": "Invalid or expired token"}, 401

    # # b. Vérifier la validité du JWT auprès de Keycloak et extraire les infos de l'utilisateur
    # try:
    #     userinfo = keycloak_openid.userinfo(token)
    # except KeycloakError:
    #     return {"error": "Invalid or expired token"}, 401

    # c. Retourner la balance associée à l'utilisateur
    username = payload.get("preferred_username")
    if username not in users_balances:
        return {"error": f"No account for user {username}"}, 404
    return {"username": username, "balance": users_balances[username]}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
