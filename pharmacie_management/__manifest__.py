# -*- coding: utf-8 -*-
{
    'name': 'Pharmacie Management',
    'version': '18.0.1.0.0',
    'category': 'Health',
    'summary': 'Gestion complète d\'une officine pharmaceutique sénégalaise',
    'description': '''
        Module de gestion de pharmacie :
        - Catalogue de médicaments (DCI, forme, dosage, TVA)
        - Gestion des lots et stocks avec alertes de péremption
        - Ventes au comptoir avec gestion des ordonnances
        - Réapprovisionnement fournisseurs
        - Rapports PDF (ticket, inventaire, bilan de caisse, bon de commande)
        - Sécurité par profil (Vendeur, Pharmacien, Gestionnaire)
    ''',
    'author': 'Université Alioune DIOP — Master 2 DSGL',
    'website': 'https://www.uadb.edu.sn',
    'depends': ['base', 'mail', 'account'],
    'data': [
        # 1) Sécurité en premier
        'security/pharmacie_security.xml',
        'security/ir.model.access.csv',
        # 2) Données initiales
        'data/pharmacie_data.xml',
        # 3) Rapports en premier (les vues y font référence)
        'report/report_actions.xml',
        'report/report_ticket_caisse.xml',
        'report/report_inventaire_stock.xml',
        'report/report_bilan_caisse.xml',
        'report/report_bon_commande.xml',
        # 4) Vues
        'views/pharmacie_categorie_views.xml',
        'views/pharmacie_medicament_views.xml',
        'views/pharmacie_lot_views.xml',
        'views/pharmacie_vente_views.xml',
        'views/pharmacie_ordonnance_views.xml',
        'views/pharmacie_reappro_views.xml',
        'views/res_partner_views_inherit.xml',
        # 5) Wizards
        'wizards/wizard_reappro_auto_views.xml',
        'wizards/wizard_bilan_caisse_views.xml',
        # 6) Menus en dernier
        'views/pharmacie_menu.xml',
    ],
    'demo': [
        'demo/pharmacie_demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
