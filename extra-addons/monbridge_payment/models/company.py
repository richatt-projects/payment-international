from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MonbridgeCompany(models.Model):
    _name = 'monbridge.company'
    _description = 'monBridge Customer Company'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', tracking=True)
    registration_number = fields.Char()
    country_id = fields.Many2one('res.country', required=True)
    state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ], default='pending', required=True, tracking=True)
    active = fields.Boolean(default=True)
    currency_balance_ids = fields.One2many('monbridge.company.balance', 'company_id')
    beneficiary_ids = fields.One2many('monbridge.beneficiary', 'company_id')
    payment_ids = fields.One2many('monbridge.payment', 'company_id')
    deposit_ids = fields.One2many('monbridge.deposit', 'company_id')

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_suspend(self):
        self.write({'state': 'suspended'})

class MonbridgeCompanyBalance(models.Model):
    _name = 'monbridge.company.balance'
    _description = 'monBridge Company Currency Balance'
    _rec_name = 'currency_id'

    company_id = fields.Many2one('monbridge.company', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', required=True, ondelete='restrict')
    balance = fields.Monetary(default=0, currency_field='currency_id')
    available_balance = fields.Monetary(default=0, currency_field='currency_id')

    _sql_constraints = [
        ('company_currency_unique', 'unique(company_id, currency_id)',
         'Only one balance per company and currency is allowed.')
    ]
