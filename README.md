# Starter DevOps - Application FullStack

Ce projet est une application FullStack complète conteneurisée, prête à être déployée sur AWS à l'aide de **Terraform** et **Ansible**.

## 🏗️ Architecture Technique

L'application est composée de 4 services orchestrés par Docker Compose :

- **Frontend** : Serveur Nginx statique (Port `8080`).
- **Backend API** : Python FastAPI (Port `8000`).
- **Base de Données** : PostgreSQL 15.
- **Cache** : Redis.

L'infrastructure est gérée comme suit :
- **Terraform** : Provisioning de l'instance EC2 AWS, Security Groups et Clés SSH.
- **Ansible** : Configuration du serveur, installation de Docker et déploiement de l'application.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :
- [Terraform](https://www.terraform.io/) (>= 1.2)
- [Ansible](https://www.ansible.com/)
- [AWS CLI](https://aws.amazon.com/cli/) configuré avec vos identifiants (`aws configure`).

## 🚀 Démarrage Rapide

### 1. Provisioning de l'infrastructure (Terraform)

Rendez-vous à la racine du projet :

```bash
# Initialiser Terraform
terraform init

# Visualiser le plan d'exécution
terraform plan

# Appliquer le déploiement (Ceci créera une clé SSH locale 'app-key-terraform.pem')
terraform apply -auto-approve
```

> **Note** : Notez l'adresse IP publique affichée à la fin de la commande (`instance_ip`).

### 2. Déploiement de l'application (Ansible)

Une fois l'instance créée, mettez à jour votre fichier d'inventaire `inventory.ini` avec l'IP obtenue :

```ini
[app_hosts]
<VOTRE_IP_INSTANCE> ansible_user=ubuntu ansible_ssh_private_key_file=./app-key-terraform.pem
```

Lancez ensuite le playbook Ansible :

```bash
# Déployer l'application
export ANSIBLE_HOST_KEY_CHECKING=False
ansible-playbook -i inventory.ini playbook.yml
```

## ⚙️ Pipeline CI/CD (GitHub Actions)

Ce projet inclut un pipeline d'automatisation complet défini dans `.github/workflows/deploy.yml`.

### Prérequis pour le Pipeline

Pour que le déploiement automatique fonctionne, vous devez configurer les **Secrets** suivants dans votre dépôt GitHub (Settings > Secrets and variables > Actions) :

| Secret Name | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | Votre clé d'accès AWS. |
| `AWS_SECRET_ACCESS_KEY` | Votre clé secrète AWS. |

> **Note** : Le token `GITHUB_TOKEN` est utilisé automatiquement pour l'authentification au registre de conteneurs (GHCR).

### Fonctionnement du Pipeline

Le pipeline se déclenche manuellement (`workflow_dispatch`) et exécute les étapes suivantes :
1. **Build & Publish** : Construit l'image Docker de l'API et la pousse sur le GitHub Container Registry (GHCR).
2. **Terraform Apply** : Provisionne l'infrastructure sur AWS.
3. **Ansible Deploy** : Configure le serveur et déploie l'application via Docker Compose.

## 🌍 Accès à l'application

Une fois le déploiement terminé :

- **Frontend** : `http://<VOTRE_IP>:8080`
- **Documentation API (Swagger)** : `http://<VOTRE_IP>:8000/docs`
- **PostgreSQL** : Port `5432`
- **Redis** : Port `6379`

## 📁 Structure du Projet

```
.
├── app/                 # Code source de l'API (FastAPI)
├── ansible/             # Contient le playbook et l'inventory
├── docker/              # Contient le docker permettant de récupérer depuis l'image api depuis le ghcr
├── frontend/            # Code source du Frontend (HTML/JS)
├── infra/               # Contient le main.tf
├── sqlfiles/            # Scripts d'initialisation SQL
├── docker-compose.yml   # Définition des services Docker 
├── python.Dockerfile    # Dockerfile pour l'API
└── requirements.txt     # Dépendances Python
```

Pour plus de détails, consultez le fichier [DOCUMENTATION.md](./DOCUMENTATION.md).
