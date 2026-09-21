from odoo import fields, models

class MonbridgeTransaction(models.Model):
    _name = 'monbridge.transaction'
    _description = 'monBridge Transaction'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    payment_id = fields.Many2one('monbridge.payment', required=True, ondelete='cascade')
    execution_reference = fields.Char(required=True)
    executed_at = fields.Datetime()
    amount = fields.Float()
    currency_id = fields.Many2one('res.currency')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('reconciled', 'Reconciled'),
    ], default='pending', required=True, tracking=True)
    provider = fields.Char()
    response_payload = fields.Text()

    def action_success(self):
        self.write({'state': 'success'})

    def action_reconcile(self):
        self.write({'state': 'reconciled'})
