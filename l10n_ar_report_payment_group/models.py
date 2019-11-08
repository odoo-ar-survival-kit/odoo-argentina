from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    @api.multi
    def payment_print(self):
        report = self.env['ir.actions.report']._get_report_from_name('l10n_ar_report_payment_group.report_payment_group')
        for apg in self:
            return report.report_action(docids=[apg.id])
