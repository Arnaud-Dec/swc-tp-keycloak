# Question 27 – Durée de validité de l'access token

La durée de validité se calcule avec deux claims du payload (voir question 26) :

| Claim | Valeur | Heure |
|---|---|---|
| `iat` (création) | `1790176556` | 17:15:56 |
| `exp` (expiration) | `1790176856` | 17:20:56 |

```
exp − iat = 1790176856 − 1790176556 = 300 secondes
300 / 60  = 5 minutes
```

**L'access token est valable 5 minutes.**

C'est la valeur par défaut de Keycloak, modifiable dans *Realm settings* → onglet *Tokens* → *Access Token Lifespan*.
Elle est courte volontairement : si le token est volé, l'attaquant ne peut s'en servir que pendant quelques minutes.
