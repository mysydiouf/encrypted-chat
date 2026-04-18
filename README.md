# Encrypted Chat

Chat en réseau avec chiffrement XOR. Un serveur gère plusieurs clients qui peuvent s'envoyer des messages chiffrés en temps réel.

## Ce que ça fait

- Serveur multi-clients avec des threads (chaque client a son propre thread)
- Chiffrement XOR des messages avec une clé partagée
- Les messages transitent chiffrés sur le réseau, illisibles sans la clé
- Commandes : `/help`, `/quit`, `/whoami`, `/raw` (envoyer en clair pour comparer)
- Le serveur affiche les connexions/déconnexions en temps réel

## Architecture

```
Client A  ──chiffre──>  Serveur  ──transmet──>  Client B
                                                  │
                                              dechiffre
                                                  │
                                            message clair
```

Le serveur ne fait que redistribuer les messages. Il ne les déchiffre pas, il ne voit que du texte chiffré. C'est les clients qui chiffrent avant d'envoyer et déchiffrent à la réception.

## Lancer

Terminal 1 - le serveur :
```bash
python3 server.py
```

Terminal 2 - un client :
```bash
python3 client.py
```

Terminal 3 - un autre client :
```bash
python3 client.py
```

Python 3.8+, pas de dépendance externe.

Pour tester sur la même machine, laisser l'adresse par défaut (127.0.0.1). Pour tester entre deux machines sur le même réseau, mettre l'IP locale du serveur.

## Demo du chiffrement

Si tu veux juste voir le chiffrement XOR en action sans lancer le serveur :

```bash
python3 demo_chiffrement.py
```

```
  Cle utilisee : 'cle-secrete-chat-2026'

  Message original  : Bonjour tout le monde
  Message chiffre   : IwoCHgQVEBxYFBkMBBQYWBQVBBg=
  Message dechiffre : Bonjour tout le monde
  OK : True

  --- Tentative avec une mauvaise cle ---

  Message original     : Information confidentielle
  Dechiffre (bonne cle): Information confidentielle
  Dechiffre (mauvaise) : )"6;c=3!+>d8>'b0&!63>>
  -> Sans la bonne cle, le message est illisible
```

## Comment marche le chiffrement XOR

XOR (ou exclusif) c'est une operation binaire : on compare chaque bit du message avec un bit de la clé.

```
message:  01001000  (H)
cle:      01101001  (i)
XOR:      00100001  (!)
```

La propriété du XOR c'est qu'il est reversible : si on refait XOR avec la même clé sur le résultat, on retrouve le message original. C'est le même principe que le chiffre de Vernam (one-time pad).

La limite ici c'est que la clé est plus courte que le message, donc on la répète. En vrai, pour que ce soit solide, il faudrait une clé aussi longue que le message (ou utiliser AES).

## Limites et améliorations possibles

- La clé est en dur dans le code, il faudrait un échange de clés (Diffie-Hellman)
- XOR avec une clé répétée c'est cassable avec une analyse fréquentielle
- Pas d'authentification des clients
- En prod il faudrait utiliser AES ou TLS directement

## Fichiers

```
encrypted-chat/
├── server.py              # serveur multi-clients
├── client.py              # client avec chiffrement
├── demo_chiffrement.py    # demo du XOR sans serveur
└── README.md
```

## Auteur

Sokhna Oumou Diouf
