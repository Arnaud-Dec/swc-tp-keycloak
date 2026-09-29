# Question 40 – Vérifier avec le JWKS ou demander à Keycloak ?

Deux façons pour l'API de savoir si un access token est valide :

| | Demander à Keycloak (`/userinfo`) | Vérifier en local avec le JWKS |
|---|---|---|
| Qui vérifie ? | Keycloak | l'application elle-même |
| Appel réseau à Keycloak | **à chaque requête** | seulement pour récupérer le JWKS (puis mis en cache) |
| Ce qui est vérifié | signature, expiration **et état actuel de la session** | signature et claims du token, **rien de plus** |

## Avantages de la vérification avec le JWKS

- **Performance** : la vérification se fait en local, en quelques calculs, sans attendre de réponse réseau. Keycloak n'est plus sollicité à chaque requête, ce qui compte avec des milliers de requêtes par seconde.
- **Disponibilité** : si Keycloak est lent ou momentanément en panne, l'API continue à accepter les tokens déjà émis.
- **Pas de secret à gérer** : l'application n'utilise que des clés publiques. La clé privée reste uniquement chez Keycloak.

## Faiblesses

- **Pas de révocation immédiate** : l'application ne sait pas ce qui s'est passé depuis la création du token. Si l'utilisateur se déconnecte, si son compte est désactivé ou si on lui retire un rôle, son token reste accepté **jusqu'à son `exp`** (5 minutes ici). Avec `/userinfo`, Keycloak l'aurait refusé tout de suite.
- **Plus de responsabilité pour l'application** : c'est à elle de tout vérifier correctement :
  - la signature, avec la clé qui a le bon `kid` ;
  - `exp` : le token n'est pas expiré ;
  - `iss` : il vient bien du realm `webapp` ;
  - `aud` : il est bien destiné à cette API ;
  - `alg` : il faut imposer `RS256` et refuser le reste (par exemple `none`, un token sans signature).

  Oublier une seule de ces vérifications crée une faille.
- **Gestion des clés publiques** : il faut mettre le JWKS en cache, et le télécharger à nouveau quand Keycloak change de clé (rotation), c'est-à-dire quand un token arrive avec un `kid` inconnu.

## En résumé

La vérification avec le JWKS est **plus rapide et plus robuste**, mais l'application **perd la vision en temps réel** de la session. C'est un compromis acceptable parce que les access tokens sont courts : dans le pire des cas, un token révoqué reste utilisable quelques minutes.
