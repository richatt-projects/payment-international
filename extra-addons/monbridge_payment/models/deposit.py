from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MonbridgeDeposit(models.Model):
    _name = 'monbridge.deposit'
    _description = 'monBridge Deposit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    company_id = fields.Many2one('monbridge.company', required=True, ondelete='restrict', tracking=True)
    amount = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True)
    destination_bank = fields.Char(required=True)
    deposit_date = fields.Date(default=fields.Date.context_today, required=True)
    state = fields.Selection([
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ], default='pending', required=True, tracking=True)
    reference = fields.Char()
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name') in (False, 'New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('monbridge.deposit') or 'New'
        return super().create(vals_list)

    def action_verify(self):
        for rec in self:
            if rec.state != 'pending':
                continue
            balance = self.env['monbridge.company.balance'].search([
                ('company_id', '=', rec.company_id.id),
                ('currency_id', '=', rec.currency_id.id),
            ], limit=1)
            if not balance:
                balance = self.env['monbridge.company.balance'].create({
                    'company_id': rec.company_id.id,
                    'currency_id': rec.currency_id.id,
                })
            balance.write({
                'balance': balance.balance + rec.amount,
                'available_balance': balance.available_balance + rec.amount,
            })
            rec.state = 'verified'

    def action_reject(self):
        self.write({'state': 'rejected'})
