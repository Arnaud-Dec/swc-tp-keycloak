# Question 28 – ID token vs access token

ID token récupéré dans la console du navigateur avec `keycloak.idToken`, puis décodé avec jwt.io.
Il a été émis en même temps que l'access token de la question 26.

## Payload de l'ID token

```json
{
  "exp": 1790176856,
  "iat": 1790176556,
  "auth_time": 1790176549,
  "jti": "29aa8da1-ee86-b2da-d0fb-18e6d764ebe8",
  "iss": "http://localhost:8090/realms/webapp",
  "aud": "webapp-frontend",
  "sub": "dcb264c9-0b18-4997-bb5a-27f73c156f09",
  "typ": "ID",
  "azp": "webapp-frontend",
  "nonce": "092b0e6d-69ec-490d-90c7-f28dfc4bfbf3",
  "sid": "JU1821mrlk3zUn8TzZtrhuw7",
  "at_hash": "C6Qr8l14myTWgE3q3w88Zw",
  "acr": "0",
  "email_verified": false,
  "name": "admin admin",
  "preferred_username": "admin-ad",
  "given_name": "admin",
  "family_name": "admin",
  "email": "admin@admin.admin"
}
```

Le header est identique à celui de l'access token (`RS256`, même `kid`) : les deux tokens sont signés avec la même clé.

## Ce qui est pareil

- **Dates** : `iat`, `exp` et `auth_time` sont identiques. L'ID token vaut lui aussi 5 minutes.
- **Émetteur et session** : `iss`, `azp`, `sid` et `acr` sont les mêmes.
- **Utilisateur** : `sub`, `preferred_username`, `email`, `name`, `given_name`, `family_name` et `email_verified` sont les mêmes.

## Ce qui change

| Claim | Access token | ID token | Explication |
|---|---|---|---|
| `typ` | `Bearer` | `ID` | Le type de token. |
| `aud` | `account` | `webapp-frontend` | L'ID token est destiné au **frontend** lui-même, l'access token à une **API**. |
| `jti` | `onrtac:6027…` | `29aa8da1…` | Chaque token a son propre identifiant. |
| `nonce` | absent | `092b0e6d…` | La valeur aléatoire envoyée dans la requête `/auth` : keycloak-js vérifie qu'elle est identique, contre le rejeu. |
| `at_hash` | absent | `C6Qr8l14…` | Empreinte de l'access token : prouve que les deux tokens ont été émis ensemble. |
| `realm_access`, `resource_access` | présents (`is-admin`…) | absents | Les **rôles** servent à autoriser l'accès à une API, pas à identifier l'utilisateur. |
| `scope`, `allowed-origins` | présents | absents | Même raison : ils ne concernent que l'accès aux API. |

**En résumé :** l'ID token décrit **qui est l'utilisateur** (pour le frontend), alors que l'access token dit **ce qu'il a le droit de faire** (pour l'API).
