# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models


class MarcheReportRecap(models.Model):
    _name = "gvoyage.report.recap"
    _description = "Recap"
    _auto = False
    _order = 'date desc'
    _rec_name = 'date'
    _order = 'date desc'

    nombre_voyage = fields.Integer("Nombre de voyages ", readonly=True)
    total_livre = fields.Integer("total_livre (Livre)", readonly=True)
    total_eloignement_livre = fields.Float("Eloignement (Livre)", readonly=True)
    total_comission_livreur_livre = fields.Float("Comission Livreur", readonly=True)
    salaire_emplyees = fields.Float("id", "poinatge des emplyees", readonly=True)
    rondemnt = fields.Float("rondemnt", readonly=True)
    total_charges = fields.Float("Total des Charges", readonly=True)
    cout_caisse = fields.Float("cout caisse", readonly=True)
    qte_livre = fields.Integer("Qte livre", readonly=True)
    date = fields.Date("date", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
       min(v.id) as id,
        count(v.id) as nombre_voyage,
-- chiffre d'affaire 
        COALESCE(sum(v."total_livre"),0) as total_livre,
        COALESCE(sum(v."total_Eloignement_livre"),0) as total_eloignement_livre,
-- total les charges 
        COALESCE(sum(v."total_comission_Livreur_livre"),0) as total_comission_livreur_livre,
        COALESCE(sum(p."salaire"),0) as salaire_emplyees, -- fix 
        COALESCE(sum(c.total),0) as total_charges, 
        (COALESCE(sum(v."total_livre"),0)+COALESCE(sum(v."total_Eloignement_livre"),0)-COALESCE(sum(v."total_comission_Livreur_livre"),0)-COALESCE(sum(p."salaire"),0)-COALESCE(sum(c.total),0)) as rondemnt,
        (COALESCE(sum(v."total_comission_Livreur_livre"),0)+COALESCE(sum(p."salaire"),0)+COALESCE(sum(c.total),0))/COALESCE(sum(v."Qte_livre"),1) as cout_caisse,
        COALESCE(sum(v."Qte_livre"),0) as qte_livre,
        DATE_TRUNC('month',v.date_depart) as date  """

        for field in fields.values():
            select_ += field

        from_ = """ 
            gvoyage_voyage v 
        full join gvoyage_charge_variable c on (DATE_TRUNC('month',date) = DATE_TRUNC('month',v.date_depart))
        full join gvoyage_attendance p on (DATE_TRUNC('month',work_day) = DATE_TRUNC('month',v.date_depart))
        group by DATE_TRUNC('month',v.date_depart)
        %s
        """ % from_clause

        return '%s (SELECT %s FROM %s)' % (with_, select_, from_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (
            self._table, self._query()))
