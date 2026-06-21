# Diagramme UML — Module `pharmacie_management`

## Diagramme de classes (Mermaid)

```mermaid
classDiagram
    direction LR

    class pharmacie_categorie {
        +Char name
        +Char code
        +Text description
        +Many2one parent_id
        +One2many child_ids
        +One2many medicament_ids
        +Integer medicament_count [computed]
    }

    class pharmacie_medicament {
        +Char reference [séquence]
        +Char nom_commercial
        +Char dci
        +Selection forme
        +Char dosage
        +Char conditionnement
        +Many2one categorie_id
        +Many2one fournisseur_id
        +Float prix_achat
        +Float prix_vente
        +Selection taux_tva
        +Float marge_pct [computed]
        +Boolean sur_ordonnance
        +Integer stock_actuel [computed]
        +Integer alerte_rupture
        +Selection statut_stock [computed]
        +Text notice
        +Binary photo
    }

    class pharmacie_lot {
        +Char numero_lot [séquence]
        +Many2one medicament_id
        +Date date_fabrication
        +Date date_peremption
        +Integer quantite_initiale
        +Integer quantite_restante
        +Float prix_achat_lot
        +Selection statut [computed]
        +Integer jours_avant_peremption [computed]
        +Many2one reappro_id
    }

    class pharmacie_vente {
        +Char reference [séquence]
        +Many2one client_id
        +Many2one vendeur_id
        +Many2one ordonnance_id
        +One2many ligne_ids
        +Float montant_ht [computed]
        +Float tva [computed]
        +Float montant_ttc [computed]
        +Selection statut
        +Selection mode_paiement
        +Datetime date_vente
        +Text note
        +action_confirmer()
        +action_annuler()
    }

    class pharmacie_vente_ligne {
        +Many2one vente_id
        +Many2one medicament_id
        +Many2one lot_id
        +Integer quantite
        +Float prix_unitaire
        +Float taux_tva [computed]
        +Float montant_ht [computed]
        +Float montant_tva [computed]
        +Float montant_ttc [computed]
    }

    class pharmacie_ordonnance {
        +Char reference [séquence]
        +Char patient_nom
        +Integer patient_age
        +Selection patient_genre
        +Char medecin_nom
        +Char structure_sante
        +Date date_prescription
        +Many2many medicament_ids
        +One2many posologie_ids
        +Selection statut
        +Many2one vente_id
        +Binary scan_ordonnance
    }

    class pharmacie_posologie {
        +Many2one ordonnance_id
        +Many2one medicament_id
        +Char posologie
        +Char duree
        +Integer quantite_prescrite
    }

    class pharmacie_reappro {
        +Char reference [séquence]
        +Many2one fournisseur_id
        +Date date_commande
        +Date date_livraison_prevue
        +One2many ligne_ids
        +Float montant_total [computed]
        +Selection statut
        +Text note_interne
        +action_envoyer_commande()
        +action_receptionner()
    }

    class pharmacie_reappro_ligne {
        +Many2one reappro_id
        +Many2one medicament_id
        +Integer quantite_commandee
        +Integer quantite_recue
        +Float prix_unitaire
        +Float montant_ligne [computed]
        +Date date_peremption_prevue
    }

    class res_partner {
        +Boolean is_fournisseur_pharma
        +Integer delai_livraison_moyen
        +Char numero_agrement
        +One2many reappro_ids
    }

    %% Relations
    pharmacie_categorie "1" --> "0..*" pharmacie_categorie : parent_id (auto-ref)
    pharmacie_categorie "1" --> "0..*" pharmacie_medicament : categorie_id

    pharmacie_medicament "1" --> "0..*" pharmacie_lot : medicament_id
    pharmacie_medicament "0..*" --> "1" res_partner : fournisseur_id

    pharmacie_lot "0..*" --> "1" pharmacie_reappro : reappro_id

    pharmacie_vente "1" --> "1..*" pharmacie_vente_ligne : ligne_ids
    pharmacie_vente "0..*" --> "0..1" pharmacie_ordonnance : ordonnance_id
    pharmacie_vente "0..*" --> "0..1" res_partner : client_id

    pharmacie_vente_ligne "0..*" --> "1" pharmacie_medicament : medicament_id
    pharmacie_vente_ligne "0..*" --> "0..1" pharmacie_lot : lot_id

    pharmacie_ordonnance "1" --> "0..*" pharmacie_posologie : posologie_ids
    pharmacie_ordonnance "0..*" --> "0..*" pharmacie_medicament : medicament_ids (M2M)

    pharmacie_reappro "1" --> "1..*" pharmacie_reappro_ligne : ligne_ids
    pharmacie_reappro "0..*" --> "1" res_partner : fournisseur_id

    pharmacie_reappro_ligne "0..*" --> "1" pharmacie_medicament : medicament_id

    pharmacie_posologie "0..*" --> "1" pharmacie_medicament : medicament_id
```

---

## Diagramme de flux — Processus de vente

```mermaid
flowchart TD
    A([Vendeur ouvre une nouvelle vente]) --> B[Saisie des lignes de vente]
    B --> C{Médicament sur ordonnance ?}
    C -->|Oui| D[Lier une ordonnance médicale]
    C -->|Non| E[Choisir mode de paiement]
    D --> E
    E --> F[Cliquer sur Confirmer]
    F --> G{Stock suffisant\npour chaque ligne ?}
    G -->|Non| H[❌ Erreur : Stock insuffisant]
    H --> B
    G -->|Oui| I[Décrémentation FEFO\ndes lots valides]
    I --> J[Statut vente → Confirmée]
    J --> K[Date_vente = maintenant]
    K --> L{Ordonnance liée ?}
    L -->|Oui| M[Statut ordonnance → Délivrée]
    L -->|Non| N([Impression ticket PDF])
    M --> N
```

---

## Diagramme de flux — Réapprovisionnement

```mermaid
flowchart TD
    A([Pharmacien ouvre le wizard\nRéappro automatique]) --> B[Scan des médicaments\nsous seuil d'alerte]
    B --> C[Affichage liste avec\nquantités suggérées]
    C --> D[Ajustement des quantités\npar le pharmacien]
    D --> E[Valider]
    E --> F[Regroupement par fournisseur]
    F --> G[Création des bons de commande\npharmacerie.reappro]
    G --> H[Statut → Commandé]
    H --> I([Impression BC fournisseur PDF])
    I --> J([Attente livraison])
    J --> K[Réception physique]
    K --> L[Saisie quantités reçues\n+ dates péremption]
    L --> M[Clic Réceptionner]
    M --> N[Création automatique\ndes lots pharmacie.lot]
    N --> O{Tout reçu ?}
    O -->|Oui| P[Statut → Reçu]
    O -->|Non| Q[Statut → Reçu partiellement]
```

---

## Schéma des groupes de sécurité

```mermaid
graph TD
    V[Vendeur] --> P[Pharmacien]
    P --> G[Gestionnaire]

    V_desc["— Lecture : médicaments, stocks, ordonnances
    — Créer/Lire : ses propres ventes
    — Accès : Caisse + Ordonnances"]
    
    P_desc["— CRUD : médicaments, stocks, ventes, ordonnances
    — CRUD : réapprovisionnements
    — Accès : tout sauf rapports financiers"]
    
    G_desc["— Accès total sur tous les modèles
    — Rapports financiers et bilan de caisse
    — Configuration et paramètres"]

    V -.-> V_desc
    P -.-> P_desc
    G -.-> G_desc

    style V fill:#e3f2fd
    style P fill:#e8f5e9
    style G fill:#fff3e0
```
