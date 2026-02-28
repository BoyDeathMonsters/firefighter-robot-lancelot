import paho.mqtt.client as mqtt
import subprocess

# Stocke le processus en cours
processus = None

# Fonction appelée lors de la réception d'un message
def on_message(client, userdata, message):
    global processus
    commande = message.payload.decode()
    print(f"Commande reçue : {commande}")

    # Démarre le script vérin si la commande est "start"                                                         croix: démarre avance verin
    if commande == "start_verin_avancer":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de verin_avancer.py")
            processus = subprocess.Popen(["python3", "verin_avancer.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script vérin si la commande est "stop"                                                           croix: arrete avance verin
    elif commande == "stop_verin_avancer":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de verin_avancer.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
 
 
     # Démarre le script vérin si la commande est "start"                                                cercle: démarre recule vérin 
    if commande == "start_verin_reculer":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de verin_reculer.py")
            processus = subprocess.Popen(["python3", "verin_reculer.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script vérin si la commande est "stop"                                                 cercle: arrete recule vérin
    elif commande == "stop_verin_reculer":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de verin_reculer.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
            
 # Démarre le script bras L1 si la commande est "start"                                    L1: augmenter joint 2
    elif commande == "start_brasL1":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasL1.py")
            processus = subprocess.Popen(["python3", "brasL1.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasL1 si la commande est "stop"                                    peut etre pas necessaire 
    elif commande == "stop_brasL1":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasL1.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")


# Démarre le script bras L2 si la commande est "start"                                   L2: diminuer joint 2
    elif commande == "start_brasL2":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasL2.py")
            processus = subprocess.Popen(["python3", "brasL2.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasL2 si la commande est "stop"                                      peut etre pas necessaire
    elif commande == "stop_brasL2":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasL2.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
            
# Démarre le script brasR1 si la commande est "start"                                       R1 :augmenter joint 3
    elif commande == "start_brasR1":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasR1.py")
            processus = subprocess.Popen(["python3", "brasR1.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasR1 si la commande est "stop"                                        peut etre pas necessaire
    elif commande == "stop_brasR1":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasR1.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
# Démarre le script brasR2 si la commande est "start"                                       R2: diminuer joint 3
    elif commande == "start_brasR2":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasR2.py")
            processus = subprocess.Popen(["python3", "brasR2.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasR2 si la commande est "stop"                                        peut etre pas necessaire
    elif commande == "stop_brasR2":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasR2.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
# Démarre le script brasO si la commande est "start"                                         O: ouvrir pince démarre
    elif commande == "start_brasO":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasO.py")
            processus = subprocess.Popen(["python3", "brasO.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasO si la commande est "stop"                                       O: ouvrir pince stop
    elif commande == "stop_brasO":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasO.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
            
# Démarre le script brasX si la commande est "start"                                       X: fermer pince start
    elif commande == "start_brasX":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasX.py")
            processus = subprocess.Popen(["python3", "brasX.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasX si la commande est "stop"                                     X: ferme pince stop
    elif commande == "stop_brasX":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasX.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
            
# Démarre le script brascarré si la commande est "start"                                  carré: allume lampe
    elif commande == "start_brascarré":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brascarré.py")
            processus = subprocess.Popen(["python3", "brascarré.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brascarré si la commande est "stop"                               carré: eteint lampe
    elif commande == "stop_brascarré":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brascarré.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
            
# Démarre le script brasfg si la commande est "start"                                  fg: fleche gauche: augmenter joint 1
    elif commande == "start_brasfg":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasfg.py")
            processus = subprocess.Popen(["python3", "brasfg.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasfg si la commande est "stop"                                peut etre pas necessaire
    elif commande == "stop_brasfg":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasfg.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            
# Démarre le script brasfd si la commande est "start"                                  fd: fleche droite: diminuer joint 1
    elif commande == "start_brasfd":
        if processus is None:  # Vérifie si le script tourne déjà
            print("Démarrage de brasfd.py")
            processus = subprocess.Popen(["python3", "brasfd.py"])
        else:
            print("Le script est déjà en cours d'exécution.")
   
    # Arrête le script brasfd si la commande est "stop"                                 peut etre pas necessaire
    elif commande == "stop_brasfd":
        if processus and processus.poll() is None:  # Si le processus est actif
            print("Arrêt de brasfd.py")
            processus.terminate()  # Envoie un signal pour arrêter
            processus.wait()  # Attend l'arrêt complet
            processus = None
        else:
            print("Aucun script en cours à arrêter.")
            


# Connexion au broker MQTT (via ngrok)
broker_address = "5.tcp.eu.ngrok.io"                                      #  à changer 
port = 12014  # Remplace avec ton port ngrok                               # à changer 

client = mqtt.Client()
client.on_message = on_message

client.connect(broker_address, port)
client.subscribe("commande")

print("En attente de commandes...")
client.loop_forever()
