from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MonbridgeBeneficiary(models.Model):
    _name = 'monbridge.beneficiary'
    _description = 'monBridge Beneficiary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Legal Name', required=True, tracking=True)
    company_id = fields.Many2one('monbridge.company', required=True, ondelete='cascade', tracking=True)
    country_id = fields.Many2one('res.country', required=True)
    street = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    email = fields.Char()
    phone = fields.Char()
    tax_reference = fields.Char()
    verification_state = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='pending', required=True, tracking=True)
    bank_ids = fields.One2many('monbridge.beneficiary.bank', 'beneficiary_id')
    default_bank_id = fields.Many2one(
        'monbridge.beneficiary.bank',
        compute='_compute_default_bank',
        store=False,
    )

    @api.depends('bank_ids', 'bank_ids.is_default')
    def _compute_default_bank(self):
        for rec in self:
            rec.default_bank_id = rec.bank_ids.filtered('is_default')[:1] or rec.bank_ids[:1]

    def action_verify(self):
        self.write({'verification_state': 'verified'})

    def action_reject(self):
        self.write({'verification_state': 'rejected'})

class MonbridgeBeneficiaryBank(models.Model):
    _name = 'monbridge.beneficiary.bank'
    _description = 'Beneficiary Bank Account'
    _inherit = ['mail.thread']
    _order = 'is_default desc, id desc'

    beneficiary_id = fields.Many2one('monbridge.beneficiary', required=True, ondelete='cascade')
    bank_name = fields.Char(required=True)
    account_holder_name = fields.Char(required=True)
    account_number = fields.Char()
    iban = fields.Char()
    swift_bic = fields.Char()
    currency_id = fields.Many2one('res.currency', required=True)
    is_default = fields.Boolean()
    verification_state = fields.Selection([
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='pending', required=True, tracking=True)

    @api.constrains('is_default', 'beneficiary_id')
    def _check_one_default(self):
        for rec in self.filtered('is_default'):
            others = self.search([
                ('beneficiary_id', '=', rec.beneficiary_id.id),
                ('id', '!=', rec.id),
                ('is_default', '=', True),
            ], limit=1)
            if others:
                raise ValidationError(_('A beneficiary can have only one default bank account.'))

    def action_verify(self):
        self.write({'verification_state': 'verified'})
