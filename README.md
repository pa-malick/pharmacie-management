# pharmacie_management — Module Odoo 18

**Université Alioune Diop de Bambey — Centre de Ressources de Dakar**  
**Master 2 DSGL ERP Odoo — Année 2025-2026**  
**Enseignant : Youssoupha LAM**

Module Odoo 18 Community complet pour la gestion d'une officine pharmaceutique sénégalaise.

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

# 3. Attendre ~15 secondes puis ouvrir le navigateur
# http://localhost:8069/web/database/manager

# 4. Créer la base de données
#    Master Password : admin123
#    Database Name   : odoo18
#    Language        : French (France)
#    Country         : Senegal

# 5. Se connecter et installer le module Pharmacie Management
```

### Mise à jour du module après modification des fichiers

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

# Mettre à jour
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
|--------|-------------|
| `pharmacie.categorie` | Catégories thérapeutiques (hiérarchie parent/enfant) |
| `pharmacie.medicament` | Catalogue : DCI, forme, dosage, TVA, stock calculé FEFO |
| `pharmacie.lot` | Lots de stock : péremption, quantités, statut automatique |
| `pharmacie.vente` | Ventes au comptoir : workflow brouillon → confirmée → annulée |
| `pharmacie.vente.ligne` | Lignes de vente avec décrémentation FEFO |
| `pharmacie.ordonnance` | Ordonnances médicales avec scan numérique |
| `pharmacie.posologie` | Détail posologique par médicament prescrit |
| `pharmacie.reappro` | Bons de commande fournisseur |
| `pharmacie.reappro.ligne` | Lignes de commande avec réception et création de lots |
| `res.partner` (étendu) | Fournisseurs pharma : agrément DPM, délai livraison |

---

## Fonctionnalités clés

### Gestion des stocks
- Calcul du stock actuel en temps réel (somme des lots valides)
- Méthode **FEFO** (First Expiry First Out) : les lots les plus proches de la péremption sont vendus en premier
- Alertes automatiques : rouge si péremption < 30 jours, orange si < 90 jours
- Statut lot calculé automatiquement : Valide / Expiré / Épuisé

### Ventes
- Référence automatique : `VTE/2024/0001`
- Vérification ordonnance obligatoire pour les médicaments réglementés
- Modes de paiement : Espèces, Carte, Wave, Orange Money, Free Money
- Décrémentation des lots à la confirmation (FEFO)

### Réapprovisionnement
- Wizard de réappro automatique : scan des ruptures + génération de bons par fournisseur
- Bouton « Réceptionner » : crée automatiquement les lots `pharmacie.lot`

### Rapports PDF (QWeb + wkhtmltopdf)
| # | Rapport | Accès |
|---|---------|-------|
| 1 | Ticket de caisse | Fiche vente → Imprimer |
| 2 | Inventaire des stocks | Liste lots → Imprimer |
| 3 | Bilan de caisse | Rapports → Bilan de caisse |
| 4 | Bon de commande fournisseur | Fiche réappro → Imprimer |

---

## Sécurité

### Groupes et droits d'accès

| Groupe | Médicaments | Stocks/Lots | Ventes | Ordonnances | Réappro |
|--------|------------|-------------|--------|-------------|---------|
| Vendeur | Lecture | Lecture | Créer/Lire | Créer/Lire | — |
| Pharmacien | CRUD | CRUD | CRUD | CRUD | CRUD |
| Gestionnaire | Lecture | CRUD | CRUD | CRUD | CRUD complet |

### Record Rule
Un vendeur ne peut consulter que ses propres ventes (`vendeur_id = utilisateur actuel`).

### Menus restreints
Les menus **Rapports** et **Configuration** sont visibles uniquement par les groupes Pharmacien et Gestionnaire.

---

## Contexte sénégalais

- Prix en **FCFA**
- TVA : **0 %** médicaments essentiels / **18 %** autres médicaments
- Champ **DCI** (Dénomination Commune Internationale) sur chaque médicament
- Champ **sur_ordonnance** : contrôle la délivrance des antibiotiques, psychotropes, etc.
- Numéro d'agrément **DPM** (Direction de la Pharmacie et du Médicament) sur les fournisseurs

---

## Structure du projet

```
Pharmacie-Management/
├── docker-compose.yml          # Environnement Docker (Odoo 18 + PostgreSQL 16)
├── odoo.conf                   # Configuration Odoo
├── .gitignore
├── README.md
├── docs/                       # Documentation technique
│   ├── INDEX.md
│   ├── diagramme_classes.png
│   ├── diagramme_flux_vente.png
│   ├── diagramme_flux_reappro.png
│   ├── diagramme_securite.png
│   ├── capture_form_vente.png
│   ├── capture_kanban_medicaments.png
│   ├── capture_inventaire_stock.png
│   ├── capture_ticket_caisse.png
│   ├── RAPPORT_PROJET.docx
│   └── GUIDE_GROUPE.docx
└── pharmacie_management/
    ├── __manifest__.py
    ├── __init__.py
    ├── data/                   # Données initiales (catégories, séquences)
    ├── demo/                   # Données de démonstration
    ├── models/                 # Modèles Python
    ├── views/                  # Vues XML + menus
    ├── wizards/                # Wizards TransientModel
    ├── report/                 # Rapports QWeb PDF
    └── security/               # Groupes, ACL, record rules
```

---

## Données de démonstration

Le fichier `demo/pharmacie_demo.xml` contient des données réalistes :
- Catégories thérapeutiques sénégalaises
- Médicaments avec DCI, formes galéniques, prix en FCFA
- Lots avec dates de péremption variées
- Fournisseurs pharmaceutiques avec numéros d'agrément DPM
- Ventes confirmées pour tester les rapports

---

## Dépannage

**Le module ne s'installe pas :**
```bash
docker logs pharmacie_odoo --tail 50
```

**Mettre à jour après modification :**
```bash
docker exec pharmacie_odoo odoo -d odoo18 -u pharmacie_management --stop-after-init
docker compose restart odoo
```

**Les menus Rapports/Configuration ne s'affichent pas :**  
Se déconnecter et se reconnecter — les droits de groupe ne sont chargés qu'à la connexion.

**Réinitialiser complètement la base :**
```bash
docker compose stop odoo
docker exec pharmacie_db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo18;"
docker compose start odoo
# Puis recréer la base via http://localhost:8069/web/database/manager
```
