# Question 29 – À quoi sert l'ID token par rapport à l'access token ?

Les deux tokens n'ont pas le même destinataire ni le même rôle :

| | ID token | Access token |
|---|---|---|
| Question à laquelle il répond | **Qui** est l'utilisateur ? | **Qu'a-t-il le droit** de faire ? |
| Destinataire (`aud`) | le frontend (`webapp-frontend`) | l'API (`account`) |
| Protocole | OpenID Connect (authentification) | OAuth 2.0 (autorisation) |
| Envoyé à une API ? | **non** | oui, dans `Authorization: Bearer …` |

## ID token : prouver l'identité au frontend

L'ID token est la **preuve que l'utilisateur s'est bien connecté**. Le frontend le lit pour :
- savoir qui est connecté et **afficher ses informations** (nom, email…) sans appeler d'API ;
- **vérifier que la connexion est légitime** : le `nonce` doit correspondre à celui envoyé dans `/auth`, et `aud` doit être le frontend lui-même ;
- **se déconnecter** : keycloak-js le transmet à Keycloak (`id_token_hint`) lors du `logout()`.

## Access token : accéder à une API

L'access token est une **clé d'accès**. Le frontend ne le lit pas : il l'envoie à l'API, qui le vérifie et regarde les rôles et les scopes pour décider ce que l'utilisateur peut faire.
C'est ce que fait notre route `/api/account`.

## Pourquoi ne pas utiliser un seul token ?

- Envoyer l'ID token à une API serait une erreur : il ne contient ni rôles ni scopes, et son `aud` indique qu'il est destiné au frontend, pas à l'API.
- Utiliser l'access token pour identifier l'utilisateur n'est pas fiable non plus : il est fait pour l'API, son contenu n'est pas garanti pour le frontend, et il peut même être opaque (illisible) selon le serveur.

Chaque token a donc un seul destinataire, ce qui limite les dégâts si l'un des deux est volé ou mal utilisé.
