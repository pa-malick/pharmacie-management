# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PharmacieVenteLigne(models.Model):
    _name = 'pharmacie.vente.ligne'
    _description = 'Ligne de vente'
    _order = 'id asc'

    vente_id = fields.Many2one(
        comodel_name='pharmacie.vente',
        string='Vente', required=True, ondelete='cascade',
    )
    medicament_id = fields.Many2one(
        comodel_name='pharmacie.medicament',
        string='Médicament', required=True,
    )
    lot_id = fields.Many2one(
        comodel_name='pharmacie.lot',
        string='Lot',
        domain="[('medicament_id', '=', medicament_id), ('statut', '=', 'valide')]",
    )
    quantite = fields.Integer(string='Quantité', required=True, default=1)
    prix_unitaire = fields.Float(string='Prix unitaire (FCFA)')
    taux_tva = fields.Float(string='TVA (%)', compute='_compute_tva', store=True)
    montant_ht = fields.Float(
        string='Montant HT', compute='_compute_montants', store=True,
    )
    montant_tva = fields.Float(
        string='Montant TVA', compute='_compute_montants', store=True,
    )
    montant_ttc = fields.Float(
        string='Montant TTC', compute='_compute_montants', store=True,
    )
    sur_ordonnance = fields.Boolean(
        related='medicament_id.sur_ordonnance', string='Sur ordonnance', readonly=True,
    )

    @api.onchange('medicament_id')
    def _onchange_medicament(self):
        if self.medicament_id:
            self.prix_unitaire = self.medicament_id.prix_vente
            # Prend le lot valide avec la péremption la plus proche (FEFO)
            lot = self.env['pharmacie.lot'].search([
                ('medicament_id', '=', self.medicament_id.id),
                ('statut', '=', 'valide'),
                ('quantite_restante', '>', 0),
            ], order='date_peremption asc', limit=1)
            self.lot_id = lot

    @api.depends('medicament_id.taux_tva')
    def _compute_tva(self):
        for ligne in self:
            ligne.taux_tva = float(ligne.medicament_id.taux_tva or '0')

    @api.depends('quantite', 'prix_unitaire', 'taux_tva')
    def _compute_montants(self):
        for ligne in self:
            ligne.montant_ht = ligne.quantite * ligne.prix_unitaire
            ligne.montant_tva = ligne.montant_ht * ligne.taux_tva / 100
            ligne.montant_ttc = ligne.montant_ht + ligne.montant_tva

    @api.constrains('quantite')
    def _check_quantite(self):
        for ligne in self:
            if ligne.quantite <= 0:
                raise ValidationError('La quantité doit être supérieure à 0.')


class PharmacieVente(models.Model):
    _name = 'pharmacie.vente'
    _description = 'Vente au comptoir'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_vente desc'

    reference = fields.Char(
        string='Référence', copy=False, readonly=True, default='Nouveau',
    )
    client_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client', help='Optionnel — client fidélisé',
    )
    vendeur_id = fields.Many2one(
        comodel_name='res.users',
        string='Vendeur', required=True,
        default=lambda self: self.env.user,
    )
    ordonnance_id = fields.Many2one(
        comodel_name='pharmacie.ordonnance',
        string='Ordonnance',
    )
    ligne_ids = fields.One2many(
        comodel_name='pharmacie.vente.ligne',
        inverse_name='vente_id',
        string='Lignes de vente',
    )
    montant_ht = fields.Float(
        string='Montant HT (FCFA)', compute='_compute_totaux', store=True,
    )
    tva = fields.Float(
        string='TVA (FCFA)', compute='_compute_totaux', store=True,
    )
    montant_ttc = fields.Float(
        string='Total TTC (FCFA)', compute='_compute_totaux', store=True,
    )
    statut = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('confirme', 'Confirmée'),
        ('annule', 'Annulée'),
    ], string='Statut', default='brouillon', tracking=True)
    mode_paiement = fields.Selection([
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
        ('free_money', 'Free Money'),
    ], string='Mode de paiement', required=True, default='especes')
    date_vente = fields.Datetime(string='Date de vente', readonly=True)
    note = fields.Text(string='Observations')

    # Calcul des totaux HT, TVA et TTC a partir des lignes de vente
    @api.depends('ligne_ids.montant_ht', 'ligne_ids.montant_tva', 'ligne_ids.montant_ttc')
    def _compute_totaux(self):
        for vente in self:
            vente.montant_ht = sum(vente.ligne_ids.mapped('montant_ht'))
            vente.tva = sum(vente.ligne_ids.mapped('montant_tva'))
            vente.montant_ttc = sum(vente.ligne_ids.mapped('montant_ttc'))

    # Actions de workflow : confirmer (avec controles stock + ordonnance), annuler
    def action_confirmer(self):
        for vente in self:
            if vente.statut != 'brouillon':
                continue

            # Vérification ordonnance pour les médicaments qui l'exigent
            lignes_ordo = vente.ligne_ids.filtered(
                lambda l: l.medicament_id.sur_ordonnance
            )
            if lignes_ordo and not vente.ordonnance_id:
                noms = ', '.join(lignes_ordo.mapped('medicament_id.nom_commercial'))
                raise UserError(
                    f'Une ordonnance est obligatoire pour : {noms}'
                )

            # Vérification des stocks et décrémentation des lots
            for ligne in vente.ligne_ids:
                stock = ligne.medicament_id.stock_actuel
                if stock < ligne.quantite:
                    raise UserError(
                        f'Stock insuffisant pour {ligne.medicament_id.nom_commercial}. '
                        f'Stock disponible : {stock} unité(s).'
                    )
                # Décrémentation FEFO (First Expiry First Out)
                remaining = ligne.quantite
                lots = self.env['pharmacie.lot'].sudo().search([
                    ('medicament_id', '=', ligne.medicament_id.id),
                    ('statut', '=', 'valide'),
                    ('quantite_restante', '>', 0),
                ], order='date_peremption asc')
                for lot in lots:
                    if remaining <= 0:
                        break
                    debit = min(lot.quantite_restante, remaining)
                    lot.sudo().write({'quantite_restante': lot.quantite_restante - debit})
                    remaining -= debit

            vente.write({
                'statut': 'confirme',
                'date_vente': fields.Datetime.now(),
            })
            # Mettre à jour le statut de l'ordonnance si liée
            if vente.ordonnance_id:
                vente.ordonnance_id.write({
                    'statut': 'delivree',
                    'vente_id': vente.id,
                })

    def action_annuler(self):
        for vente in self:
            if vente.statut == 'confirme':
                raise UserError(
                    'Une vente confirmée ne peut pas être annulée directement. '
                    'Contactez le pharmacien responsable.'
                )
            vente.statut = 'annule'

    def action_brouillon(self):
        for vente in self:
            if vente.statut == 'confirme':
                raise UserError(
                    'Une vente confirmée ne peut pas être remise en brouillon. '
                    'Contactez le pharmacien responsable.'
                )
            vente.statut = 'brouillon'

    # Attribution automatique de la reference via sequence ir.sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'pharmacie.vente'
                ) or 'VTE0001'
        return super().create(vals_list)
