<p align="center">
  <img src="docs/logo_uadb.png" alt="Université Alioune Diop de Bambey" height="90"/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/odoo/documentation/18.0/static/img/odoo_logo.png" alt="Odoo 18" height="60"/>
</p>

<h1 align="center">pharmacie_management</h1>

<p align="center">
  <strong>Module ERP Odoo 18 — Gestion de pharmacie au Sénégal</strong><br>
  Université Alioune Diop de Bambey | Master 2 DSGL | 2025-2026<br>
  Encadrant : Youssoupha LAM
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Odoo-18%20Community-714B67?logo=odoo&logoColor=white" alt="Odoo 18"/>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker"/>
</p>

---

## Présentation

Ce module Odoo 18 Community couvre la gestion complète d'une officine pharmaceutique sénégalaise : catalogue de médicaments, gestion des stocks par lot (algorithme FEFO), ventes au comptoir avec contrôle des ordonnances, réapprovisionnement fournisseur et 4 rapports PDF professionnels.

Développé dans le cadre du cours ERP Odoo du Master 2 Data Science et Génie Logiciel (DSGL) de l'Université Alioune Diop de Bambey.

En savoir plus sur Odoo : [odoo.com](https://www.odoo.com)

---

## Fonctionnalités

| Domaine | Ce que fait le module |
|---|---|
| Catalogue | Médicaments avec DCI, forme galénique, dosage, TVA 0%/18% |
| Stocks | Lots, alertes péremption/rupture, algorithme FEFO |
| Ventes | Ticket de caisse, lignes de vente, contrôle ordonnances |
| Ordonnances | Prescriptions médicales, posologies, scan numérique |
| Réappro | Bons de commande fournisseur, réception automatique des lots |
| Rapports | 4 rapports PDF via QWeb (ticket, inventaire, bilan, bon de commande) |
| Sécurité | 3 groupes (Vendeur / Pharmacien / Gestionnaire), record rules |

---

## Prérequis

- Docker Desktop installé et démarré
- Git

---

## Installation rapide (Docker)

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd Pharmacie-Management

# 2. Démarrer les conteneurs
docker compose up -d

# 3. Ouvrir le navigateur après 15 secondes
# http://localhost:8069/web/database/manager

# 4. Créer la base de données
#    Master Password : admin123
#    Database Name   : odoo18
#    Language        : French (France)
#    Country         : Senegal

# 5. Se connecter et installer le module Pharmacie Management
```

### Mise à jour après modification

```bash
docker exec pharmacie_odoo odoo -d odoo18 -u pharmacie_management --stop-after-init
docker compose restart odoo
```

---

## Installation manuelle (sans Docker)

```bash
cp -r pharmacie_management /chemin/odoo/addons/
python odoo-bin -c odoo.conf -d odoo18 -i pharmacie_management
python odoo-bin -c odoo.conf -d odoo18 -u pharmacie_management
```

---

## Architecture des menus

```
Pharmacie
├── Caisse
│   ├── Nouvelle vente
│   └── Historique des ventes
├── Ordonnances
│   └── Liste des ordonnances
├── Stock
│   ├── Médicaments
│   ├── Lots et stocks
│   └── Alertes de péremption / rupture
├── Fournisseurs
│   ├── Liste des fournisseurs
│   └── Réapprovisionnements
├── Rapports
│   └── Bilan de caisse (wizard)
└── Configuration  [Pharmacien / Gestionnaire uniquement]
    ├── Catégories de médicaments
    └── Paramètres de la pharmacie
```

---

## Modèles de données

| Modèle | Description |
|---|---|
| `pharmacie.categorie` | Catégories thérapeutiques (hiérarchie parent/enfant) |
| `pharmacie.medicament` | Catalogue : DCI, forme, dosage, TVA, stock calculé FEFO |
| `pharmacie.lot` | Lots de stock : péremption, quantités, statut automatique |
| `pharmacie.vente` | Ventes au comptoir : workflow brouillon, confirmée, annulée |
| `pharmacie.vente.ligne` | Lignes de vente avec décrémentation FEFO |
| `pharmacie.ordonnance` | Ordonnances médicales avec scan numérique |
| `pharmacie.posologie` | Détail posologique par médicament prescrit |
| `pharmacie.reappro` | Bons de commande fournisseur |
| `pharmacie.reappro.ligne` | Lignes de commande avec réception et création de lots |
| `res.partner` (étendu) | Fournisseurs pharma : agrément DPM, délai livraison |

---

## Sécurité

| Groupe | Médicaments | Stocks/Lots | Ventes | Ordonnances | Réappro |
|---|---|---|---|---|---|
| Vendeur | Lecture | Lecture | Créer/Lire/Modifier | Créer/Lire/Modifier | Aucun accès |
| Pharmacien | CRUD | CRUD | CRUD | CRUD | CRUD |
| Gestionnaire | CRUD | CRUD | CRUD | CRUD | CRUD |

Un vendeur ne peut consulter que ses propres ventes (record rule : `vendeur_id = utilisateur actuel`).

Les menus **Rapports** et **Configuration** sont visibles uniquement par les groupes Pharmacien et Gestionnaire.

---

## Contexte sénégalais

- Prix en **FCFA**
- TVA : **0%** médicaments essentiels / **18%** autres médicaments
- Champ **DCI** (Dénomination Commune Internationale) sur chaque médicament
- Champ **sur_ordonnance** : contrôle la délivrance des antibiotiques, psychotropes, etc.
- Numéro d'agrément **DPM** (Direction de la Pharmacie et du Médicament) sur les fournisseurs

---

## Structure du projet

```
Pharmacie-Management/
├── docker-compose.yml
├── odoo.conf
├── .gitignore
├── README.md
├── docs/
│   └── logo_uadb.png
└── pharmacie_management/
    ├── __manifest__.py
    ├── models/
    ├── views/
    ├── wizards/
    ├── report/
    ├── security/
    ├── data/
    └── demo/
```

---

## Dépannage

**Le module ne s'installe pas :**
```bash
docker logs pharmacie_odoo --tail 50
```

**Les menus Rapports/Configuration ne s'affichent pas :**
Se déconnecter et se reconnecter — les droits de groupe ne sont chargés qu'à la connexion.

**Réinitialiser complètement la base :**
```bash
docker compose stop odoo
docker exec pharmacie_db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo18;"
docker compose start odoo
```
