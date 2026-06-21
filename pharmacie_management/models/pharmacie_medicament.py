# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PharmacieMedicament(models.Model):
    _name = 'pharmacie.medicament'
    _description = 'Médicament'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nom_commercial asc'

    # ── Identification ──────────────────────────────────────────────────
    nom_commercial = fields.Char(
        string='Nom commercial', required=True, tracking=True,
    )
    dci = fields.Char(
        string='DCI (Dénomination Commune Internationale)',
        help='Nom générique du principe actif, ex : Amoxicilline',
    )
    reference = fields.Char(
        string='Référence', copy=False, readonly=True, default='Nouveau',
    )
    forme = fields.Selection([
        ('comprime', 'Comprimé'),
        ('sirop', 'Sirop'),
        ('injectable', 'Injectable'),
        ('suppositoire', 'Suppositoire'),
        ('creme', 'Crème / Pommade'),
        ('gouttes', 'Gouttes'),
        ('capsule', 'Capsule'),
        ('poudre', 'Poudre'),
        ('patch', 'Patch'),
        ('autre', 'Autre'),
    ], string='Forme galénique', required=True)
    dosage = fields.Char(
        string='Dosage', help='ex : 500 mg, 250 mg/5 mL',
    )
    conditionnement = fields.Char(
        string='Conditionnement', help='ex : Boîte de 24, Flacon 100 mL',
    )

    # ── Classification ──────────────────────────────────────────────────
    categorie_id = fields.Many2one(
        comodel_name='pharmacie.categorie',
        string='Catégorie thérapeutique',
        required=True,
        tracking=True,
    )
    fournisseur_id = fields.Many2one(
        comodel_name='res.partner',
        string='Fournisseur principal',
        domain=[('is_fournisseur_pharma', '=', True)],
    )

    # ── Tarification ────────────────────────────────────────────────────
    prix_achat = fields.Float(
        string='Prix d\'achat (FCFA)', required=True, tracking=True,
    )
    prix_vente = fields.Float(
        string='Prix de vente (FCFA)', required=True, tracking=True,
    )
    taux_tva = fields.Selection([
        ('0', '0 % — Médicament essentiel'),
        ('18', '18 % — Autre médicament'),
    ], string='Taux TVA', required=True, default='0')
    marge_pct = fields.Float(
        string='Marge (%)',
        compute='_compute_marge',
        store=True,
    )

    # ── Réglementation ──────────────────────────────────────────────────
    sur_ordonnance = fields.Boolean(
        string='Sur ordonnance',
        help='Si coché, la vente est soumise à une ordonnance médicale',
        tracking=True,
    )

    # ── Stock ────────────────────────────────────────────────────────────
    stock_actuel = fields.Integer(
        string='Stock actuel (unités)',
        compute='_compute_stock_actuel',
        store=True,
    )
    alerte_rupture = fields.Integer(
        string='Seuil alerte rupture', default=10,
        help='Alerte déclenchée si stock tombe sous ce seuil',
    )
    lot_ids = fields.One2many(
        comodel_name='pharmacie.lot',
        inverse_name='medicament_id',
        string='Lots',
    )

    # ── Documentation ────────────────────────────────────────────────────
    notice = fields.Text(string='Notice / Indications')
    photo = fields.Binary(string='Photo', attachment=True)
    photo_name = fields.Char(string='Nom photo')

    # ── Statut visuel ────────────────────────────────────────────────────
    statut_stock = fields.Selection([
        ('ok', 'En stock'),
        ('alerte', 'Alerte rupture'),
        ('rupture', 'En rupture'),
    ], string='Statut stock', compute='_compute_statut_stock', store=True)

    # ── Calculs ──────────────────────────────────────────────────────────
    @api.depends('prix_achat', 'prix_vente')
    def _compute_marge(self):
        for med in self:
            if med.prix_achat > 0:
                med.marge_pct = (med.prix_vente - med.prix_achat) / med.prix_achat * 100
            else:
                med.marge_pct = 0.0

    @api.depends('lot_ids.quantite_restante', 'lot_ids.statut')
    def _compute_stock_actuel(self):
        for med in self:
            lots_valides = med.lot_ids.filtered(lambda l: l.statut == 'valide')
            med.stock_actuel = sum(lots_valides.mapped('quantite_restante'))

    @api.depends('stock_actuel', 'alerte_rupture')
    def _compute_statut_stock(self):
        for med in self:
            if med.stock_actuel <= 0:
                med.statut_stock = 'rupture'
            elif med.stock_actuel <= med.alerte_rupture:
                med.statut_stock = 'alerte'
            else:
                med.statut_stock = 'ok'

    # ── Contraintes ──────────────────────────────────────────────────────
    @api.constrains('prix_achat', 'prix_vente')
    def _check_prix(self):
        for med in self:
            if med.prix_achat < 0 or med.prix_vente < 0:
                raise ValidationError('Les prix ne peuvent pas être négatifs.')
            if med.prix_vente < med.prix_achat:
                raise ValidationError(
                    f'Le prix de vente ({med.prix_vente} FCFA) ne peut pas être '
                    f'inférieur au prix d\'achat ({med.prix_achat} FCFA).'
                )

    # ── Création avec séquence ────────────────────────────────────────────
    @api.model
    def create(self, vals):
        if vals.get('reference', 'Nouveau') == 'Nouveau':
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'pharmacie.medicament'
            ) or 'MED0001'
        return super().create(vals)

    def action_view_lots(self):
        self.ensure_one()
        return {
            'name': f'Lots — {self.nom_commercial}',
            'type': 'ir.actions.act_window',
            'res_model': 'pharmacie.lot',
            'view_mode': 'list,form',
            'domain': [('medicament_id', '=', self.id)],
            'context': {'default_medicament_id': self.id},
        }

    def name_get(self):
        result = []
        for med in self:
            name = med.nom_commercial
            if med.dci:
                name = f'{name} ({med.dci})'
            if med.dosage:
                name = f'{name} — {med.dosage}'
            result.append((med.id, name))
        return result
