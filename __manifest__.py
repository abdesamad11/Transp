# -*- coding: utf-8 -*-
{
    'name': "gvoyage",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','hr','board','product','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/produit.xml',
        'views/attendance.xml',
        'views/voyage.xml',
        'views/employee.xml',
        'views/charges.xml',
        'views/cheque.xml',
        'views/voyage_produit.xml',
        'views/Avance.xml',
        'views/gvoyage_report_pointage.xml',
        #'views/movementpay.xml',
        # 'views/trait.xml',
        'views/viecule.xml',
        'views/gvoyage_report_recap.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
