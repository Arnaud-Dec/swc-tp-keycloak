# Question 23 – Diagramme de séquence : Implicit flow

> Keycloak est exposé sur `http://localhost:8090` dans notre environnement (le sujet utilise `8080`).
> Configuration : client `webapp-frontend` avec *Implicit flow* coché (et *Standard flow* décoché),
> et `keycloak.init({ onLoad: "login-required", flow: "implicit" })`.

## Diagramme

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant B as Navigateur<br/>(index.html + keycloak-js)
    participant F as Webapp Flask<br/>localhost:8081
    participant K as Keycloak<br/>localhost:8090 (realm webapp)

    U->>B: Ouvre http://localhost:8081
    B->>F: GET /
    F-->>B: 200 OK (index.html)
    B->>B: new Keycloak({url, realm, clientId})<br/>init({ onLoad: "login-required", flow: "implicit" })<br/>génère state, nonce (pas de PKCE)

    Note over B,K: (a) Requête d'autorisation
    B->>K: GET /realms/webapp/protocol/openid-connect/auth<br/>?client_id=webapp-frontend<br/>&redirect_uri=http://localhost:8081/<br/>&response_type=id_token token<br/>&response_mode=fragment<br/>&scope=openid<br/>&state=…&nonce=…

    alt Utilisateur NON connecté (pas de cookie de session Keycloak)
        K-->>B: 200 OK — page de login HTML
        U->>B: Saisit login + mot de passe
        B->>K: POST /realms/webapp/login-actions/authenticate?…<br/>(username, password)
        K->>K: Vérifie les identifiants, crée la session SSO
        K-->>B: 302 Found<br/>Set-Cookie: KEYCLOAK_IDENTITY, KEYCLOAK_SESSION<br/>Location: http://localhost:8081/#35;state=…&session_state=…&iss=…<br/>&access_token=eyJ…&token_type=Bearer<br/>&id_token=eyJ…&expires_in=300
    else Utilisateur DÉJÀ connecté (cookie de session SSO valide)
        K-->>B: 302 Found (pas de page de login)<br/>Location: http://localhost:8081/#35;state=…&session_state=…&iss=…<br/>&access_token=eyJ…&token_type=Bearer<br/>&id_token=eyJ…&expires_in=300
    end

    B->>F: GET / (le fragment #35;… n'est pas envoyé au serveur)
    F-->>B: 200 OK (index.html)
    B->>B: keycloak-js lit le fragment, vérifie state et le nonce de l'id_token,<br/>stocke access_token + id_token, nettoie l'URL<br/>authenticated = true

    Note over B,K: (b) AUCUNE requête vers /openid-connect/token<br/>les tokens ont été reçus directement dans l'URL (pas de refresh_token)

    Note over B,K: Utilisation du token (appel API)
    B->>F: GET /api/account<br/>Authorization: Bearer <access_token>
    F->>K: GET http://keycloak:8080/realms/webapp/protocol/openid-connect/userinfo<br/>Authorization: Bearer <access_token>
    K-->>F: 200 OK { sub, email, preferred_username, … }<br/>(401 si le token est invalide ou expiré)
    F-->>B: 200 OK { "balance": … }
    B-->>U: « Bienvenue <email>, balance : … € »

    Note over B,K: À expiration de l'access token (300 s) : pas de refresh_token,<br/>il faut refaire la requête /auth (reconnexion silencieuse via le cookie SSO)
```

## Les 2 requêtes étudiées en Standard flow

### (a) `GET …/openid-connect/auth` : toujours présente, avec d'autres paramètres

| Paramètre | Standard flow | Implicit flow |
|---|---|---|
| `client_id` | `webapp-frontend` | `webapp-frontend` |
| `redirect_uri` | `http://localhost:8081/` | `http://localhost:8081/` |
| `response_type` | `code` | **`id_token token`** : on demande directement les tokens |
| `response_mode` | `fragment` | `fragment` |
| `scope` | `openid` | `openid` |
| `state` / `nonce` | oui | oui (le `nonce` est obligatoire en implicit) |
| `code_challenge` (PKCE) | oui | **non** : il n'y a pas de code à protéger |

**Codes HTTP :** les mêmes qu'en Standard flow.
- Utilisateur non connecté : `200` avec la page de login, puis `302` après l'envoi du formulaire.
- Utilisateur déjà connecté : `302` direct.

La différence est dans le contenu du `Location` de la redirection. Il contient directement
`access_token`, `id_token`, `token_type`, `expires_in` (avec `state`, `session_state`, `iss`),
au lieu d'un simple `code`.

### (b) `POST …/openid-connect/token` : n'existe plus

Il n'y a aucun échange de code contre des tokens, puisque les tokens arrivent dès la redirection de l'étape (a). Conséquences :
- **pas de `refresh_token`** : à l'expiration de l'access token, il faut repasser par `/auth` ;
- les tokens circulent **dans l'URL**, où ils peuvent se retrouver dans l'historique du navigateur, dans le header `Referer`, ou être lus par une extension ou un script injecté (XSS) ;
- pas de PKCE, donc aucune preuve que l'application qui reçoit les tokens est bien celle qui les a demandés.
