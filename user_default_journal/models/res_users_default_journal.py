# -*- coding: utf-8 -*-
from odoo import api, fields, models,_

from odoo.exceptions import  ValidationError

class ResUsersDefaultJournal(models.Model):
    _name = 'res.users.default_journal'
    _description = 'Default journal by user'

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
        is_defined = self.search([('user_id','=',self.user_id.id),('company_id','=',self.company_id.id)])
        if len(is_defined):
            raise  ValidationError(_('This user has default journal for this company'))
