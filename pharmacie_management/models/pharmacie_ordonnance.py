# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PharmaciePosologie(models.Model):
    _name = 'pharmacie.posologie'
    _description = 'Posologie d\'une ordonnance'
    _order = 'id asc'

    ordonnance_id = fields.Many2one(
        comodel_name='pharmacie.ordonnance',
        string='Ordonnance', required=True, ondelete='cascade',
    )
    medicament_id = fields.Many2one(
        comodel_name='pharmacie.medicament',
        string='Médicament', required=True,
    )
    posologie = fields.Char(
        string='Posologie',
        help='ex : 1 comprimé matin et soir pendant 7 jours',
        required=True,
    )
    duree = fields.Char(string='Durée du traitement')
    quantite_prescrite = fields.Integer(string='Quantité prescrite')


class PharmacieOrdonnance(models.Model):
    _name = 'pharmacie.ordonnance'
    _description = 'Ordonnance médicale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_prescription desc'

    reference = fields.Char(
        string='Référence', copy=False, readonly=True, default='Nouveau',
    )

    # Informations du patient
    patient_nom = fields.Char(string='Nom du patient', required=True)
    patient_age = fields.Integer(string='Âge')
    patient_genre = fields.Selection([
        ('m', 'Masculin'),
        ('f', 'Féminin'),
    ], string='Genre')

    # Informations du medecin prescripteur
    medecin_nom = fields.Char(string='Nom du médecin', required=True)
    structure_sante = fields.Char(
        string='Structure de santé',
        help='Hôpital, clinique ou cabinet',
    )
    date_prescription = fields.Date(
        string='Date de prescription', required=True,
        default=fields.Date.today,
    )

    # Medicaments prescrits (M2M) et detail des posologies (O2M)
    medicament_ids = fields.Many2many(
        comodel_name='pharmacie.medicament',
        relation='pharmacie_ordonnance_medicament_rel',
        column1='ordonnance_id',
        column2='medicament_id',
        string='Médicaments prescrits',
    )
    posologie_ids = fields.One2many(
        comodel_name='pharmacie.posologie',
        inverse_name='ordonnance_id',
        string='Détail posologique',
    )

    # Statut de delivrance et lien vers la vente associee
    statut = fields.Selection([
        ('attente', 'En attente'),
        ('partielle', 'Délivrée partiellement'),
        ('delivree', 'Délivrée complètement'),
    ], string='Statut', default='attente', tracking=True)
    vente_id = fields.Many2one(
        comodel_name='pharmacie.vente',
        string='Vente associée', readonly=True,
    )

    # Scan numerique de l'ordonnance papier (optionnel)
    scan_ordonnance = fields.Binary(string='Scan / Photo de l\'ordonnance')
    scan_ordonnance_name = fields.Char(string='Nom du fichier')
    notes = fields.Text(string='Notes internes')

    # Validation : la date de prescription ne peut pas etre dans le futur
    @api.constrains('date_prescription')
    def _check_date_prescription(self):
        today = fields.Date.today()
        for ordo in self:
            if ordo.date_prescription and ordo.date_prescription > today:
                raise ValidationError(
                    'La date de prescription ne peut pas être dans le futur.'
                )

    # Attribution automatique de la reference via sequence ir.sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'pharmacie.ordonnance'
                ) or 'ORD0001'
        return super().create(vals_list)

    def _compute_display_name(self):
        for ordo in self:
            ordo.display_name = f'{ordo.reference} — {ordo.patient_nom} ({ordo.medecin_nom})'
