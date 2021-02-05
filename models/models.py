# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Product(models.Model):
    _name = 'gvoyage.product'
    _description = 'Produit'
    _rec_name='code'

    code = fields.Char(required=True)
    desiniation = fields.Char(required=True)
    commission = fields.Float(required=True)
    Type = fields.Selection([('VERRE', 'VERRE'),('PET', 'PET'),('BOITE', 'BOITE')],string="Type",required=True)
    Eloignement = fields.Float(string='Eloignement',default=0.26,required=True)
    comission_Livreur = fields.Float(string='comission Livreur',required=True,default=0.12)


class voyage(models.Model):
    _name = 'gvoyage.voyage'
    _description = 'voyages'
    _rec_name='referance'

    currency_id = fields.Many2one('res.currency',required=True, string='Currency',default=lambda self: self.env.user.company_id.currency_id)
    date_depart = fields.Datetime(required=True,string="Date de Départ")
    nombre_factures = fields.Integer(string="Nombre des Factures",required=True)
    camion = fields.Many2one('fleet.vehicle',string='Camion',required=True)
    destination = fields.Many2many('gvoyage.destination',string="Liste des destinations",required=True)

    product_ids = fields.One2many('gvoyage.voyage_produit','voyage_id') #SORTIE
    voyage_produit_retour_ids = fields.One2many('gvoyage.voyage_produit_retour','voyage_id') #RETOUR

    

    #[(4,line.id)]
                

    # odoo: domain 


    salaire_emplyees = fields.Monetary(currency_field="currency_id",string="Total pointage des employés",store=True,compute='_compute_salaire_emplyees')
    # qte
    Qte_sortie = fields.Float(store=True,string='Quantité (sortie)',compute='_compute_rendement_sorite')
    Qte_retour = fields.Float(store=True,string='Quantité (retour)',compute='_compute_rendement_retour')
    Qte_livre = fields.Float(store=True,string='Quantité (Livre)',compute='_compute_Qte_livre')
    
    # commision
    total_sortie = fields.Monetary(currency_field="currency_id",string='Commission (sortie)',store=True,compute='_compute_rendement_sorite')
    total_retour = fields.Monetary(currency_field="currency_id",string='Commission (retour)',store=True,compute='_compute_rendement_retour')
    total_livre = fields.Monetary(currency_field="currency_id",string='Commission (Livre)',store=True,compute='_compute_Qte_livre')
    
    # Eloignement
    total_sortie_Eloignement = fields.Monetary(currency_field="currency_id",string='Eloignement (sortie)',store=True,compute='_compute_rendement_sorite')
    total_retour_Eloignement = fields.Monetary(currency_field="currency_id",string='Eloignement (retour)',store=True,compute='_compute_rendement_retour')
    total_Eloignement_livre = fields.Monetary(currency_field="currency_id",string='Eloignement (Livre)',store=True,compute='_compute_Qte_livre')
    
    total_sortie_comission_Livreur = fields.Monetary(currency_field="currency_id",store=True,string='comission Livreur (sortie)',compute='_compute_rendement_sorite')
    total_retour_comission_Livreur = fields.Monetary(currency_field="currency_id",store=True,string='comission Livreur (retour)',compute='_compute_rendement_retour')
    total_comission_Livreur_livre = fields.Monetary(currency_field="currency_id",string='comission Livreur (Livre)',store=True,compute='_compute_Qte_livre')

    rendement = fields.Monetary(currency_field="currency_id",store=True,compute ='_compute_rendement',string="rendement")
    Taux_caisse = fields.Monetary(currency_field="currency_id",store=True,compute ='_compute_rendement',string="Coût de Caisse")
    referance = fields.Char(string ='Référence de voyage',required=True)
    taux_retour = fields.Char(store=True,string='Taux de retour',compute ='_compute_taux_retour')
    emplyee_ids = fields.Many2many('hr.employee',string="Eeffectif",required=True)
    chauffeur =  fields.Many2one('hr.employee',string='Chauffeur',required=True)
    charges_ids = fields.One2many('gvoyage.charge_variable','voyage_id',string='Les charges')
    Chiffre_affaire = fields.Monetary(currency_field="currency_id",store=True,compute ='_compute_Chiffre_affaire',string="Chiffre d'affaire")
    Charges = fields.Monetary(currency_field="currency_id",store=True,compute ='_compute_charges',string="Montant des charges")
    charges_var = fields.Monetary(currency_field="currency_id",store=True,compute ='_compute_charges',string="Les charges variables")
    
    
    @api.depends('emplyee_ids','chauffeur','chauffeur.salaire')
    def _compute_salaire_emplyees(self):
        for rec in self:
            sum_emplyees = 0
            for line in rec.emplyee_ids:
                sum_emplyees += line.salaire
            sum_emplyees +=  rec.chauffeur.salaire
            rec.salaire_emplyees = sum_emplyees
                
    @api.depends('charges_ids','emplyee_ids','chauffeur','total_comission_Livreur_livre')
    def _compute_charges(self):
        for record in self:
            sum_charges=0
            for line in record.charges_ids:
                sum_charges += line.total
            record.charges_var=sum_charges
            record.Charges=sum_charges+record.salaire_emplyees+record.total_comission_Livreur_livre
                
    @api.depends('Qte_sortie','Qte_retour','Qte_livre')
    def _compute_Qte_livre(self):
        for record in self:
            record.Qte_livre=record.Qte_sortie - record.Qte_retour
            record.total_livre=record.total_sortie - record.total_retour
            record.total_Eloignement_livre=record.total_sortie_Eloignement - record.total_retour_Eloignement
            record.total_comission_Livreur_livre=record.total_sortie_comission_Livreur - record.total_retour_comission_Livreur
        
    @api.depends('total_livre','total_Eloignement_livre','Chiffre_affaire')
    def _compute_Chiffre_affaire(self):
        for record in self:
            record.Chiffre_affaire = record.total_livre + record.total_Eloignement_livre
            
    @api.depends('Qte_sortie','Qte_retour')
    def _compute_taux_retour(self):
        for record in self:
            if record.Qte_sortie>1:
                Temp = (record.Qte_retour/record.Qte_sortie*100)
            else:
                Temp  = 0
            record.taux_retour = str(round(Temp,3)) + "%"
    
    @api.depends('total_sortie','product_ids','total_sortie_Eloignement','total_sortie_comission_Livreur')
    def _compute_rendement_sorite(self):
        for record in self:
            sum_sous_rendement=0
            sum_Eloignement=0
            Qte_sortie = 0 
            comission_Livreur=0
            for line in record.product_ids:
                sum_sous_rendement=sum_sous_rendement+line.sous_rendement
                sum_Eloignement=sum_Eloignement+line.sous_eloignement
                Qte_sortie = Qte_sortie + line.quantite
                comission_Livreur = comission_Livreur + line.sous_comission_Livreur
            record.total_sortie=sum_sous_rendement
            record.total_sortie_Eloignement=sum_Eloignement
            record.Qte_sortie = Qte_sortie
            record.total_sortie_comission_Livreur = comission_Livreur
            

    @api.depends('total_retour','voyage_produit_retour_ids')
    def _compute_rendement_retour(self):
        for record in self:
            sumretour=0
            sum_retour_Eloignement=0
            Qte_retour=0
            comission_Livreur_retour = 0
            for line in record.voyage_produit_retour_ids:
                sumretour=sumretour+line.sous_rendement_retour
                sum_retour_Eloignement=sum_retour_Eloignement+line.sous_Eloignement_retour
                Qte_retour += line.quantite
                comission_Livreur_retour += line.sous_comission_Livreur_retour
            record.total_retour=sumretour
            record.total_retour_Eloignement=sum_retour_Eloignement
            record.Qte_retour = Qte_retour
            record.total_retour_comission_Livreur = comission_Livreur_retour
            
    
    @api.depends('Chiffre_affaire','rendement','Charges','total_livre','Qte_livre')
    def _compute_rendement(self):
        for record in self:
            record.rendement = record.Chiffre_affaire - record.Charges
            if record.Qte_livre !=0 :                
                record.Taux_caisse = record.Charges/record.Qte_livre
            else:
                record.Taux_caisse = 0
    def open_Products(self):
        context={'default_voyage_id':self.id,'group_by':'Type'}
        return {
            'name': ('liste des produits'),
            'domain': [('voyage_id','=',self.id)],
            'res_model': 'gvoyage.voyage_produit',
            'view_mode': 'tree,form',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context':context
        }
class voyage_produit(models.Model):
    _name = 'gvoyage.voyage_produit'
    _description = 'voyage_produit'

    quantite = fields.Float(required=True)
    voyage_id = fields.Many2one('gvoyage.voyage',required=True)
    product_id = fields.Many2one('gvoyage.product',string="Produit",required=True)
    desiniation = fields.Char(string="Designation",store=True,related='product_id.desiniation')
    Type = fields.Selection(related='product_id.Type',store=True)
    sous_rendement = fields.Float(store=True,compute='_compute_sous_rendement',string='Commission')
    sous_eloignement = fields.Float(store=True,compute='_compute_sous_rendement',string='Eloignement')
    sous_comission_Livreur = fields.Float(store=True,compute='_compute_sous_rendement',string='comission Livreur')

    @api.depends('sous_rendement','quantite','product_id','product_id.commission')
    def _compute_sous_rendement(self):
        for record in self:
            record.sous_rendement = record.product_id.commission * record.quantite
            record.sous_eloignement = record.product_id.Eloignement * record.quantite
            record.sous_comission_Livreur = record.product_id.comission_Livreur * record.quantite

class voyage_produit_retour(models.Model):


    _name = 'gvoyage.voyage_produit_retour'
    _description = 'voyage_produit_retour'

    quantite = fields.Float()
    voyage_id = fields.Many2one('gvoyage.voyage')
    product_id = fields.Many2one('gvoyage.product',required=True) 
    sous_rendement_retour = fields.Float(store=True,compute='_compute_sous_rendement_retour',string='Comission retour')
    sous_Eloignement_retour = fields.Float(store=True,compute='_compute_sous_rendement_retour',string='Eloignement')
    sous_comission_Livreur_retour = fields.Float(store=True,compute='_compute_sous_rendement_retour',string='comission_Livreur')
    sortie_ids=fields.Many2many('gvoyage.product',compute="_compute_p_sortie",store=True)

    @api.depends('voyage_id','voyage_id.product_ids','sortie_ids')
    def _compute_p_sortie(self):
        for rec in self:
            rec.sortie_ids = False 
            for line in rec.voyage_id.product_ids:
                rec.sortie_ids=[(4,line.product_id.id)]
    #costarinct

    @api.constrains('quantite')
    def _check_quantite(self):
        for rec in self:
            temp =  self.env['gvoyage.voyage_produit'].search([('product_id.id', '=', rec.product_id.id),('voyage_id.id', '=', rec.voyage_id.id)])
            print(temp.quantite)
            if temp.quantite < rec.quantite :
                raise ValidationError("la quantite de produit retourné est superieur a la quantite sortier veuiler verifier la quantite" + ';' + rec.product_id.code)



    


    @api.depends('sous_rendement_retour','quantite','product_id','product_id.commission')
    def _compute_sous_rendement_retour(self):
        for record in self:
            record.sous_rendement_retour = record.product_id.commission * record.quantite
            record.sous_Eloignement_retour = record.product_id.Eloignement * record.quantite
            record.sous_comission_Livreur_retour = record.product_id.comission_Livreur * record.quantite

class destination(models.Model):
    _name = 'gvoyage.destination'
    _description = 'destination'
    _rec_name='lieu'

    lieu = fields.Char(required=True)
    
class cheque(models.Model):
    _name = 'gvoyage.cheque'
    _description = 'cheque'
    _rec_name='numero_cheque'

    numero_cheque = fields.Char(required=True)
    notes = fields.Text(required=True)
    client =  fields.Many2one('res.partner',required=True,string='Client - Fournisseur')
    date = fields.Datetime(required=True,string="date d'échéance")
    Type = fields.Selection([('client', 'client'),('fournisseur','fournisseur')],required=True,default="client")
    state = fields.Selection([('attende', 'en attente'),('done','chèque payé'),('non_payé','impayé')],string="etat:",default='attende')
    banque = fields.Char(string="banque")

    @api.depends('state','date')
    def _compute_cheque_state(self):
        for record in self:
            record.state = 'attende'
    
class caisse(models.Model):
    _name = 'gvoyage.caisse'
    _description = 'caisse'  

    date = fields.Datetime(required=True)
    personne = fields.Char()
    note =  fields.Text(required=True)
    montant = fields.Float()
    Types = fields.Selection([('debut', 'debut'),('credit','credit')],required=True,default="credit")
    
class Avance(models.Model):
    _name = 'gvoyage.avance'
    _description = 'avance sur salaire '
    _rec_name="employee_id"
    
    employee_id = fields.Many2one('hr.employee',string='employee',required=True)
    date = fields.Date(string="date",required=True)
    montant = fields.Float(string="montant",required=True)
    
    
class hr_employee(models.Model):
    _inherit = 'hr.employee'
    salaire = fields.Float(required=True,string='salaire par jour')



class fleet_viecule(models.Model):

    _inherit='fleet.vehicle.log.fuel'

    
    #liter=fields.Float(required=True,string='Liter')
    product_id=fields.Many2one('product.template',string='product name',required=True)
    picking_type_id = fields.Many2one('stock.picking.type',compute='_compute_picking_type_id',default=False)
    picking_id = fields.Many2one('stock.picking',string='',default=False)
    location_id = fields.Many2one( 'stock.location', 'Source Location',compute='_compute_picking_type_id')
    location_dest_id = fields.Many2one( 'stock.location', 'Source Location',compute='_compute_picking_type_id')
    is_gasoil=fields.Boolean(string='gasoil')
    

    

    @api.depends('picking_type_id')
    def _compute_picking_type_id(self):
        for rec in self:
            picking_type_ids=self.env['stock.picking.type'].search([['sequence_code', '=', 'OUT']])
            rec.picking_type_id = picking_type_ids[0].id
            rec.location_id = rec.picking_type_id.default_location_src_id.id
            rec.location_dest_id = rec.picking_type_id.default_location_dest_id.id

    def compute_confirm(self):
        for rec in self:
            # stock
            company_id = self.env.user.company_id.id

            #total=self.env['gvoyage.charge_variable'].search(['total'])
        
            picking_vals = {    'origin': 'Operation',
                                'partner_id': False,
                                'user_id': False,
                                'picking_type_id': rec.picking_type_id.id,
                                'company_id': company_id,
                                'move_type': 'direct',
                                'note': "notes",
                                'location_id':rec.location_id.id,
                                'location_dest_id':rec.location_dest_id.id
                            }
            picking_id=self.env['stock.picking'].create(picking_vals)
            rec.picking_id = picking_id
            if rec.liter <= 0:
                raise ValidationError('au moins liter plus  grand de zero ')
            self.env['stock.move'].create( {  
                    'product_id':rec.product_id.id,
                    'product_uom_qty':rec.liter,
                    'quantity_done':rec.liter,    
                    'picking_id':picking_id.id,
                    'name':rec.product_id.name,
                    'product_uom':rec.product_id.uom_id.id,
                    'location_id':rec.location_id.id,
                    'location_dest_id':rec.location_dest_id.id
                })
        picking_id.action_confirm()
        picking_id.action_assign()
        picking_id.action_done()
        # les charges
        vals = {
            'name':'oggg',
            'total':rec.amount,
            'type_charge':1
        }

        self.env['gvoyage.charge_variable'].create(vals)





class viecule(models.Model):

    _inherit='fleet.vehicle'

    
    #liter=fields.Float(required=True,string='Liter')
    #liter=fields.Float(required=True,string='Liter')
    total_km=fields.Float(string='Total kilométrage',compute='_compute_total_km',default=1)
    total_fuel=fields.Float(string='Total Fuel',compute='_compute_total_fuel')
    mconsomassion=fields.Float(string='Consommation',compute='_compute_mconsomassion')
    
    
    
    @api.onchange('total_km','log_fuel','log_fuel.odometer')
    def _compute_total_km(self):
        total=0.0
        for rec in self:
            if len(rec.log_fuel ) > 0 :
                rec.total_km=rec.odometer-rec.log_fuel[0].odometer
            else:
                rec.total_km=1
        

        
    
    
    @api.onchange('mconsomassion','total_fuel','total_km')
    def _compute_mconsomassion(self):
        for rec in self:
            if rec.total_km > 0:
                rec.mconsomassion=(rec.total_fuel / rec.total_km ) * 100.00
            else: 
                rec.mconsomassion=1

    
    
    @api.onchange('total_fuel','log_fuel','log_fuel.odometer')
    def _compute_total_fuel(self):
        for rec in self:
            total=0.0   
            log_ids =self.env['fleet.vehicle.log.fuel'].search([['is_gasoil', '=', True],['vehicle_id','=',rec.id]])
            if len(rec.log_fuel) > 0:
                # print(log_ids)
                # for line in rec.log_fuel:
                #     if line.is_gasoil == True :
                #         total+=line.liter
                # total=total-rec.log_fuel[-1].liter
                # rec.total_fuel=total
                for line in log_ids:
                    total+=line.liter
                total=total-rec.log_fuel[-1].liter
                rec.total_fuel=total 
            else:
                rec.total_fuel=0


