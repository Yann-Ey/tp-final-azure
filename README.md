# TP Final - Application Flask Serverless sur Azure

Ce projet déploie une application Flask simple sur Azure Kubernetes Service (AKS) via une pipeline CI/CD GitHub Actions.

> [!NOTE]
> Déploiement automatique via GitHub Actions.


## Structure du Projet

- `app.py` : Application Flask (API REST).
- `Dockerfile` : Configuration pour conteneuriser l'application.
- `terraform/` : Infrastructure as Code pour provisionner les ressources Azure.
- `k8s/` : Manifestes Kubernetes (Deployment, Service).
- `.github/workflows/` : Pipeline CI/CD pour le déploiement automatique.

## Prérequis

- Compte Azure actif.
- Azure CLI installé.
- Terraform installé.
- Docker Desktop installé.

## Déploiement

### 1. Infrastructure (Terraform)

Initialisez et appliquez la configuration Terraform pour créer le Resource Group, l'ACR et l'AKS.

```bash
cd terraform
terraform init
terraform apply
```

**Notez les outputs** : `acr_login_server`, `aks_name`, `resource_group_name`.

### 2. Configuration GitHub Secrets

Ajoutez les secrets suivants dans votre repository GitHub (Settings > Secrets and variables > Actions) :

- `AZURE_CREDENTIALS` : JSON de votre Service Principal Azure.
- `ACR_NAME` : Nom de votre Azure Container Registry.
- `ACR_LOGIN_SERVER` : URL de votre ACR (ex: `tpfinalacrXYZ.azurecr.io`).
- `ACR_USERNAME` : Username de l'ACR (activé via `admin_enabled = true`).
- `ACR_PASSWORD` : Password de l'ACR.
- `AKS_CLUSTER_NAME` : Nom de votre cluster AKS.
- `RESOURCE_GROUP` : Nom de votre Resource Group.

### 3. Déploiement Automatique

Pushez vos changements sur la branche `main` pour déclencher la pipeline :

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

La pipeline va :
1.  Builder l'image Docker.
2.  Pusher l'image sur votre ACR.
3.  Déployer l'application sur votre cluster AKS.

## Test

Une fois déployé, récupérez l'IP externe du service :

```bash
kubectl get svc tp-final-app-service
```

Accédez à l'API : `http://<EXTERNAL-IP>/hello`
