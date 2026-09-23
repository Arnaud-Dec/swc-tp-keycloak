# Question 24 – Standard flow ou Implicit flow ?

## Comparaison

| | Standard flow | Implicit flow |
|---|---|---|
| Ce que renvoie `/auth` | un **code** à usage unique | directement les **tokens** |
| Requête `/token` | oui, pour échanger le code | non |
| Tokens visibles dans l'URL | non | oui |
| PKCE | oui | non |
| `refresh_token` | oui | non |
| Nombre de requêtes | une de plus | une de moins |

## Standard flow

**Avantages**
- Les tokens ne passent jamais dans l'URL : ils arrivent dans le corps de la réponse `/token`.
- Un code intercepté ne sert à rien : il est à usage unique, expire vite, et PKCE exige le `code_verifier` que seul le navigateur connaît.
- Le `refresh_token` permet de rester connecté sans refaire de redirection vers Keycloak.

**Faiblesses**
- Un aller-retour de plus avec Keycloak.
- Un peu plus complexe à implémenter (mais keycloak-js le fait pour nous).

## Implicit flow

**Avantages**
- Plus simple : une seule redirection suffit pour obtenir les tokens.
- Historiquement pensé pour les applications 100 % navigateur, à une époque où les appels entre domaines (CORS) vers `/token` n'étaient pas possibles.

**Faiblesses**
- Les tokens sont dans l'URL : ils peuvent fuiter via l'historique du navigateur, les logs, une extension ou un script malveillant (XSS).
- Pas de PKCE : un attaquant qui récupère la redirection obtient directement un token utilisable.
- Pas de `refresh_token` : à expiration, il faut repasser par Keycloak.

## Lequel utiliser en production ?

**Le Standard flow avec PKCE.**

L'Implicit flow est aujourd'hui déconseillé par les recommandations de sécurité OAuth 2.0 (RFC 9700) et a été retiré d'OAuth 2.1. La raison qui le justifiait (pas de CORS) n'existe plus, et PKCE rend le Standard flow sûr même pour un client public comme notre frontend.
