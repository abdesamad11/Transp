# -*- coding: utf-8 -*-

from odoo import models, fields, api,  _
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class gvoyage_type_charge(models.Model):
    _name = 'gvoyage.type_charge'
    _description="les charges"
    _rec_name= "name"
    
    name = fields.Char(string="nome")
    
class gvoyage_charge(models.Model):
    _name = 'gvoyage.charge'
    _description="les charges"
    _rec_name= "name"
    _inherit = ['mail.thread']

    type_charge = fields.Many2one('gvoyage.type_charge',required=True)
    name  = fields.Char(required=True,string="Titre")
    date_debut  = fields.Date(required=True,string="date",default=fields.Datetime.now())
    currency_id = fields.Many2one('res.currency',required=True, string='Currency',default=lambda self: self.env.user.company_id.currency_id)
    total = fields.Monetary(currency_field="currency_id",required=True,string="Montant:",track_visibility="always")
    notes  = fields.Text(string="notes")
    date_fin =fields.Date(string="date Fin",required=False)
    sous_charges_ids = fields.One2many('gvoyage.charge_variable','charge_parent_id',string="les sous charges")
    
    # def confirm(self):
    #     for rec in self:
    #         for sous_charges_id in rec.sous_charges_ids:
    #             sous_charges_id.unlink()
                
    #         prix_jour = rec.total/26/len(rec.equipe_ids)
    #         for equip in  rec.equipe_ids:
    #             sdate = rec.date_debut
    #             edate = rec.date_fin
    #             delta = edate - sdate 
    #             for i in range(delta.days + 1):
    #                 day = sdate + timedelta(days=i)
                    
    #                 if day.weekday() != 6:
    #                     charge_variable={
    #                         'type_charge':rec.type_charge.id,
    #                         'name':'%s equipe' % (rec.name),
    #                         'date':day,
    #                         'total':prix_jour,
    #                         'equipe_id':equip.id,
    #                         'charge_parent_id':self.id
    #                     }
    #                     self.env["gvoyage.charge_variable"].create(charge_variable)
                

class gvoyage_charge_variable(models.Model):
    _name = 'gvoyage.charge_variable'
    _description="charges variable"
    _rec_name= "name"

    type_charge = fields.Many2one('gvoyage.type_charge',required=True)
    name  = fields.Char(required=True,string="Titre")
    date  = fields.Date(required=True,string="date",default=fields.Datetime.now())
    currency_id = fields.Many2one('res.currency',required=True, string='Currency',default=lambda self: self.env.user.company_id.currency_id)
    total = fields.Monetary(currency_field="currency_id",required=True,string="Montant:",track_visibility="always")
    notes  = fields.Text(string="note")
    voyage_id = fields.Many2one('gvoyage.voyage')
    charge_parent_id=fields.Many2one('gvoyage.charge',string="charge parent",readonly=True,ondelete="cascade")
   
    

class gvoyage_prime(models.Model):
    _name = 'gvoyage.prime'
    _description="les primes"
    _rec_name= "name"
    _inherit = ['mail.thread']

    name  = fields.Char(required=True,string="Titre")
    date  = fields.Date(required=True,string="date",default=fields.Datetime.now())
    currency_id = fields.Many2one('res.currency',required=True, string='Currency',default=lambda self: self.env.user.company_id.currency_id)
    total = fields.Monetary(currency_field="currency_id",required=True,string="Montant:",track_visibility="always")
    notes  = fields.Text(string="note")
    employee_id = fields.Many2one('hr.employee',required=True,string='employee')

    
