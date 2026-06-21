# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class PharmacieLot(models.Model):
    _name = 'pharmacie.lot'
    _description = 'Lot de stock'
    _order = 'date_peremption asc'

    numero_lot = fields.Char(
        string='Numéro de lot', copy=False, readonly=True, default='Nouveau',
    )
    medicament_id = fields.Many2one(
        comodel_name='pharmacie.medicament',
        string='Médicament', required=True, ondelete='cascade',
    )
    date_fabrication = fields.Date(string='Date de fabrication')
    date_peremption = fields.Date(string='Date de péremption', required=True)
    quantite_initiale = fields.Integer(
        string='Quantité initiale', required=True,
    )
    quantite_restante = fields.Integer(
        string='Quantité restante', required=True,
    )
    prix_achat_lot = fields.Float(
        string='Prix d\'achat du lot (FCFA)',
        help='Peut différer du prix catalogue si promotion ou négociation',
    )
    statut = fields.Selection([
        ('valide', 'Valide'),
        ('expire', 'Expiré'),
        ('epuise', 'Épuisé'),
    ], string='Statut', default='valide', compute='_compute_statut', store=True)
    jours_avant_peremption = fields.Integer(
        string='Jours avant péremption',
        compute='_compute_jours_avant_peremption',
        store=True,
    )
    reappro_id = fields.Many2one(
        comodel_name='pharmacie.reappro',
        string='Bon de commande d\'origine',
    )

    # ── Calculs ──────────────────────────────────────────────────────────
    @api.depends('date_peremption', 'quantite_restante')
    def _compute_statut(self):
        today = date.today()
        for lot in self:
            if lot.quantite_restante <= 0:
                lot.statut = 'epuise'
            elif lot.date_peremption and lot.date_peremption < today:
                lot.statut = 'expire'
            else:
                lot.statut = 'valide'

    @api.depends('date_peremption')
    def _compute_jours_avant_peremption(self):
        today = date.today()
        for lot in self:
            if lot.date_peremption:
                delta = lot.date_peremption - today
                lot.jours_avant_peremption = delta.days
            else:
                lot.jours_avant_peremption = 0

    # ── Contraintes ──────────────────────────────────────────────────────
    @api.constrains('date_fabrication', 'date_peremption')
    def _check_dates(self):
        for lot in self:
            if lot.date_fabrication and lot.date_peremption:
                if lot.date_peremption <= lot.date_fabrication:
                    raise ValidationError(
                        'La date de péremption doit être postérieure à la date de fabrication.'
                    )

    @api.constrains('quantite_initiale', 'quantite_restante')
    def _check_quantites(self):
        for lot in self:
            if lot.quantite_initiale < 0:
                raise ValidationError('La quantité initiale ne peut pas être négative.')
            if lot.quantite_restante < 0:
                raise ValidationError('La quantité restante ne peut pas être négative.')
            if lot.quantite_restante > lot.quantite_initiale:
                raise ValidationError(
                    'La quantité restante ne peut pas dépasser la quantité initiale.'
                )

    # ── Création avec séquence ────────────────────────────────────────────
    @api.model
    def create(self, vals):
        if vals.get('numero_lot', 'Nouveau') == 'Nouveau':
            vals['numero_lot'] = self.env['ir.sequence'].next_by_code(
                'pharmacie.lot'
            ) or 'LOT0001'
        return super().create(vals)

    def name_get(self):
        result = []
        for lot in self:
            name = f'{lot.numero_lot} — {lot.medicament_id.nom_commercial}'
            result.append((lot.id, name))
        return result
