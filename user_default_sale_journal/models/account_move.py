# -*- coding: utf-8 -*-
from odoo import api, fields , models, _
from odoo.exceptions import  UserError

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    @api.model
    def _get_default_journal(self):
        ''' Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        '''
        move_type = self._context.get('default_type', 'entry')
        journal_type = 'general'
        if move_type in self.get_sale_types(include_receipts=True):
            journal_type = 'sale'
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_type = 'purchase'

        if self._context.get('default_journal_id'):
            journal = self.env['account.journal'].browse(self._context['default_journal_id'])

            if move_type != 'entry' and journal.type != journal_type:
                raise UserError(_("Cannot create an invoice of type %s with a journal having %s as type.") % (move_type, journal.type))
        else:
            company_id = self._context.get('default_company_id', self.env.company.id)
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

            journal = None

            if journal_type == 'sale':
                domain +=[('sale_default_user_ids','=',self._uid)]
            if self._context.get('default_currency_id'):
                currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
                journal = self.env['account.journal'].search(currency_domain, limit=1)

            if not journal:

                journal = self.env['account.journal'].search(domain, limit=1)
            if not journal:
                error_msg = _('Please define an accounting miscellaneous journal in your company')
                if journal_type == 'sale':
                    error_msg = _('Please define an accounting sale journal in your user and company')
                elif journal_type == 'purchase':
                    error_msg = _('Please define an accounting purchase journal in your company')
                raise UserError(error_msg)
        return journal

    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]",
        default=lambda self: self._get_default_journal())
