# -*- coding: utf-8 -*-
from odoo import api, fields, models,_

from odoo.exceptions import  ValidationError

class ResUsersDefaultSaleJournal(models.Model):
    _name = 'res.users.default_sale_journal'
    _description = 'Default sale journal by user'

    user_id = fields.Many2one(
        'res.users',
        string='User',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Sale journal',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related="journal_id.company_id",
        readonly=True, 
        store=True,
    )

    @api.constrains('user_id','company_id','journal_id')
    def company_constrain(self):
        if self.journal_id.company_id.id not in self.user_id.company_ids.ids :
            raise  ValidationError(_('The journal company not in user company'))
        is_defined = self.search([('id','<>',self.id),('user_id','=',self.user_id.id),('company_id','=',self.company_id.id)])
        if len(is_defined):
            raise  ValidationError(_('This user has default journal for this company'))
