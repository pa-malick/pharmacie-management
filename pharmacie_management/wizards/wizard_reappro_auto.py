# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class WizardReapproAutoLigne(models.TransientModel):
    _name = 'wizard.reappro.auto.ligne'
    _description = 'Ligne de réapprovisionnement automatique'

    wizard_id = fields.Many2one('wizard.reappro.auto', ondelete='cascade')
    medicament_id = fields.Many2one(
        comodel_name='pharmacie.medicament', string='Médicament', readonly=True,
    )
    fournisseur_id = fields.Many2one(
        comodel_name='res.partner', string='Fournisseur', readonly=True,
    )
    stock_actuel = fields.Integer(string='Stock actuel', readonly=True)
    alerte_rupture = fields.Integer(string='Seuil alerte', readonly=True)
    quantite_suggere = fields.Integer(string='Quantité suggérée')
    quantite_commander = fields.Integer(string='Quantité à commander')
    selected = fields.Boolean(string='Inclure', default=True)


class WizardReapproAuto(models.TransientModel):
    # Wizard de reapprovisionnement automatique.
    # Scanne les medicaments en alerte et genere un bon de commande par fournisseur.
    _name = 'wizard.reappro.auto'
    _description = 'Réapprovisionnement automatique'

    ligne_ids = fields.One2many(
        comodel_name='wizard.reappro.auto.ligne',
        inverse_name='wizard_id',
        string='Médicaments en alerte',
    )
    nb_alertes = fields.Integer(
        string='Nombre d\'alertes', compute='_compute_nb_alertes',
    )

    @api.depends('ligne_ids')
    def _compute_nb_alertes(self):
        for wiz in self:
            wiz.nb_alertes = len(wiz.ligne_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Scanner automatiquement les médicaments en alerte
        meds_en_alerte = self.env['pharmacie.medicament'].search([
            ('statut_stock', 'in', ('alerte', 'rupture')),
        ])
        lignes = []
        for med in meds_en_alerte:
            # Quantité suggérée = 2× le seuil d'alerte (minimum)
            qte_suggere = max(med.alerte_rupture * 2, 10)
            lignes.append((0, 0, {
                'medicament_id': med.id,
                'fournisseur_id': med.fournisseur_id.id if med.fournisseur_id else False,
                'stock_actuel': med.stock_actuel,
                'alerte_rupture': med.alerte_rupture,
                'quantite_suggere': qte_suggere,
                'quantite_commander': qte_suggere,
                'selected': True,
            }))
        res['ligne_ids'] = lignes
        return res

    def action_generer_commandes(self):
        # Cree un bon de commande par fournisseur en regroupant les medicaments selectionnes.
        lignes_selectionnees = self.ligne_ids.filtered(
            lambda l: l.selected and l.quantite_commander > 0
        )
        if not lignes_selectionnees:
            raise UserError('Sélectionnez au moins un médicament à commander.')

        Reappro = self.env['pharmacie.reappro']
        # Regroupement par fournisseur
        by_fournisseur = {}
        for ligne in lignes_selectionnees:
            fid = ligne.fournisseur_id.id if ligne.fournisseur_id else False
            if fid not in by_fournisseur:
                by_fournisseur[fid] = {
                    'fournisseur_id': fid,
                    'lignes': [],
                }
            by_fournisseur[fid]['lignes'].append({
                'medicament_id': ligne.medicament_id.id,
                'quantite_commandee': ligne.quantite_commander,
                'prix_unitaire': ligne.medicament_id.prix_achat,
            })

        reappros_crees = self.env['pharmacie.reappro']
        for fid, data in by_fournisseur.items():
            if not fid:
                raise UserError(
                    'Certains médicaments n\'ont pas de fournisseur assigné. '
                    'Veuillez les mettre à jour avant de générer les commandes.'
                )
            reappro = Reappro.create({
                'fournisseur_id': data['fournisseur_id'],
                'ligne_ids': [(0, 0, l) for l in data['lignes']],
            })
            reappros_crees |= reappro

        # Ouvre la liste des bons de commande créés
        if len(reappros_crees) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'pharmacie.reappro',
                'res_id': reappros_crees.id,
                'view_mode': 'form',
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pharmacie.reappro',
            'view_mode': 'list,form',
            'domain': [('id', 'in', reappros_crees.ids)],
            'name': 'Bons de commande générés',
        }
