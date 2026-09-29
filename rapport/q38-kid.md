# Question 38 – Le claim `kid` du header

Header de l'access token décodé avec jwt.io (voir question 26) :

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "jt1TrUgJONgjeb3u13e8mAXGDMNmozP5kpQKmPhqS9Q"
}
```

## Signification

`kid` signifie ***Key ID*** : c'est l'**identifiant de la clé** qui a servi à signer le token.

Keycloak ne possède pas une seule clé, mais plusieurs (voir question 39). Pour vérifier la signature d'un token, une application doit savoir **laquelle utiliser**. Le `kid` le lui dit :

1. l'application lit le `kid` dans le header du token ;
2. elle cherche la clé qui a le même `kid` dans la liste des clés publiques de Keycloak (le JWKS) ;
3. elle vérifie la signature avec cette clé.

## Pourquoi c'est utile

- **Plusieurs clés en même temps** : un realm peut avoir des clés pour différents usages (signature, chiffrement) ou différents algorithmes. Le `kid` évite toute ambiguïté.
- **Changement de clé (rotation)** : pour des raisons de sécurité, on change régulièrement les clés. Pendant la transition, l'ancienne et la nouvelle clé coexistent. Les anciens tokens gardent l'ancien `kid` et restent vérifiables, les nouveaux utilisent le nouveau `kid`.

Le `kid` n'est pas secret : c'est juste une étiquette, pas la clé elle-même.
