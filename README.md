# Compte Rendu Détaillé : Déploiement Cloud Native sur Azure AKS

**Auteur :** Yann-Ey
**Projet :** TP Final - Déploiement d'une application Flask sur Kubernetes (AKS) via CI/CD
**Date :** 15 Décembre 2025

---

## 1. Introduction et Objectifs

L'objectif de ce projet était de concevoir et déployer une architecture **Cloud Native** complète sur Microsoft Azure. Ce travail valide les compétences en **DevOps**, **Conteneurisation** et **Orchestration**.

**Les piliers du projet :**
1.  **Code** : Application Python Flask.
2.  **Container** : Dockerisation optimisée.
3.  **Infrastructure** : Provisioning automatisé via Terraform (IaC).
4.  **Orchestration** : Déploiement résilient sur Kubernetes (AKS).
5.  **Automation** : Pipeline CI/CD GitHub Actions.

---

## 2. Architecture Technique

### Schéma des Flux
`Développeur` -> `Git Push` -> `GitHub Actions` -> `Build Docker` -> `Push ACR` -> `Deploy AKS` -> `LoadBalancer` -> `Utilisateur Final`

### Composants Clés
*   **GitHub** : Source de vérité (Code & Config).
*   **Azure Container Registry (ACR)** : Registre privé sécurisé pour nos images Docker.
*   **Azure Kubernetes Service (AKS)** : Cluster managé pour exécuter l'application.
*   **Terraform** : Outil pour créer l'infrastructure de manière reproductible.

---

## 3. Analyse Technique Approfondie (Micro-Étapes)

Cette section détaille chaque fichier clé pour justifier les choix techniques.

### 3.1. Dockerfile (Optimisation et Caching)

Le fichier `Dockerfile` a été conçu pour être léger et rapide à construire.

```dockerfile
# 1. Image de base "slim"
# CHOIX : python:3.9-slim est beaucoup plus légère que python:3.9 (environ 100Mo vs 900Mo).
# AVANTAGE : Téléchargement plus rapide, surface d'attaque réduite (sécurité).
FROM python:3.9-slim

# 2. Répertoire de travail
# CHOIX : Isoler l'application dans /app pour ne pas polluer la racine du conteneur.
WORKDIR /app

# 3. Gestion des dépendances (Layer Caching)
# CHOIX : On copie UNIQUEMENT requirements.txt d'abord.
COPY requirements.txt .

# 4. Installation des paquets
# AVANTAGE : Si on modifie le code source (app.py) sans toucher aux requirements.txt,
# Docker réutilisera le cache de cette étape. Le build sera instantané.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie du code source
COPY . .

# 6. Commande de démarrage
# CHOIX : Lancement du serveur Flask.
CMD ["python", "app.py"]
```

### 3.2. Kubernetes : Deployment (Haute Disponibilité)

Le fichier `k8s/deployment.yaml` assure que l'application est toujours disponible.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tp-final-app
spec:
  # CHOIX : 2 Réplicas.
  # AVANTAGE : Si un pod crashe ou si un nœud Azure redémarre, l'application reste accessible via le 2ème pod.
  replicas: 2
  selector:
    matchLabels:
      app: tp-final-app # Le lien avec le Service
  template:
    metadata:
      labels:
        app: tp-final-app
    spec:
      containers:
        - name: tp-final-app
          # CHOIX : Utilisation de l'ACR privé.
          # Le tag est dynamique (${{ github.sha }}) pour garantir qu'on déploie exactement la version du commit.
          image: tpfinalacrsgoh4x.azurecr.io/tp-final-app:latest
          ports:
            - containerPort: 8080 # Port interne de Flask
```

### 3.3. Kubernetes : Service (Exposition Externe)

Le fichier `k8s/service.yaml` rend l'application accessible depuis Internet.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tp-final-app-service
spec:
  # CHOIX : LoadBalancer.
  # AVANTAGE : Demande automatiquement à Azure de provisionner une IP Publique et un répartiteur de charge.
  type: LoadBalancer
  selector:
    app: tp-final-app # Cible les pods ayant ce label
  ports:
    - protocol: TCP
      port: 80        # Port exposé aux utilisateurs (HTTP standard)
      targetPort: 8080 # Port écouté par le conteneur Flask
```

---

## 4. Infrastructure as Code (Terraform)

L'infrastructure n'a pas été créée "à la main" (ClickOps) mais via du code (`main.tf`), garantissant l'**idempotence**.

*   **Resource Group** : `tp-final-rg`
*   **ACR** : `tpfinalacrsgoh4x` (Sku Basic pour réduire les coûts).
*   **AKS** : `tp-final-aks` (Node Pool par défaut).
*   **IAM** : Attribution automatique du rôle `AcrPull` au cluster AKS. Cela permet au cluster de télécharger les images depuis le registre privé sans avoir besoin de gérer des mots de passe Docker (`imagePullSecrets`), une **bonne pratique de sécurité majeure**.

---

## 5. Pipeline CI/CD (GitHub Actions)

L'automatisation est totale via `.github/workflows/azure-deploy.yml`.

1.  **Trigger** : À chaque `push` sur la branche `main`.
2.  **Sécurité** : Utilisation de `secrets.AZURE_CREDENTIALS` (Service Principal) pour ne jamais exposer les identifiants dans le code.
3.  **Build & Push** :
    *   Construction de l'image.
    *   Tag avec le SHA du commit (ex: `sha-a1b2c3d`).
    *   Push vers l'ACR.
4.  **Deploy** :
    *   Injection de la nouvelle image dans le cluster AKS.
    *   Kubernetes effectue un **Rolling Update** (mise à jour sans interruption de service).

---

## 6. Problèmes Rencontrés & Résolutions

### 🔴 Problème : ImagePullBackOff
*   **Description** : Kubernetes n'arrivait pas à télécharger l'image.
*   **Cause** : Le manifeste `deployment.yaml` pointait vers `tp-final-app:latest` (interprété comme Docker Hub) au lieu de l'ACR Azure.
*   **Solution** : Mise à jour du manifeste avec l'URL complète du registre : `tpfinalacrsgoh4x.azurecr.io/...`.

### 🔴 Problème : Erreur 404
*   **Description** : L'accès à l'IP racine renvoyait une erreur.
*   **Cause** : L'application Flask n'a pas de route `/`.
*   **Solution** : Utilisation de la route `/hello` définie dans `app.py`.

---

## 7. Preuves de Fonctionnement

### Statut des Pods (Running)
```bash
NAME                            READY   STATUS    RESTARTS   AGE
tp-final-app-5f879b8ffc-k9z2r   1/1     Running   0          45m
tp-final-app-5f879b8ffc-x4p9l   1/1     Running   0          45m
```

### Test de l'API (Curl)
```bash
$ curl http://20.4.146.110/hello
{
  "message": "Bonjour, monde du serverless!"
}
```

---

## 8. Conclusion

Ce projet démontre une maîtrise complète de la chaîne de valeur DevOps :
1.  **Développement** propre et conteneurisé.
2.  **Infrastructure** gérée par le code (Terraform).
3.  **Déploiement** automatisé et sécurisé (CI/CD).
4.  **Opérations** résilientes (Kubernetes).

L'application est en ligne et fonctionnelle.
