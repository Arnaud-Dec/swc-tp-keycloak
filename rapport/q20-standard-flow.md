# Question 20 – Diagramme de séquence : Standard flow (Authorization Code + PKCE)

> Keycloak est exposé sur `http://localhost:8090` dans notre environnement (le sujet utilise `8080`).
> Les URLs ci-dessous utilisent donc `8090` ; seul le port change.

## Diagramme

![Diagramme](q20-standard-flow.png)

Source Mermaid (`src/q20-standard-flow.mmd`, config `src/mermaid-config.json`) :

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant B as Navigateur<br/>(index.html + keycloak-js)
    participant F as Webapp Flask<br/>localhost:8081
    participant K as Keycloak<br/>localhost:8090 · realm webapp

    U->>B: Ouvre http://localhost:8081
    B->>F: GET /
    F-->>B: 200 OK — index.html
    Note over B: keycloak.init({ onLoad: "login-required" })<br/>génère state, nonce, code_verifier<br/>code_challenge = BASE64URL(SHA256(code_verifier))

    rect rgb(232, 240, 254)
    Note over B,K: (a) Requête d'autorisation
    B->>K: GET /realms/webapp/protocol/openid-connect/auth
    Note over B,K: client_id=webapp-frontend<br/>redirect_uri=http://localhost:8081/<br/>response_type=code  ·  response_mode=fragment  ·  scope=openid<br/>state=…  ·  nonce=…<br/>code_challenge=…  ·  code_challenge_method=S256
    alt Utilisateur NON connecté (pas de cookie SSO)
        K-->>B: 200 OK — page de login
        U->>B: Saisit identifiant + mot de passe
        B->>K: POST /realms/webapp/login-actions/authenticate
        Note over K: vérifie les identifiants<br/>crée la session SSO
        K-->>B: 302 Found + Set-Cookie (KEYCLOAK_IDENTITY, KEYCLOAK_SESSION)
    else Utilisateur DÉJÀ connecté (cookie SSO valide)
        K-->>B: 302 Found — sans page de login
    end
    Note over B,K: Location: http://localhost:8081/#35;state=…&session_state=…&iss=…&code=…
    end

    B->>F: GET / (le fragment n'est pas envoyé au serveur)
    F-->>B: 200 OK — index.html
    Note over B: lit le fragment, vérifie state<br/>récupère le code, nettoie l'URL

    rect rgb(236, 253, 243)
    Note over B,K: (b) Échange du code contre les tokens
    B->>K: POST /realms/webapp/protocol/openid-connect/token
    Note over B,K: Content-Type: application/x-www-form-urlencoded<br/>grant_type=authorization_code  ·  code=…<br/>client_id=webapp-frontend  ·  redirect_uri=http://localhost:8081/<br/>code_verifier=…
    Note over K: vérifie le code (usage unique),<br/>redirect_uri et SHA256(code_verifier)
    K-->>B: 200 OK — JSON
    Note over B,K: access_token  ·  expires_in: 300  ·  token_type: "Bearer"<br/>refresh_token  ·  refresh_expires_in: 1800<br/>id_token  ·  session_state  ·  scope: "openid email profile"
    Note over B: vérifie le nonce de l'id_token<br/>authenticated = true
    end

    rect rgb(245, 243, 255)
    Note over B,K: Utilisation du token
    B->>F: GET /api/account — Authorization: Bearer
    F->>K: GET /userinfo — Authorization: Bearer
    K-->>F: 200 OK — sub, email… (401 si invalide)
    F-->>B: 200 OK — { balance }
    B-->>U: « Bienvenue <email>, balance : … € »
    end
```

## (a) Requête `GET …/openid-connect/auth`

| Paramètre | Valeur | Rôle |
|---|---|---|
| `client_id` | `webapp-frontend` | Client Keycloak qui demande l'authentification (client public, sans secret). |
| `redirect_uri` | `http://localhost:8081/` | Adresse où Keycloak renvoie le navigateur. Elle doit correspondre aux *Valid redirect URIs* (`http://localhost:8081/*`). |
| `response_type` | `code` | Indique le Standard flow : Keycloak renvoie un **code d'autorisation**, pas un token. |
| `response_mode` | `fragment` | Le code est renvoyé dans le fragment `#…` de l'URL, donc jamais envoyé au serveur Flask. |
| `scope` | `openid` | Demande une authentification OpenID Connect, qui produit un `id_token`. |
| `state` | valeur aléatoire | Protection CSRF : keycloak-js vérifie qu'il retrouve la même valeur au retour. |
| `nonce` | valeur aléatoire | Protection contre le rejeu : la valeur est recopiée dans l'`id_token`, puis vérifiée. |
| `code_challenge` | `BASE64URL(SHA256(code_verifier))` | PKCE : empêche un tiers qui intercepterait le code de l'utiliser. |
| `code_challenge_method` | `S256` | Méthode de hachage PKCE. |

**Code HTTP de la réponse :**
- **Utilisateur non connecté** : `200 OK`, avec la page de login de Keycloak. L'envoi du formulaire (`POST …/login-actions/authenticate`) renvoie ensuite `302 Found` vers `redirect_uri#state=…&session_state=…&iss=…&code=…` et pose les cookies de session SSO.
- **Utilisateur déjà connecté** (cookie `KEYCLOAK_IDENTITY` valide) : `302 Found` directement vers `redirect_uri#…&code=…`, sans demander d'identifiants.

## (b) Requête `POST …/openid-connect/token`

Paramètres envoyés dans le corps `application/x-www-form-urlencoded` :

| Paramètre | Valeur | Rôle |
|---|---|---|
| `grant_type` | `authorization_code` | Échange d'un code d'autorisation contre des tokens. |
| `code` | code reçu à l'étape (a) | Code à usage unique, valable très peu de temps (environ 1 minute). |
| `client_id` | `webapp-frontend` | Doit être le même client que celui de la requête `/auth`. |
| `redirect_uri` | `http://localhost:8081/` | Doit être identique à celui de la requête `/auth`. |
| `code_verifier` | valeur aléatoire générée au départ | PKCE : Keycloak vérifie que `SHA256(code_verifier)` est égal au `code_challenge` reçu. |

> Pas de `client_secret`, car `webapp-frontend` est un client public (*Client authentication* → OFF).

Contenu de la réponse (`200 OK`, JSON) :

| Champ | Contenu |
|---|---|
| `access_token` | JWT à envoyer à l'API dans `Authorization: Bearer …`. |
| `expires_in` | Durée de validité de l'access token en secondes (300 s par défaut). |
| `refresh_token` | Token permettant d'obtenir un nouvel access token sans se reconnecter. |
| `refresh_expires_in` | Durée de validité du refresh token en secondes (1800 s par défaut). |
| `id_token` | JWT décrivant l'identité de l'utilisateur (email, nom, …) pour le frontend. |
| `token_type` | `Bearer`. |
| `not-before-policy` | Date avant laquelle les tokens sont refusés (révocation). |
| `session_state` | Identifiant de la session SSO Keycloak. |
| `scope` | Scopes accordés (`openid email profile`). |
