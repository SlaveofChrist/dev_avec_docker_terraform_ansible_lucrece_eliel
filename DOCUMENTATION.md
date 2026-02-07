# Documentation Technique

Ce document détaille l'architecture, les choix techniques et les procédures d'opération pour le projet Starter DevOps.

## 1. Architecture Infrastructure (Terraform)

Le fichier `main.tf` définit les ressources AWS nécessaires.

### Ressources Déployées
- **AWS Instance (EC2)** : Type `t3.micro` (offre gratuite éligible), image **Ubuntu 24.04 LTS**.
  - Disque : 30 Go GP3.
- **Security Group** : Pare-feu autorisant les flux suivants :
  - `TCP/22` (SSH) : Administration.
  - `TCP/8080` (Frontend) : Accès web utilisateur.
  - `TCP/8000` (API) : Accès API REST.
  - `TCP/5432` (PostgreSQL) : Accès base de données direct.
  - `TCP/6379` (Redis) : Accès cache direct.
  - *Note : Dans un environnement de production, les ports 5432 et 6379 ne devraient pas être exposés sur `0.0.0.0/0`.*
- **Key Pair** : Une paire de clés SSH (`app-key-terraform`) est générée dynamiquement. La clé privée est sauvegardée localement dans `app-key-terraform.pem` (permissions 0400).

## 2. Architecture Applicative (Docker)

L'application est définie dans `docker-compose.yml` et comprend 4 services interconnectés.

### Services

#### 1. Frontend (`frontend`)
- **Image** : `nginx:alpine`
- **Configuration** : Sert les fichiers statiques montés depuis le dossier `./frontend`.
- **Port** : Exposé sur le port hôte `8080` (mappé vers 80).
- **Volume** : Montage en lecture seule (`:ro`) pour la sécurité.

#### 2. Base de Données (`db`)
- **Image** : `postgres:15-alpine`
- **Persistance** : Volume Docker `postgres_data`.
- **Initialisation** : Exécute automatiquement les scripts SQL présents dans `./sqlfiles` au premier démarrage (Migration de schéma).
- **Healthcheck** : Vérifie la disponibilité via `pg_isready`.

#### 3. Cache (`redis`)
- **Image** : `redis:alpine`
- **Persistance** : Volume Docker `redis_data`.
- **Healthcheck** : Vérifie la disponibilité via `redis-cli ping`.

#### 4. API (`api`)
- **Build** : Construit à partir de `python.Dockerfile`.
  - Base : Python 3.9-slim
  - Installation des dépendances depuis `requirements.txt`.
- **Commande** : Lance le serveur `uvicorn` sur le port 8000.
- **Dépendances** : Attend que `db` et `redis` soient `healthy` avant de démarrer.
- **Variables d'environnement** :
  - `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - `REDIS_HOST`

## 3. Automatisation (Ansible)

Le playbook `playbook.yml` automatise l'installation et le déploiement sur le serveur distant.

### Étapes du Playbook
1. **Préparation** : Mise à jour `apt`, installation de Docker, Docker Compose, Git et Pip.
2. **Utilisateur** : Ajout de l'utilisateur `ubuntu` au groupe `docker`.
3. **Mise en place** : Création de l'arborescence `/home/ubuntu/app-fullstack`.
4. **Transfert** : Copie des fichiers de configuration et sources (docker-compose, Dockerfile, codes sources, SQL, requirements).
5. **Gestion du cycle de vie** :
   - Arrêt de l'ancienne stack (`docker compose down`).
   - Rebuild et démarrage (`docker compose up --build -d`).
6. **Vérification** : Affiche l'état des conteneurs et les URLs d'accès.

## 4. Procédures Courantes

### Mettre à jour l'application
Si vous modifiez le code (Python ou HTML) :
1. Sauvegardez vos changements localement.
2. Re-lancez simplement le playbook Ansible :
   ```bash
   ansible-playbook -i inventory.ini playbook.yml
   ```
   *Ansible détectera les changements de fichiers, les transférera et redémarrera les conteneurs grâce aux tâches définies.*

### Connexion SSH au serveur
Utilisez la clé générée par Terraform :
```bash
ssh -i app-key-terraform.pem ubuntu@<IP_INSTANCE>
```

### Voir les logs
Sur le serveur distant :
```bash
cd ~/app-fullstack
docker compose logs -f
```
