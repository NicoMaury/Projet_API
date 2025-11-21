# Rail Traffic API

Ce projet est une application complète permettant d'importer, de stocker et d'exposer des données sur les gares ferroviaires françaises provenant de l'Open Data SNCF.

Il utilise **Docker** pour orchestrer une base de données **PostgreSQL**, un script d'importation **Python**, et une API REST construite avec **FastAPI**.

## Fonctionnalités

*   **Importation de données** : Récupération automatique de la liste des gares depuis l'API SNCF et stockage dans une base de données relationnelle.
*   **Base de données** : Stockage persistant des données (Gares et Départements) avec PostgreSQL.
*   **API REST** : Consultation des données via des endpoints HTTP performants.

## Prérequis

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## Installation et Démarrage

1.  Clonez ce dépôt :
    ```bash
    git clone <votre-repo-url>
    cd Projet_API
    ```

2.  Lancez les conteneurs avec Docker Compose :
    ```bash
    docker-compose up --build
    ```

    Cette commande va :
    *   Construire les images Docker pour l'importateur et l'API.
    *   Démarrer la base de données PostgreSQL.
    *   Lancer le script d'importation (`importer`) qui va peupler la base de données.
    *   Démarrer le serveur API (`api`) sur le port 8000.

## Utilisation de l'API

Une fois les conteneurs démarrés, l'API est accessible à l'adresse `http://localhost:8000`.

### Documentation Interactive

La documentation complète et interactive (Swagger UI) est disponible ici :
👉 **http://localhost:8000/docs**

### Endpoints Principaux

*   **Liste des départements** :
    *   `GET /departements`
    *   Retourne la liste de tous les départements enregistrés.

*   **Liste des gares** :
    *   `GET /gares`
    *   Paramètres optionnels :
        *   `limit` (int, défaut 100) : Nombre de résultats à retourner.
        *   `offset` (int, défaut 0) : Décalage pour la pagination.
        *   `departement` (str) : Filtrer par nom de département (ex: `PARIS`).

## Structure du Projet

*   `api.py` : Code source de l'API FastAPI.
*   `import_data.py` : Script Python pour récupérer les données SNCF et les insérer en base.
*   `check_data.py` : Script utilitaire pour vérifier rapidement le contenu de la base.
*   `docker-compose.yml` : Configuration des services Docker.
*   `Dockerfile` : Définition de l'image Python utilisée par l'importateur et l'API.
*   `requirements.txt` : Liste des dépendances Python.

## Vérification des données

Vous pouvez vérifier que les données sont bien présentes en base en exécutant le script de vérification via Docker :

```bash
docker-compose run --rm importer python check_data.py
```
