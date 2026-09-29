# Question 31 – À quoi sert le refresh token par rapport à l'access token ?

L'access token ne dure que 5 minutes. Sans refresh token, l'utilisateur devrait se reconnecter toutes les 5 minutes.
Le refresh token permet d'**obtenir un nouvel access token sans redemander le mot de passe**.

## Comment ça marche

Quand l'access token expire, le frontend envoie le refresh token à Keycloak :

```
POST /realms/webapp/protocol/openid-connect/token
grant_type=refresh_token
refresh_token=eyJ…
client_id=webapp-frontend
```

Keycloak vérifie que la session (`sid`) est toujours active, puis renvoie un **nouvel access token**, un **nouvel ID token** et un **nouveau refresh token**.

Avec keycloak-js, c'est la fonction `keycloak.updateToken()` qui s'en charge.

## Deux tokens, deux rôles

| | Access token | Refresh token |
|---|---|---|
| Sert à | appeler une **API** | obtenir un **nouvel access token** |
| Envoyé à | l'API (`/api/account`) | Keycloak uniquement (`/token`) |
| Durée | courte (5 min) | plus longue (30 min) |
| Vérifiable par | n'importe quelle API (clé publique) | Keycloak seul (clé secrète) |

## Pourquoi c'est plus sûr

- **L'access token circule beaucoup** (à chaque appel d'API) : on le garde court, pour qu'un token volé ne soit utilisable que quelques minutes.
- **Le refresh token ne circule presque pas** (uniquement vers Keycloak, de temps en temps) : il est moins exposé, donc il peut durer plus longtemps.
- **Keycloak garde le contrôle** : à chaque renouvellement, il vérifie que la session existe toujours. Si l'utilisateur se déconnecte ou si un administrateur ferme sa session, le refresh token ne marche plus, et aucun nouvel access token n'est délivré.

On a donc à la fois une bonne sécurité (tokens d'accès courts) et un bon confort (pas de reconnexion toutes les 5 minutes).
