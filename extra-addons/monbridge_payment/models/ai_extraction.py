from odoo import fields, models

class MonbridgeAiExtraction(models.Model):
    _name = 'monbridge.ai.extraction'
    _description = 'AI Document Extraction'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(required=True)
    payment_id = fields.Many2one('monbridge.payment', ondelete='cascade')
    attachment_id = fields.Many2one('ir.attachment', ondelete='set null')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('needs_review', 'Needs Human Review'),
        ('failed', 'Failed'),
    ], default='pending', required=True, tracking=True)
    confidence = fields.Float()
    extracted_data = fields.Json()
    error_message = fields.Text()

    def action_needs_review(self):
        self.write({'status': 'needs_review'})
