# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class PharmacieReapproLigne(models.Model):
    _name = 'pharmacie.reappro.ligne'
    _description = 'Ligne de réapprovisionnement'
    _order = 'id asc'

    reappro_id = fields.Many2one(
        comodel_name='pharmacie.reappro',
        string='Bon de commande', required=True, ondelete='cascade',
    )
    medicament_id = fields.Many2one(
        comodel_name='pharmacie.medicament',
        string='Médicament', required=True,
    )
    quantite_commandee = fields.Integer(
        string='Quantité commandée', required=True, default=1,
    )
    quantite_recue = fields.Integer(
        string='Quantité reçue', default=0,
    )
    prix_unitaire = fields.Float(string='Prix unitaire (FCFA)')
    montant_ligne = fields.Float(
        string='Montant (FCFA)',
        compute='_compute_montant_ligne',
        store=True,
    )
    date_peremption_prevue = fields.Date(string='Date de péremption du lot reçu')

    @api.onchange('medicament_id')
    def _onchange_medicament(self):
        if self.medicament_id:
            self.prix_unitaire = self.medicament_id.prix_achat

    @api.depends('quantite_commandee', 'prix_unitaire')
    def _compute_montant_ligne(self):
        for ligne in self:
            ligne.montant_ligne = ligne.quantite_commandee * ligne.prix_unitaire

    @api.constrains('quantite_commandee')
    def _check_quantite(self):
        for ligne in self:
            if ligne.quantite_commandee <= 0:
                raise ValidationError('La quantité commandée doit être supérieure à 0.')


class PharmacieReappro(models.Model):
    _name = 'pharmacie.reappro'
    _description = 'Bon de commande fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_commande desc'

    reference = fields.Char(
        string='Référence', copy=False, readonly=True, default='Nouveau',
    )
    fournisseur_id = fields.Many2one(
        comodel_name='res.partner',
        string='Fournisseur', required=True,
        domain=[('is_fournisseur_pharma', '=', True)],
    )
    date_commande = fields.Date(
        string='Date de commande', required=True, default=fields.Date.today,
    )
    date_livraison_prevue = fields.Date(string='Date de livraison prévue')
    ligne_ids = fields.One2many(
        comodel_name='pharmacie.reappro.ligne',
        inverse_name='reappro_id',
        string='Lignes de commande',
    )
    montant_total = fields.Float(
        string='Montant total (FCFA)',
        compute='_compute_montant_total',
        store=True,
    )
    statut = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('commande', 'Commandé'),
        ('partiel', 'Reçu partiellement'),
        ('recu', 'Reçu'),
        ('annule', 'Annulé'),
    ], string='Statut', default='brouillon', tracking=True)
    note_interne = fields.Text(string='Notes internes / Conditions de livraison')

    # ── Calculs ──────────────────────────────────────────────────────────
    @api.depends('ligne_ids.montant_ligne')
    def _compute_montant_total(self):
        for reappro in self:
            reappro.montant_total = sum(reappro.ligne_ids.mapped('montant_ligne'))

    # ── Contraintes ──────────────────────────────────────────────────────
    @api.constrains('date_commande', 'date_livraison_prevue')
    def _check_dates(self):
        for reappro in self:
            if (reappro.date_commande and reappro.date_livraison_prevue
                    and reappro.date_livraison_prevue < reappro.date_commande):
                raise ValidationError(
                    'La date de livraison prévue doit être postérieure à la date de commande.'
                )

    # ── Workflow ──────────────────────────────────────────────────────────
    def action_envoyer_commande(self):
        for reappro in self:
            if not reappro.ligne_ids:
                raise UserError('Ajoutez au moins un médicament avant d\'envoyer la commande.')
            reappro.statut = 'commande'

    def action_receptionner(self):
        """
        Crée automatiquement les lots pharmacie.lot pour chaque ligne reçue
        et met à jour le statut selon la réception complète ou partielle.
        """
        Lot = self.env['pharmacie.lot']
        for reappro in self:
            if reappro.statut not in ('commande', 'partiel'):
                raise UserError('Seules les commandes en cours peuvent être réceptionnées.')

            all_complete = True
            for ligne in reappro.ligne_ids:
                if ligne.quantite_recue <= 0:
                    all_complete = False
                    continue
                if not ligne.date_peremption_prevue:
                    raise UserError(
                        f'Veuillez renseigner la date de péremption pour : '
                        f'{ligne.medicament_id.nom_commercial}'
                    )
                # Création du lot correspondant
                Lot.create({
                    'medicament_id': ligne.medicament_id.id,
                    'quantite_initiale': ligne.quantite_recue,
                    'quantite_restante': ligne.quantite_recue,
                    'prix_achat_lot': ligne.prix_unitaire,
                    'date_peremption': ligne.date_peremption_prevue,
                    'reappro_id': reappro.id,
                })
                if ligne.quantite_recue < ligne.quantite_commandee:
                    all_complete = False

            reappro.statut = 'recu' if all_complete else 'partiel'

    def action_annuler(self):
        for reappro in self:
            if reappro.statut in ('recu',):
                raise UserError('Un bon de commande déjà réceptionné ne peut pas être annulé.')
            reappro.statut = 'annule'

    # ── Création avec séquence ────────────────────────────────────────────
    @api.model
    def create(self, vals):
        if vals.get('reference', 'Nouveau') == 'Nouveau':
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'pharmacie.reappro'
            ) or 'BC0001'
        return super().create(vals)
