# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Create Purchase Order',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Create purchase order(s) from sale order, grouped by vendor',
    'description': """
Adds a "Create PO" button on sale orders. Creates one purchase order per vendor
(from product supplier info), with the same lines as the sale order (Method B).
    """,
    'depends': ['sale', 'purchase', 'sale_purchase'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
