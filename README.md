# 🚀 Customer Analytics & Churn Prediction MLOps Platform

![MLOps Platform](https://img.shields.io/badge/MLOps-Platform-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-green)
![Python](https://img.shields.io/badge/Python-3.9-yellow)
![Airflow](https://img.shields.io/badge/Airflow-2.7-red)
![MLflow](https://img.shields.io/badge/MLflow-2.8-orange)

Une plateforme MLOps complète pour la prédiction du churn client avec entraînement automatisé, suivi d'expérimentations et monitoring en temps réel.

## 📊 Architecture

```
graph TB
    A[Airflow Orchestrator] --> B[Data Processing]
    B --> C[Model Training]
    C --> D[MLflow Tracking]
    D --> E[MinIO Artifact Store]
    D --> F[Streamlit Dashboard]
    G[PostgreSQL] --> D
    G --> A
    H[MinIO Storage] --> E
    I[Streamlit UI] --> F
```

## 🏗️ Stack Technologique

| Composant | Utilisation | Technologie |
|-----------|-------------|-------------|
| Orchestration | Automatisation des workflows | Apache Airflow 2.7 |
| Suivi d'expériences | Versioning des modèles ML | MLflow 2.8 |
| Stockage d'artefacts | Stockage des modèles | MinIO (compatible S3) |
| Visualisation | Dashboard temps réel | Streamlit |
| Stockage métadonnées | Métadonnées des expériences | PostgreSQL 13 |
| Conteneurisation | Isolation des services | Docker Compose |

## 🚀 Démarrage Rapide

### Prérequis

- Docker 20.10+ et Docker Compose 2.0+
- Git
- 8GB+ RAM recommandés

### Installation

```
# Cloner le dépôt
git clone https://github.com/YOUSSEF-BT/customer-mlops-pipeline.git
cd customer-mlops-pipeline

# Démarrer tous les services
docker-compose up -d

# Attendre le démarrage des services (environ 45 secondes)
sleep 45

# Initialiser la base de données Airflow et créer l'utilisateur admin
docker-compose exec airflow-webserver airflow db init
docker-compose exec airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

## 📁 Structure du Projet

```
customer-mlops-pipeline/
├── airflow/                  # Configuration Airflow
│   ├── dags/                # DAGs du pipeline
│   ├── Dockerfile           # Conteneur Airflow
│   └── requirements.txt     # Dépendances Python
├── mlflow/                  # Serveur de tracking MLflow
│   └── Dockerfile           # Conteneur MLflow
├── streamlit/               # Dashboard Streamlit
│   ├── Dockerfile           # Conteneur Streamlit
│   ├── requirements.txt     # Dépendances Python
│   └── streamlit_app.py     # Application dashboard
├── training_pipeline/       # Scripts d'entraînement
│   ├── config.yaml         # Fichier de configuration
│   └── src/train_model.py  # Pipeline d'entraînement
├── data/                    # Données d'exemple (gitignored)
├── models/                  # Modèles entraînés (gitignored)
├── docker-compose.yml       # Orchestration complète
├── .gitignore              # Fichier d'exclusion Git
├── LICENSE                 # Licence MIT
└── README.md              # Ce fichier
```

## 🔧 Configuration des Services

| Service | Port | Identifiants par défaut | Utilisation |
|---------|------|------------------------|-------------|
| Airflow Webserver | 8080 | admin/admin | Interface d'orchestration |
| Airflow Scheduler | - | - | Planification des tâches |
| MLflow | 5001 | - | Interface de tracking |
| MinIO | 9000 | minioadmin/minioadmin | API de stockage |
| MinIO Console | 9001 | minioadmin/minioadmin | Interface de gestion |
| Streamlit | 8502 | - | Dashboard temps réel |
| Adminer | 8081 | - | Interface de gestion DB |
| PostgreSQL (Airflow) | 5432 | airflow/airflow | Métadonnées Airflow |
| PostgreSQL (MLflow) | 5432 | mlflow/mlflow | Métadonnées MLflow |

## 📈 Fonctionnalités

### ✅ Pipeline MLOps Complet

- **Traitement automatisé des données** : Ingestion, nettoyage et feature engineering
- **Entraînement de modèles** : Algorithmes multiples avec tuning d'hyperparamètres
- **Suivi d'expériences** : Intégration complète MLflow pour la reproductibilité
- **Versioning d'artefacts** : Stockage des modèles dans MinIO avec contrôle de version
- **Monitoring temps réel** : Dashboard live avec Streamlit

### ✅ Architecture Scalable

- **Microservices** : Chaque composant s'exécute dans des conteneurs isolés
- **Stockage persistant** : PostgreSQL pour les métadonnées, MinIO pour les artefacts
- **Isolation réseau** : Réseau interne sécurisé entre services
- **Health checks** : Monitoring automatique et redémarrage des services

### ✅ Monitoring & Visualisation

- **Dashboard Streamlit** : Analytics clients interactifs et prédictions
- **Interface MLflow** : Comparaison d'expériences et registre de modèles
- **Interface Airflow** : Monitoring des pipelines et déclenchement manuel
- **Console MinIO** : Gestion du stockage d'artefacts

## 🎯 Guide d'Utilisation

### Étape 1 : Démarrer la Plateforme

```
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Consulter les logs
docker-compose logs -f
```

### Étape 2 : Accéder aux Interfaces

- **Airflow UI** : http://localhost:8080 (admin/admin)
- **MLflow UI** : http://localhost:5001
- **Dashboard Streamlit** : http://localhost:8502
- **Console MinIO** : http://localhost:9001 (minioadmin/minioadmin)

### Étape 3 : Configurer le Stockage d'Artefacts MLflow

```
# Configurer le bucket MinIO pour MLflow
docker-compose exec minio mc alias set myminio http://localhost:9000 minioadmin minioadmin
docker-compose exec minio mc mb myminio/mlflow-artifacts
```

### Étape 4 : Exécuter le Pipeline d'Entraînement

1. Accéder à l'interface Airflow (http://localhost:8080)
2. Trouver le DAG : `churn_mlops_pipeline`
3. Activer le DAG (bouton ON)
4. Cliquer sur le bouton de déclenchement
5. Surveiller l'exécution dans la vue Graph

### Étape 5 : Visualiser les Résultats

- **MLflow** : Suivre les expériences, comparer les modèles, consulter les métriques
- **Streamlit** : Visualiser les prédictions, segments clients et performances
- **MinIO** : Parcourir les modèles et artefacts stockés

## 🛠️ Développement

### Ajouter de Nouveaux Modèles

1. Modifier `training_pipeline/src/train_model.py`
2. Mettre à jour `training_pipeline/config.yaml`
3. Tester localement : `python train_model.py`
4. Committer et pousser les modifications

### Modifier le Dashboard

1. Éditer `streamlit/streamlit_app.py`
2. Mettre à jour `streamlit/requirements.txt`
3. Rebuilder : `docker-compose build streamlit-app`
4. Redémarrer : `docker-compose up -d streamlit-app`

### Ajouter de Nouveaux DAGs

1. Ajouter un fichier Python dans `airflow/dags/`
2. Suivre les bonnes pratiques Airflow
3. Tester dans l'interface Airflow

## 🔍 Dépannage

### Problèmes Courants

**MLflow ne démarre pas** :

```
# Vérifier la connexion PostgreSQL
docker-compose exec postgres-mlflow psql -U mlflow -d mlflowdb -c "SELECT 1;"

# Rebuilder le service MLflow
docker-compose build --no-cache mlflow
docker-compose up -d mlflow
```

**Erreurs de base de données Airflow** :

```
# Initialiser la base de données Airflow
docker-compose exec airflow-webserver airflow db init

# Créer l'utilisateur admin (si inexistant)
docker-compose exec airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

**Permissions du bucket MinIO** :

```
# Rendre le bucket public (développement uniquement)
docker-compose exec minio mc anonymous set public myminio/mlflow-artifacts
```

### Logs des Services

```
# Consulter les logs d'un service spécifique
docker-compose logs mlflow
docker-compose logs airflow-webserver
docker-compose logs streamlit-app

# Suivre les logs en temps réel
docker-compose logs -f mlflow
```

### Problèmes de Ressources

```
# Vérifier l'utilisation des ressources
docker stats

# Arrêter tous les services
docker-compose down

# Supprimer les volumes (ATTENTION : supprime toutes les données)
docker-compose down -v
```

## 🤝 Contribuer

1. Forker le dépôt
2. Créer une branche feature (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committer les modifications (`git commit -m 'Ajout NouvelleFonctionnalite'`)
4. Pousser vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrir une Pull Request

### Guidelines de Développement

- Suivre PEP 8 pour le code Python
- Ajouter des docstrings pour les fonctions et classes
- Mettre à jour la documentation lors de modifications
- Tester localement avant de soumettre une PR

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## 👤 Auteur

**YOUSSEF-BT**

- GitHub : [@YOUSSEF-BT](https://github.com/YOUSSEF-BT)
- Projet : [Customer MLOps Pipeline](https://github.com/YOUSSEF-BT/customer-mlops-pipeline)

## 🙏 Remerciements

- L'équipe Apache Airflow pour l'orchestration des workflows
- L'équipe MLflow pour le suivi d'expériences
- L'équipe Streamlit pour le développement rapide de dashboards
- L'équipe MinIO pour le stockage compatible S3
- La communauté Docker pour la conteneurisation

## 📚 Références

- [Documentation Airflow](https://airflow.apache.org/docs/)
- [Documentation MLflow](https://mlflow.org/docs/latest/index.html)
- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation MinIO](https://min.io/docs/minio/linux/index.html)
- [Documentation Docker Compose](https://docs.docker.com/compose/)

## 📊 Métriques de Performance

| Métrique | Valeur | Description |
|----------|--------|-------------|
| Temps de démarrage | ~2 minutes | Temps pour que tous les services soient prêts |
| Entraînement modèle | ~5-10 minutes | Exécution complète du pipeline |
| Stockage | 2GB+ | Estimé pour 1000+ expériences |
| Utilisateurs simultanés | 10+ | Dashboard et monitoring |

## 🔄 Intégration Continue

Cette plateforme inclut :

- Docker Compose pour le développement local
- PostgreSQL pour les métadonnées persistantes
- MinIO pour le stockage scalable d'artefacts
- Health checks pour tous les services

### Prochaines Étapes

- Déploiement cloud (AWS/Azure/GCP)
- Ajout d'un pipeline CI/CD
- Implémentation du monitoring de modèles

---

⭐️ **Donnez une étoile si ce projet vous a aidé !**

Développé avec ❤️ par YOUSSEF-BT
