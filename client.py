#!/usr/bin/env python3
"""
Client de chat avec chiffrement
Sokhna Oumou Diouf

Se connecte au serveur et permet d'envoyer/recevoir
des messages chiffres avec les autres utilisateurs.

Le chiffrement utilise XOR avec une cle partagee.
C'est pas le plus solide mais ca montre le principe :
sans la cle, les messages interceptes sont illisibles.
"""

import socket
import threading
import sys
import base64

# cle de chiffrement partagee entre tous les clients
# en vrai il faudrait un echange de cles (Diffie-Hellman par ex)
# mais la c'est pour montrer le principe
CLE = "cle-secrete-chat-2026"


def xor_chiffrement(message, cle):
    """
    Chiffre/dechiffre un message avec XOR.

    Le XOR c'est une operation binaire :
    - si on fait message XOR cle, on obtient le message chiffre
    - si on refait chiffre XOR cle, on retrouve le message original

    C'est le meme principe que le one-time pad,
    sauf qu'ici la cle est plus courte que le message
    donc on la repete (ce qui est moins securise).
    """
    resultat = []
    for i, char in enumerate(message):
        # on XOR chaque caractere du message avec un caractere de la cle
        # on boucle sur la cle avec modulo
        char_cle = cle[i % len(cle)]
        char_chiffre = chr(ord(char) ^ ord(char_cle))
        resultat.append(char_chiffre)

    texte_chiffre = "".join(resultat)

    # on encode en base64 pour pouvoir l'envoyer sur le reseau
    # (sinon les caracteres speciaux posent probleme)
    return base64.b64encode(texte_chiffre.encode("utf-8")).decode("utf-8")


def xor_dechiffrement(message_b64, cle):
    """Dechiffre un message chiffre en XOR + base64"""
    try:
        texte_chiffre = base64.b64decode(message_b64.encode("utf-8")).decode("utf-8")

        resultat = []
        for i, char in enumerate(texte_chiffre):
            char_cle = cle[i % len(cle)]
            char_dechiffre = chr(ord(char) ^ ord(char_cle))
            resultat.append(char_dechiffre)

        return "".join(resultat)
    except:
        # si le dechiffrement foire, on renvoie tel quel
        return message_b64


def recevoir_messages(client_socket):
    """
    Tourne dans un thread separe.
    Ecoute en permanence les messages du serveur et les affiche.
    """
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                print("\n  [!] Connexion perdue avec le serveur")
                break

            message = data.decode("utf-8")

            # les messages du serveur (join/quit) sont pas chiffres
            if message.startswith("[serveur]"):
                print(f"\n  {message}")
            else:
                # format : "pseudo: message_chiffre"
                # on separe le pseudo du contenu
                if ": " in message:
                    pseudo, contenu = message.split(": ", 1)
                    contenu_clair = xor_dechiffrement(contenu, CLE)
                    print(f"\n  {pseudo}: {contenu_clair}")
                else:
                    print(f"\n  {message}")

            # remettre le prompt
            print("  > ", end="", flush=True)

        except ConnectionResetError:
            print("\n  [!] Le serveur s'est arrete")
            break
        except Exception as e:
            print(f"\n  [!] Erreur: {e}")
            break

    client_socket.close()
    sys.exit(0)


def afficher_aide():
    print("\n  Commandes :")
    print("  /quit     - quitter le chat")
    print("  /whoami   - afficher ton pseudo")
    print("  /help     - afficher cette aide")
    print("  /raw <msg> - envoyer sans chiffrement (pour comparer)")
    print()


def demarrer_client():
    """Connexion au serveur et boucle d'envoi"""
    host = input("  Adresse du serveur (defaut: 127.0.0.1) : ").strip()
    if not host:
        host = "127.0.0.1"

    port_str = input("  Port (defaut: 5555) : ").strip()
    port = int(port_str) if port_str else 5555

    pseudo = input("  Ton pseudo : ").strip()
    if not pseudo:
        print("  [!] Pseudo vide")
        return

    # connexion
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except ConnectionRefusedError:
        print(f"\n  [!] Impossible de se connecter a {host}:{port}")
        print("  Verifie que le serveur est lance")
        return
    except Exception as e:
        print(f"\n  [!] Erreur de connexion: {e}")
        return

    # envoyer le pseudo au serveur
    client_socket.send(pseudo.encode("utf-8"))

    print(f"\n  Connecte au serveur {host}:{port} en tant que '{pseudo}'")
    print(f"  Chiffrement XOR actif (cle: {CLE[:8]}...)")
    print(f"  Tape /help pour les commandes\n")

    # lancer le thread de reception
    t = threading.Thread(target=recevoir_messages, args=(client_socket,))
    t.daemon = True
    t.start()

    # boucle d'envoi
    try:
        while True:
            print("  > ", end="", flush=True)
            message = input()

            if not message:
                continue

            if message == "/quit":
                print("  Deconnexion...")
                break

            elif message == "/whoami":
                print(f"  Tu es {pseudo}")
                continue

            elif message == "/help":
                afficher_aide()
                continue

            elif message.startswith("/raw "):
                # envoi sans chiffrement pour montrer la difference
                msg_brut = message[5:]
                client_socket.send(msg_brut.encode("utf-8"))
                print(f"  (envoye en clair: '{msg_brut}')")
                continue

            # chiffrer et envoyer
            message_chiffre = xor_chiffrement(message, CLE)
            client_socket.send(message_chiffre.encode("utf-8"))

            # montrer ce qui est envoye sur le reseau
            print(f"  (chiffre: {message_chiffre[:40]}...)")

    except (KeyboardInterrupt, EOFError):
        print("\n  Deconnexion...")
    finally:
        client_socket.close()


if __name__ == "__main__":
    print("\n  === CHAT CLIENT (chiffre) ===\n")
    demarrer_client()
