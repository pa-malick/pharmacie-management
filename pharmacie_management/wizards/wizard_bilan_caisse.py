# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizardBilanCaisse(models.TransientModel):
    """
    Wizard : bilan de caisse sur une période sélectionnée.
    Calcule le CA, le nombre de ventes, le panier moyen et le détail par vendeur.
    """
    _name = 'wizard.bilan.caisse'
    _description = 'Bilan de caisse'

    date_debut = fields.Date(
        string='Date de début', required=True, default=fields.Date.today,
    )
    date_fin = fields.Date(
        string='Date de fin', required=True, default=fields.Date.today,
    )

    # ── Résultats calculés ─────────────────────────────────────────────
    ca_total = fields.Float(string='Chiffre d\'affaires TTC (FCFA)', readonly=True)
    nb_ventes = fields.Integer(string='Nombre de ventes', readonly=True)
    panier_moyen = fields.Float(string='Panier moyen (FCFA)', readonly=True)
    ligne_ids = fields.One2many(
        comodel_name='wizard.bilan.caisse.ligne',
        inverse_name='wizard_id',
        string='Détail par vendeur',
        readonly=True,
    )
    calcule = fields.Boolean(default=False)

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for wiz in self:
            if wiz.date_debut and wiz.date_fin and wiz.date_fin < wiz.date_debut:
                raise ValidationError(
                    'La date de fin doit être postérieure ou égale à la date de début.'
                )

    def action_calculer(self):
        """Calcule les indicateurs de la période sélectionnée."""
        Vente = self.env['pharmacie.vente']
        ventes = Vente.search([
            ('statut', '=', 'confirme'),
            ('date_vente', '>=', fields.Datetime.to_datetime(self.date_debut)),
            ('date_vente', '<=', fields.Datetime.to_datetime(self.date_fin).replace(
                hour=23, minute=59, second=59
            )),
        ])

        self.nb_ventes = len(ventes)
        self.ca_total = sum(ventes.mapped('montant_ttc'))
        self.panier_moyen = self.ca_total / self.nb_ventes if self.nb_ventes else 0.0

        # Détail par vendeur
        self.ligne_ids = [(5, 0, 0)]  # Effacer les anciennes lignes
        by_vendeur = {}
        for vente in ventes:
            vid = vente.vendeur_id.id
            if vid not in by_vendeur:
                by_vendeur[vid] = {
                    'vendeur_id': vid,
                    'nb_ventes': 0,
                    'ca': 0.0,
                }
            by_vendeur[vid]['nb_ventes'] += 1
            by_vendeur[vid]['ca'] += vente.montant_ttc

        lignes = []
        for vid, data in by_vendeur.items():
            pm = data['ca'] / data['nb_ventes'] if data['nb_ventes'] else 0
            lignes.append((0, 0, {
                'vendeur_id': data['vendeur_id'],
                'nb_ventes': data['nb_ventes'],
                'ca_vendeur': data['ca'],
                'panier_moyen': pm,
            }))
        self.ligne_ids = lignes
        self.calcule = True

        # Retourne la même vue (reste ouvert)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.bilan.caisse',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_generer_rapport(self):
        """Lance la génération du rapport PDF de bilan de caisse."""
        if not self.calcule:
            self.action_calculer()
        return self.env.ref(
            'pharmacie_management.action_report_bilan_caisse'
        ).report_action(self)


class WizardBilanCaisseLigne(models.TransientModel):
    _name = 'wizard.bilan.caisse.ligne'
    _description = 'Ligne de bilan de caisse par vendeur'

    wizard_id = fields.Many2one('wizard.bilan.caisse', ondelete='cascade')
    vendeur_id = fields.Many2one('res.users', string='Vendeur', readonly=True)
    nb_ventes = fields.Integer(string='Nb ventes', readonly=True)
    ca_vendeur = fields.Float(string='CA (FCFA)', readonly=True)
    panier_moyen = fields.Float(string='Panier moyen (FCFA)', readonly=True)
