# pharmacie_management — Module Odoo 18

Module Odoo de gestion d'officine pharmaceutique.  
**Université Alioune Diop de Bambey — Master 2 DSGL ERP Odoo**

---

## Installation

```bash
# 1. Copier le dossier dans le répertoire addons d'Odoo
cp -r pharmacie_management /chemin/vers/odoo/addons/

# 2. Installer le module
python odoo-bin -c odoo.conf -d ma_base -i pharmacie_management

# 3. Mise à jour après modification
python odoo-bin -c odoo.conf -d ma_base -u pharmacie_management
```

---

## Modèles de données

| Modèle | Description |
|--------|-------------|
| `pharmacie.categorie` | Catégories thérapeutiques (hiérarchique) |
| `pharmacie.medicament` | Catalogue des médicaments |
| `pharmacie.lot` | Lots de stock avec dates de péremption |
| `pharmacie.vente` | Ventes au comptoir |
| `pharmacie.vente.ligne` | Lignes d'une vente |
| `pharmacie.ordonnance` | Ordonnances médicales |
| `pharmacie.posologie` | Détail posologique par médicament |
| `pharmacie.reappro` | Bons de commande fournisseur |
| `pharmacie.reappro.ligne` | Lignes d'un bon de commande |

---

## Groupes de sécurité

| Groupe | Droits |
|--------|--------|
| Vendeur | Lecture médicaments/stocks, Créer/voir ses propres ventes |
| Pharmacien | CRUD médicaments, stocks, ventes, ordonnances, réappro |
| Gestionnaire | Accès complet + rapports financiers |

---

## Rapports PDF

1. **Ticket de caisse** — depuis la fiche vente (menu Imprimer)
2. **Inventaire des stocks** — depuis la liste des lots
3. **Bilan de caisse** — depuis le wizard (Rapports > Bilan de caisse)
4. **Bon de commande fournisseur** — depuis la fiche réapprovisionnement

---

## Données de démonstration

Le fichier `data/pharmacie_data.xml` fournit :
- 8 catégories thérapeutiques (Antibiotiques, Antipaludéens, etc.)
- Les séquences automatiques pour toutes les références

Ajoutez vos données de test dans Odoo après installation.
