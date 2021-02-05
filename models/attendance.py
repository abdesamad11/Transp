
from odoo import models, fields, api,  _
from odoo.exceptions import ValidationError
	
class hr_employee(models.Model):
    _inherit = 'hr.employee'

	
   
    cin = fields.Char(string="Numéro CIN", required=False)
    matricule_cnss = fields.Char(string="Numéro CNSS", required=False)
    matricule_cimr = fields.Char(string="Numéro CIMR", required=False)
    matricule_mut = fields.Char(string="Numéro MUTUELLE", required=False)
    num_chezemployeur = fields.Integer(string="Matricule")
    abs = fields.Integer(string="Absence en heures" ,default=0)
    hs25 = fields.Integer(string="Heures sup à 25" ,default=0)
    hs50 = fields.Integer(string="Heures sup à 50",default=0)
    hs100 = fields.Integer(string="Heures sup à 100",default=0)
    av_sal = fields.Integer(string="Avance sur Salaire",default=0)   
    rem_mut = fields.Integer(string="Remboursement Mutuelle",default=0)
    salaire = fields.Float(required=True,string='salaire par jour',default=0)
    
class gvoyage_attendance(models.Model):
    _name = 'gvoyage.attendance'
    _rec_name="work_day"
    _inherit = ['mail.thread']

    work_day  = fields.Date(string="date",default=fields.Datetime.now())
    work_day_id  = fields.Many2one('gvoyage.workday',compute="_compute_workday")
    employee_id = fields.Many2one('hr.employee',string='employee')
    state = fields.Selection([('absent', 'absent'),('present','present')],required=True,default="absent")
    state_val = fields.Integer(store=True,string="etat",compute='_compute_etat')
    salaire = fields.Float(required=True,string='salaire par jour')

    
    @api.depends('state','state_val')
    def _compute_etat(self):
        for rec in self:
            if rec.state =='absent':
               rec.state_val=0
            if rec.state =='present':
               rec.state_val=1
                

    @api.depends('work_day','work_day_id')
    def _compute_workday(self):
        for Rec in self:
            records_pointgae = self.env['gvoyage.workday'].search([('work_day', '=',Rec.work_day)])
            if len(records_pointgae)>=1:
                Rec.work_day_id=records_pointgae[0].id 
            else:
                Rec.work_day_id=False
    
    @api.constrains('employee_id')
    def _validate_unique_employee_id(self):
        for rec in self:
            records_pointgae = self.env['gvoyage.attendance'].search([('work_day', '=',rec.work_day),('employee_id', '=',rec.employee_id.id)])
            if len(records_pointgae) > 1:
                ErrorMessage =  'le pointaeg de ce jour pour '+ str(rec.employee_id.name)  +' deja'
                raise ValidationError(_(ErrorMessage))      
                      
    def mark_absent(self):
        for rec in self:
            rec.state='absent'

    def mark_present(self):
        for rec in self:
            rec.state='present'
            
class gvoyage_workday(models.Model):
    _name = 'gvoyage.workday'
    _rec_name='rec_name'
    _inherit = ['mail.thread']

    work_day  = fields.Date(string="jour de travaille",default=fields.Datetime.now(),readonly=True)
    attendance_ids = fields.One2many('gvoyage.attendance', 'work_day_id')
    rec_name = fields.Char(compute="_compute_rec_name")
   
    @api.depends('work_day')
    def _compute_rec_name(self):
        for Rec in self:
            Rec.rec_name = 'Pointage de jour:'+' '+ str(Rec.work_day.day)+'/'+ str(Rec.work_day.month) +'/'+ str(Rec.work_day.year)
    
    
    @api.constrains('work_day')
    def _validate_work_day(self):
        for rec in self:
            records_pointgae = self.env['gvoyage.workday'].search([('work_day', '=',rec.work_day)])
            if len(records_pointgae) > 1:
                raise ValidationError(_('le pointaeg de ce jour exist deja '))
    
    @api.model
    def create(self, vals):
        rec = super(gvoyage_workday, self).create(vals)
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            data={
                'work_day':rec.work_day,
                'work_day_id':rec.id,
                'employee_id':employee.id,
                'state':'absent',
                'salaire':employee.salaire
            }
            self.env['gvoyage.attendance'].create(data)
        return rec   