# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartnerExtend(models.Model):
    _inherit = 'res.partner'

    is_fournisseur_pharma = fields.Boolean(
        string='Fournisseur pharmaceutique',
        help='Distingue les fournisseurs/grossistes pharmaceutiques des autres contacts',
    )
    delai_livraison_moyen = fields.Integer(
        string='Délai de livraison moyen (jours)',
        help='Délai habituel de livraison en jours ouvrés',
    )
    numero_agrement = fields.Char(
        string='N° Agrément DPM',
        help='Numéro d\'agrément Direction de la Pharmacie et du Médicament (Sénégal)',
    )
    reappro_ids = fields.One2many(
        comodel_name='pharmacie.reappro',
        inverse_name='fournisseur_id',
        string='Bons de commande',
    )
    reappro_count = fields.Integer(
        string='Nb commandes',
        compute='_compute_reappro_count',
    )

    def _compute_reappro_count(self):
        for partner in self:
            partner.reappro_count = len(partner.reappro_ids)

    def action_view_reappros(self):
        return {
            'name': 'Bons de commande',
            'type': 'ir.actions.act_window',
            'res_model': 'pharmacie.reappro',
            'view_mode': 'list,form',
            'domain': [('fournisseur_id', '=', self.id)],
            'context': {'default_fournisseur_id': self.id},
        }
