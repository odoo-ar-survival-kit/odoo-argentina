# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import datetime
from datetime import datetime, timedelta, date

class AccountPayment(models.Model):
	_inherit = 'account.paymentt'

"""
	def _compute_price_subtotal_vat(self):
		for line in self:
                    if line.tax_ids:
                        for tax_id in line.tax_ids:
                            if tax_id.tax_group_id.tax_type == 'vat':
                                line.price_subtotal_vat = line.price_subtotal * ( 1 + tax_id.amount / 100 )

	price_subtotal_vat = fields.Float('price_subtotal_vat',compute=_compute_price_subtotal_vat)
"""

