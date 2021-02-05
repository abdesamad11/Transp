# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class MarcheReportPointage(models.Model):
    _name = "gvoyage.report.pointage"
    _description = "Analysis Pointage"
    _auto = False
    _order = 'date desc'
    _rec_name = 'date'
    _order = 'date desc'

    id =  fields.Integer("id", readonly=True)
    date = fields.Date("Jour", readonly=True)
    employee_id = fields.Many2one('hr.employee',string='employee', readonly=True)
    total_pointage = fields.Float(string='total pointage')
    total_primes = fields.Float(string='total primes')
    note_prime = fields.Char(string="note de prime",readonly=True)
    total_avance =  fields.Float(string='total avance')
    total_payer =  fields.Float(string='total a payer')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""
        
        select_ = """
        att.id as id,
        att.salaire as total_pointage,
        COALESCE(att.work_day,avance.date_avance) as date,
        COALESCE(avance.montant_avance,0) as total_avance ,
        att.employee_id as employee_id ,
        COALESCE(att.salaire,0)+COALESCE(primes.prime,0)-COALESCE(avance.montant_avance,0) as total_payer,
        COALESCE(primes.prime,0) as total_primes ,
        primes.note_prime as note_prime """
                        
        for field in fields.values():
            select_ += field
            
        from_ = """ 
        gvoyage_attendance att
FULL join  (select total as prime ,name as note_prime ,date as date_prime ,employee_id as employee_id  from gvoyage_prime ) as primes on (primes.employee_id =att.employee_id and att.work_day =primes.date_prime)
FULL join  (select montant as montant_avance  ,date as date_avance ,employee_id as employee_id  from gvoyage_avance) as avance on (avance.employee_id = att.employee_id and att.work_day = avance.date_avance)

        %s
        """ % from_clause
        
    
        
        return '%s (SELECT %s FROM %s where att.state_val=1)' % (with_, select_, from_)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))