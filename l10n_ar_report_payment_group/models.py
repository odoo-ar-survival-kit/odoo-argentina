from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    @api.multi
    def payment_print(self):
        for apg in self:
            self.env['report'].get_action(self, 'l10n_ar_report_payment_group.report_payment_group')
