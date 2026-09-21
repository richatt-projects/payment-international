from odoo import fields, models

class MonbridgeFxQuote(models.Model):
    _name = 'monbridge.fx.quote'
    _description = 'Foreign Exchange Quote'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(default='FX Quote', required=True)
    company_id = fields.Many2one('monbridge.company', required=True, ondelete='cascade')
    source_currency_id = fields.Many2one('res.currency', required=True)
    target_currency_id = fields.Many2one('res.currency', required=True)
    rate = fields.Float(required=True, digits=(16, 8))
    source = fields.Char()
    valid_until = fields.Datetime(required=True)
    accepted = fields.Boolean(default=False, tracking=True)
    accepted_at = fields.Datetime(readonly=True)

    def action_accept(self):
        self.write({
            'accepted': True,
            'accepted_at': fields.Datetime.now(),
        })
