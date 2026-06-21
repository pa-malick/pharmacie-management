# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PharmacieCategorie(models.Model):
    _name = 'pharmacie.categorie'
    _description = 'Catégorie de médicament'
    _order = 'name asc'
    # Auto-référencement pour hiérarchie parent/enfant
    # Ex : Antibiotiques > Pénicillines > Amoxicilline
    _parent_store = True

    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')

    parent_id = fields.Many2one(
        comodel_name='pharmacie.categorie',
        string='Catégorie parente',
        ondelete='restrict',
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        comodel_name='pharmacie.categorie',
        inverse_name='parent_id',
        string='Sous-catégories',
    )
    medicament_ids = fields.One2many(
        comodel_name='pharmacie.medicament',
        inverse_name='categorie_id',
        string='Médicaments',
    )
    medicament_count = fields.Integer(
        string='Nb médicaments',
        compute='_compute_medicament_count',
    )

    @api.depends('medicament_ids')
    def _compute_medicament_count(self):
        for cat in self:
            cat.medicament_count = len(cat.medicament_ids)

    def name_get(self):
        result = []
        for cat in self:
            if cat.parent_id:
                result.append((cat.id, f'{cat.parent_id.name} / {cat.name}'))
            else:
                result.append((cat.id, cat.name))
        return result
