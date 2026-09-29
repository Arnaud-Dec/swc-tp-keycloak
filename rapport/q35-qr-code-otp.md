# Question 35 – Contenu du QR code OTP

QR code affiché par Keycloak lors de la configuration de la double authentification :

![QR code OTP](QR%20code.png)

Décodé avec un petit script Python (`decodeQr.py`, bibliothèque OpenCV), il contient ce texte :

```
otpauth://totp/webapp:admin-ad?secret=G5JHA33EJQYTSUCWNM4W23CGPFWUU4DO&digits=6&algorithm=SHA1&issuer=webapp&period=30
```

C'est une URL au format `otpauth://`, que les applications d'authentification (Google Authenticator, 2FAS…) savent lire.

## Détail de l'URL

| Partie | Valeur | Signification |
|---|---|---|
| Type | `totp` | *Time-based One-Time Password* : le code change en fonction de l'heure. |
| Libellé | `webapp:admin-ad` | Nom affiché dans l'application : le realm `webapp` et l'utilisateur `admin-ad`. |
| `secret` | `G5JHA33E…` | **La clé secrète** partagée entre Keycloak et le téléphone, encodée en Base32. |
| `digits` | `6` | Le code généré fait 6 chiffres. |
| `algorithm` | `SHA1` | Fonction de hachage utilisée pour calculer le code. |
| `period` | `30` | Un nouveau code est généré toutes les 30 secondes. |
| `issuer` | `webapp` | Qui a émis ce compte OTP (affiché dans l'application). |

## Comment ça marche

Le QR code sert uniquement à **transmettre le secret au téléphone**, une seule fois.
Ensuite, Keycloak et le téléphone calculent chacun le code de leur côté, sans communiquer :

```
code = HMAC-SHA1(secret, heure actuelle / 30 s), réduit à 6 chiffres
```

Comme ils ont le même secret et la même heure, ils obtiennent le même code. Keycloak n'a plus qu'à comparer.

**Conséquence :** ce secret est aussi sensible qu'un mot de passe. Quiconque voit ce QR code peut générer les mêmes codes que le téléphone. C'est pour ça que Keycloak ne l'affiche qu'une seule fois.
