# Question 32 – Durée de validité du refresh token

La durée de validité se calcule avec deux claims du payload (voir question 30) :

| Claim | Valeur | Heure |
|---|---|---|
| `iat` (création) | `1790176556` | 17:15:56 |
| `exp` (expiration) | `1790178356` | 17:45:56 |

```
exp − iat = 1790178356 − 1790176556 = 1800 secondes
1800 / 60 = 30 minutes
```

**Le refresh token est valable 30 minutes.**

## Comparaison avec l'access token

| | Access token | Refresh token |
|---|---|---|
| Durée | 300 s = **5 minutes** | 1800 s = **30 minutes** |

Le refresh token dure **6 fois plus longtemps** que l'access token.
Pendant ces 30 minutes, le frontend peut donc renouveler l'access token (toutes les 5 minutes) sans que l'utilisateur ait à se reconnecter.

Dans Keycloak, cette durée correspond au réglage *SSO Session Idle* (*Realm settings* → onglet *Sessions*) : si l'utilisateur reste inactif plus de 30 minutes, sa session expire et il doit se reconnecter.
