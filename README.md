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

## Presentation

Ce module Odoo 18 Community couvre la gestion complète d'une officine pharmaceutique senegalaise : catalogue de medicaments, gestion des stocks par lot (algorithme FEFO), ventes au comptoir avec controle des ordonnances, reapprovisionnement fournisseur et 4 rapports PDF professionnels.

Developpe dans le cadre du cours ERP Odoo du Master 2 Data Science et Genie Logiciel (DSGL) de l'Universite Alioune Diop de Bambey.

En savoir plus sur Odoo : [odoo.com](https://www.odoo.com)

---

## Fonctionnalites

| Domaine | Ce que fait le module |
|---|---|
| Catalogue | Medicaments avec DCI, forme galenique, dosage, TVA 0%/18% |
| Stocks | Lots, alertes peremption/rupture, algorithme FEFO |
| Ventes | Ticket de caisse, lignes de vente, controle ordonnances |
| Ordonnances | Prescriptions medicales, posologies, scan numerique |
| Reappro | Bons de commande fournisseur, reception automatique des lots |
| Rapports | 4 rapports PDF via QWeb (ticket, inventaire, bilan, bon de commande) |
| Securite | 3 groupes (Vendeur / Pharmacien / Gestionnaire), record rules |

---

## Prerequis

- Docker Desktop installe et demarre
- Git

---

## Installation rapide (Docker)

```bash
# 1. Cloner le depot
git clone <url-du-repo>
cd Pharmacie-Management

# 2. Demarrer les conteneurs
docker compose up -d

# 3. Attendre ~15 secondes puis ouvrir le navigateur
# http://localhost:8069/web/database/manager

# 4. Creer la base de donnees
#    Master Password : admin123
#    Database Name   : odoo18
#    Language        : French (France)
#    Country         : Senegal

# 5. Se connecter et installer le module Pharmacie Management
```

### Mise a jour apres modification

```bash
docker exec pharmacie_odoo odoo -d odoo18 -u pharmacie_management --stop-after-init
docker compose restart odoo
```

---

## Installation manuelle (sans Docker)

```bash
# Copier le module dans le dossier addons d'Odoo
cp -r pharmacie_management /chemin/odoo/addons/

# Installer
python odoo-bin -c odoo.conf -d odoo18 -i pharmacie_management

# Mettre a jour
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
│   ├── Medicaments
│   ├── Lots et stocks
│   └── Alertes de peremption / rupture
├── Fournisseurs
│   ├── Liste des fournisseurs
│   └── Reapprovisionnements
├── Rapports
│   └── Bilan de caisse (wizard)
└── Configuration  [Pharmacien / Gestionnaire uniquement]
    ├── Categories de medicaments
    └── Parametres de la pharmacie
```

---

## Modeles de donnees

| Modele | Description |
|---|---|
| `pharmacie.categorie` | Categories therapeutiques (hierarchie parent/enfant) |
| `pharmacie.medicament` | Catalogue : DCI, forme, dosage, TVA, stock calcule FEFO |
| `pharmacie.lot` | Lots de stock : peremption, quantites, statut automatique |
| `pharmacie.vente` | Ventes au comptoir : workflow brouillon, confirmee, annulee |
| `pharmacie.vente.ligne` | Lignes de vente avec decrementation FEFO |
| `pharmacie.ordonnance` | Ordonnances medicales avec scan numerique |
| `pharmacie.posologie` | Detail posologique par medicament prescrit |
| `pharmacie.reappro` | Bons de commande fournisseur |
| `pharmacie.reappro.ligne` | Lignes de commande avec reception et creation de lots |
| `res.partner` (etendu) | Fournisseurs pharma : agrement DPM, delai livraison |

---

## Securite

| Groupe | Medicaments | Stocks/Lots | Ventes | Ordonnances | Reappro |
|---|---|---|---|---|---|
| Vendeur | Lecture | Lecture | Creer/Lire | Creer/Lire | Aucun acces |
| Pharmacien | CRUD | CRUD | CRUD | CRUD | CRUD |
| Gestionnaire | CRUD | CRUD | CRUD | CRUD | CRUD |

Un vendeur ne peut consulter que ses propres ventes (record rule : `vendeur_id = utilisateur actuel`).

Les menus **Rapports** et **Configuration** sont visibles uniquement par les groupes Pharmacien et Gestionnaire.

---

## Contexte senegalais

- Prix en **FCFA**
- TVA : **0%** medicaments essentiels / **18%** autres medicaments
- Champ **DCI** (Denomination Commune Internationale) sur chaque medicament
- Champ **sur_ordonnance** : controle la delivrance des antibiotiques, psychotropes, etc.
- Numero d'agrement **DPM** (Direction de la Pharmacie et du Medicament) sur les fournisseurs

---

## Structure du projet

```
Pharmacie-Management/
├── docker-compose.yml
├── odoo.conf
├── .gitignore
├── README.md
├── docs/
│   ├── logo_uadb.png
│   ├── RAPPORT_TECHNIQUE.docx
│   ├── GUIDE_UTILISATEUR.docx
│   └── GUIDE_GROUPE.docx
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

## Depannage

**Le module ne s'installe pas :**
```bash
docker logs pharmacie_odoo --tail 50
```

**Les menus Rapports/Configuration ne s'affichent pas :**
Se deconnecter et se reconnecter — les droits de groupe ne sont charges qu'a la connexion.

**Reinitialiser completement la base :**
```bash
docker compose stop odoo
docker exec pharmacie_db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo18;"
docker compose start odoo
# Puis recreer la base via http://localhost:8069/web/database/manager
```
