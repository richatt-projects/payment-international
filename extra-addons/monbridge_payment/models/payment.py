from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class MonbridgePayment(models.Model):
    _name = 'monbridge.payment'
    _description = 'monBridge Payment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    company_id = fields.Many2one('monbridge.company', required=True, ondelete='restrict', tracking=True)
    beneficiary_id = fields.Many2one('monbridge.beneficiary', required=True, ondelete='restrict')
    beneficiary_bank_id = fields.Many2one('monbridge.beneficiary.bank', required=True, ondelete='restrict')
    source_currency_id = fields.Many2one('res.currency', string='Balance Currency', required=True)
    target_currency_id = fields.Many2one('res.currency', string='Receiving Currency', required=True)
    amount = fields.Monetary(required=True, currency_field='source_currency_id')
    converted_amount = fields.Float()
    fx_quote_id = fields.Many2one('monbridge.fx.quote')
    fee_amount = fields.Float()
    reference = fields.Char(readonly=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ], default='draft', required=True, tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')
    ai_extraction_ids = fields.One2many('monbridge.ai.extraction', 'payment_id')
    transaction_ids = fields.One2many('monbridge.transaction', 'payment_id')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name') in (False, 'New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('monbridge.payment') or 'New'
            if not vals.get('reference'):
                vals['reference'] = vals['name']
        return super().create(vals_list)

    @api.onchange('beneficiary_id')
    def _onchange_beneficiary(self):
        if self.beneficiary_id:
            self.beneficiary_bank_id = self.beneficiary_id.default_bank_id

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_('Payment amount must be greater than zero.'))

    def action_submit(self):
        for rec in self:
            if rec.company_id.state != 'approved':
                raise UserError(_('The customer company must be approved.'))
            if rec.beneficiary_id.verification_state != 'verified':
                raise UserError(_('The beneficiary must be verified.'))
            if rec.beneficiary_bank_id.verification_state != 'verified':
                raise UserError(_('The beneficiary bank account must be verified.'))
            rec.state = 'pending_approval'

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_process(self):
        for rec in self:
            balance = self.env['monbridge.company.balance'].search([
                ('company_id', '=', rec.company_id.id),
                ('currency_id', '=', rec.source_currency_id.id),
            ], limit=1)
            if not balance or balance.available_balance < rec.amount:
                raise UserError(_('Insufficient available balance.'))
            balance.write({'available_balance': balance.available_balance - rec.amount})
            rec.state = 'processing'

    def action_mark_paid(self):
        self.write({'state': 'paid'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_fail(self):
        self.write({'state': 'failed'})
