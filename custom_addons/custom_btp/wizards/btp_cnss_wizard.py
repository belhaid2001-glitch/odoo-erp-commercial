# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api
from odoo.exceptions import UserError


class BtpCnssWizard(models.TransientModel):
    """Wizard — Export CNSS : Génère le fichier DUE téléchargeable"""
    _name = 'btp.cnss.wizard'
    _description = 'Export CNSS — Bordereau DUE'

    # ── Champs ─────────────────────────────────────────────────
    chantier_id = fields.Many2one(
        'btp.chantier', string='Chantier', required=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    mois = fields.Selection([
        ('01', 'Janvier'), ('02', 'Février'), ('03', 'Mars'),
        ('04', 'Avril'), ('05', 'Mai'), ('06', 'Juin'),
        ('07', 'Juillet'), ('08', 'Août'), ('09', 'Septembre'),
        ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre'),
    ], string='Mois', required=True)
    annee = fields.Char('Année', required=True, default=lambda self: str(fields.Date.today().year))
    nb_jours = fields.Integer('Nombre de jours travaillés', default=26, required=True)

    # Fichier généré
    file_data = fields.Binary('Fichier DUE', readonly=True)
    file_name = fields.Char('Nom du fichier', readonly=True)
    state = fields.Selection([
        ('config', 'Configuration'),
        ('done', 'Terminé'),
    ], default='config')

    # ── Actions ────────────────────────────────────────────────
    def action_generer_due(self):
        """Génère le fichier DUE au format texte à positions fixes CNSS Maroc"""
        self.ensure_one()

        chantier = self.chantier_id
        company = chantier.company_id or self.env.company
        code_employeur = (company.company_registry or '').ljust(8)[:8]

        lines_txt = []
        # En-tête
        lines_txt.append("E{code}{mois}{annee}".format(
            code=code_employeur,
            mois=self.mois,
            annee=self.annee.ljust(4)[:4],
        ))

        total_jours = 0
        total_salaire = 0

        for res in chantier.ressource_ids:
            cnss = (res.numero_cnss or '').ljust(8)[:8]
            cin = (res.numero_cin or '').ljust(8)[:8]
            nom = (res.name or '').ljust(30)[:30]
            jours = str(self.nb_jours).rjust(2, '0')
            salaire_brut = res.taux_horaire * 8 * self.nb_jours
            salaire_str = str(int(salaire_brut * 100)).rjust(9, '0')  # centimes, 9 chars

            line = "S{cnss}{cin}{nom}{jours}{salaire}".format(
                cnss=cnss,
                cin=cin,
                nom=nom,
                jours=jours,
                salaire=salaire_str,
            )
            lines_txt.append(line)
            total_jours += self.nb_jours
            total_salaire += salaire_brut

        # Pied
        lines_txt.append("T{nb:04d}{jours:06d}{salaire:012d}".format(
            nb=len(chantier.ressource_ids),
            jours=total_jours,
            salaire=int(total_salaire * 100),
        ))

        content = '\r\n'.join(lines_txt)
        file_data = base64.b64encode(content.encode('ascii', errors='replace'))
        file_name = "CNSS_DUE_{chantier}_{mois}_{annee}.txt".format(
            chantier=chantier.reference or 'CHT',
            mois=self.mois,
            annee=self.annee,
        )

        self.write({
            'file_data': file_data,
            'file_name': file_name,
            'state': 'done',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
