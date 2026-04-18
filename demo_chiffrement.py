#!/usr/bin/env python3
"""
Demo du chiffrement XOR
Pour montrer comment ca marche sans lancer le serveur
"""

import base64

CLE = "cle-secrete-chat-2026"


def xor_chiffrement(message, cle):
    resultat = []
    for i, char in enumerate(message):
        char_cle = cle[i % len(cle)]
        char_chiffre = chr(ord(char) ^ ord(char_cle))
        resultat.append(char_chiffre)
    return base64.b64encode("".join(resultat).encode("utf-8")).decode("utf-8")


def xor_dechiffrement(message_b64, cle):
    texte = base64.b64decode(message_b64.encode("utf-8")).decode("utf-8")
    resultat = []
    for i, char in enumerate(texte):
        char_cle = cle[i % len(cle)]
        resultat.append(chr(ord(char) ^ ord(char_cle)))
    return "".join(resultat)


print("\n  === DEMO CHIFFREMENT XOR ===\n")
print(f"  Cle utilisee : '{CLE}'\n")

messages = [
    "Bonjour tout le monde",
    "Le mot de passe du serveur est admin123",
    "RDV a 14h pour le deploiement",
]

for msg in messages:
    chiffre = xor_chiffrement(msg, CLE)
    dechiffre = xor_dechiffrement(chiffre, CLE)

    print(f"  Message original  : {msg}")
    print(f"  Message chiffre   : {chiffre}")
    print(f"  Message dechiffre : {dechiffre}")
    print(f"  OK : {msg == dechiffre}")
    print()

# demo avec la mauvaise cle
print("  --- Tentative avec une mauvaise cle ---\n")
msg = "Information confidentielle"
chiffre = xor_chiffrement(msg, CLE)
mauvais = xor_dechiffrement(chiffre, "mauvaise-cle")

print(f"  Message original     : {msg}")
print(f"  Chiffre              : {chiffre}")
print(f"  Dechiffre (bonne cle): {xor_dechiffrement(chiffre, CLE)}")
print(f"  Dechiffre (mauvaise) : {mauvais}")
print(f"  -> Sans la bonne cle, le message est illisible\n")
