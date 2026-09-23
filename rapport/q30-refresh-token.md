# Question 30 – Refresh token vs access token

Refresh token récupéré dans la console du navigateur avec `keycloak.refreshToken`, puis décodé avec jwt.io.
Il a été émis en même temps que l'access token de la question 26.

## Header

```json
{
  "alg": "HS512",
  "typ": "JWT",
  "kid": "cb44d7eb-426c-43ad-aecf-f51ec0998b1e"
}
```

## Payload

```json
{
  "exp": 1790178356,
  "iat": 1790176556,
  "jti": "e6634f0d-7161-8a50-d70d-cb10f9bedea0",
  "iss": "http://localhost:8090/realms/webapp",
  "aud": "http://localhost:8090/realms/webapp",
  "sub": "dcb264c9-0b18-4997-bb5a-27f73c156f09",
  "typ": "Refresh",
  "azp": "webapp-frontend",
  "sid": "JU1821mrlk3zUn8TzZtrhuw7",
  "scope": "openid basic roles web-origins email acr profile",
  "aud_x": "account",
  "prov": "default"
}
```

## Ce qui est pareil

- `iat` : créé au même moment que l'access token.
- `iss`, `sub`, `azp`, `sid` : même émetteur, même utilisateur, même client et même session.

## Ce qui change

| Claim | Access token | Refresh token | Explication |
|---|---|---|---|
| `alg` (header) | `RS256` | `HS512` | Signature **symétrique** : seul Keycloak connaît la clé, lui seul peut vérifier ce token. L'access token, lui, est vérifiable par n'importe quelle API avec la clé publique. |
| `kid` (header) | `jt1TrUg…` | `cb44d7eb…` | Pas la même clé de signature. |
| `typ` | `Bearer` | `Refresh` | Le type de token. |
| `aud` | `account` | `http://localhost:8090/realms/webapp` | Destiné à **Keycloak lui-même**, pas à une API. |
| `exp` | `1790176856` (17:20:56) | `1790178356` (17:45:56) | Il dure **beaucoup plus longtemps** (voir question 32). |
| `scope` | `openid email profile` | `openid basic roles web-origins email acr profile` | Liste complète des scopes, pour pouvoir recréer un access token identique. |
| Infos utilisateur (`email`, `name`…) | présentes | **absentes** | Il ne sert pas à identifier l'utilisateur. |
| Rôles (`realm_access`…) | présents | **absents** | Il ne donne accès à aucune API. |
| `aud_x`, `prov` | absents | présents | Claims internes à Keycloak. |

**En résumé :** le refresh token contient presque uniquement de quoi retrouver la session (`sub`, `sid`, `scope`). Il ne peut être utilisé que par Keycloak, pour délivrer de nouveaux tokens.
