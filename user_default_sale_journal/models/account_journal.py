# -*- coding: utf-8 -*-
from odoo import  fields, models

class AccountJournal(models.Model):

    _inherit = 'account.journal'

    sale_default_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='res_users_default_sale_journal',
        column1='journal_id',
        column2='user_id',
        string="sale default user ids"
    )

