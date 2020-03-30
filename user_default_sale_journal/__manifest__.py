{
    'name': "User default sale journal",
    'version': '13.0.1.0',
    'depends': ['account'],
    'author': "Filoquin",
    'category': 'account',
    'description': """
        Add default sale journal for users 
    """,
    # data files always loaded at installation
    'data': [
        'views/res_users_default_journal.xml',
    ],
}
