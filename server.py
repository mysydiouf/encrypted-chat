#!/usr/bin/env python3
"""
Serveur de chat chiffre
Sokhna Oumou Diouf

Gere les connexions de plusieurs clients en meme temps
et transmet les messages chiffres entre eux.
"""

import socket
import threading
import sys
from datetime import datetime

# config du serveur
HOST = "0.0.0.0"  # ecoute sur toutes les interfaces
PORT = 5555
MAX_CLIENTS = 10

# stocke les clients connectes : {socket: pseudo}
clients = {}
lock = threading.Lock()  # pour eviter les problemes d'acces concurrent


def log(msg):
    """Affiche un message avec l'heure"""
    heure = datetime.now().strftime("%H:%M:%S")
    print(f"  [{heure}] {msg}")


def broadcast(message, expediteur=None):
    """
    Envoie un message a tous les clients connectes
    sauf a l'expediteur (pour pas qu'il recoive son propre message)
    """
    with lock:
        deconnectes = []
        for client_socket in clients:
            if client_socket != expediteur:
                try:
                    client_socket.send(message.encode("utf-8"))
                except:
                    deconnectes.append(client_socket)

        # nettoyer les clients qui ont plante
        for c in deconnectes:
            pseudo = clients.pop(c, "?")
            log(f"{pseudo} deconnecte (erreur)")


def gerer_client(client_socket, adresse):
    """
    Fonction executee dans un thread separe pour chaque client.
    Recoit les messages du client et les redistribue aux autres.
    """
    pseudo = None

    try:
        # premiere chose : le client envoie son pseudo
        pseudo = client_socket.recv(1024).decode("utf-8").strip()
        if not pseudo:
            client_socket.close()
            return

        with lock:
            clients[client_socket] = pseudo

        log(f"{pseudo} s'est connecte depuis {adresse[0]}:{adresse[1]}")
        broadcast(f"[serveur] {pseudo} a rejoint le chat", client_socket)

        # boucle principale : on recoit et on redistribue
        while True:
            data = client_socket.recv(4096)
            if not data:
                break

            message = data.decode("utf-8")
            log(f"{pseudo}: {message[:50]}...")  # log tronque
            broadcast(f"{pseudo}: {message}", client_socket)

    except ConnectionResetError:
        pass
    except Exception as e:
        log(f"Erreur avec {pseudo}: {e}")
    finally:
        # deconnexion propre
        with lock:
            if client_socket in clients:
                del clients[client_socket]
        client_socket.close()

        if pseudo:
            log(f"{pseudo} s'est deconnecte")
            broadcast(f"[serveur] {pseudo} a quitte le chat")


def demarrer_serveur():
    """Lance le serveur et accepte les connexions entrantes"""
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        serveur.bind((HOST, PORT))
    except OSError as e:
        print(f"[!] Impossible de lancer le serveur sur le port {PORT}: {e}")
        sys.exit(1)

    serveur.listen(MAX_CLIENTS)
    log(f"Serveur demarre sur {HOST}:{PORT}")
    log(f"En attente de connexions (max {MAX_CLIENTS})...")
    print()

    try:
        while True:
            client_socket, adresse = serveur.accept()

            # on verifie qu'on a pas trop de clients
            with lock:
                if len(clients) >= MAX_CLIENTS:
                    client_socket.send("Serveur plein, reessaye plus tard".encode())
                    client_socket.close()
                    continue

            # on lance un thread pour ce client
            t = threading.Thread(target=gerer_client, args=(client_socket, adresse))
            t.daemon = True  # le thread s'arrete quand le serveur s'arrete
            t.start()

    except KeyboardInterrupt:
        log("Arret du serveur...")
        # on previent tout le monde
        broadcast("[serveur] Le serveur s'arrete")
        with lock:
            for c in clients:
                c.close()
        serveur.close()


if __name__ == "__main__":
    print("\n  === CHAT SERVER ===\n")
    demarrer_serveur()
