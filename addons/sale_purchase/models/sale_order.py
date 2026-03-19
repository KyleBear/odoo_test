# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_count = fields.Integer(
        "Number of Purchase Order Generated",
        compute='_compute_purchase_order_count',
        groups='purchase.group_purchase_user')

    @api.depends('order_line.purchase_line_ids.order_id')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order._get_purchase_orders())

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self:
            order.order_line.sudo()._purchase_service_generation()
        return result

    def _action_cancel(self):
        result = super()._action_cancel()
        # When a sale person cancel a SO, he might not have the rights to write
        # on PO. But we need the system to create an activity on the PO (so 'write'
        # access), hence the `sudo`.
        self.sudo()._activity_cancel_on_purchase()
        return result

    def action_view_purchase_orders(self):
        self.ensure_one()
        purchase_order_ids = self._get_purchase_orders().ids
        action = {
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
        if len(purchase_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': purchase_order_ids[0],
            })
        else:
            action.update({
                'name': _("Purchase Order generated from %s", self.name),
                'domain': [('id', 'in', purchase_order_ids)],
                'view_mode': 'list,form',
            })
        return action

    def _get_purchase_orders(self):
        return self.order_line.purchase_line_ids.order_id

    def action_create_purchase_order(self):
        """Create purchase order(s) from this sale order, one PO per vendor (Method B)."""
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda l: l.product_id and not l.display_type
        )
        if not lines:
            raise UserError(_("There are no product lines to create a purchase order from."))

        partner_lines_map = defaultdict(list)
        for line in lines:
            line = line.with_company(line.company_id)
            supplierinfo = line.product_id._select_seller(
                partner_id=False,
                quantity=line.product_uom_qty,
                date=self.date_order and self.date_order.date() if self.date_order else None,
                uom_id=line.product_uom_id,
            )
            if not supplierinfo:
                raise UserError(
                    _("There is no vendor associated to the product %s. Please define a vendor for this product.",
                      line.product_id.display_name)
                )
            partner_lines_map[supplierinfo.partner_id].append((line, supplierinfo))

        PurchaseOrder = self.env['purchase.order'].sudo()
        PurchaseOrderLine = self.env['purchase.order.line'].sudo()
        created_orders = self.env['purchase.order']
        for partner, line_supplier_list in partner_lines_map.items():
            first_line, first_supplierinfo = line_supplier_list[0]
            order_vals = first_line._purchase_service_prepare_order_values(first_supplierinfo)
            purchase_order = PurchaseOrder.with_context(
                mail_create_nosubscribe=True
            ).create(order_vals)
            created_orders |= purchase_order
            for line, _supplierinfo in line_supplier_list:
                line_vals = line._purchase_service_prepare_line_values(purchase_order)
                PurchaseOrderLine.create(line_vals)

        return self.action_view_purchase_orders()

    def _activity_cancel_on_purchase(self):
        """ If some SO are cancelled, we need to put an activity on their generated purchase. If sale lines of
            different sale orders impact different purchase, we only want one activity to be attached.
        """
        purchase_to_notify_map = {}  # map PO -> recordset of SOL as {purchase.order: set(sale.orde.liner)}

        purchase_order_lines = self.env['purchase.order.line'].search([
            ('sale_line_id', 'in', self.mapped('order_line').ids),
            ('state', '!=', 'cancel'),
            ('product_id.service_to_purchase', '=', True),
        ])
        for purchase_line in purchase_order_lines:
            purchase_to_notify_map.setdefault(purchase_line.order_id, self.env['sale.order.line'])
            purchase_to_notify_map[purchase_line.order_id] |= purchase_line.sale_line_id

        for purchase_order, sale_order_lines in purchase_to_notify_map.items():
            purchase_order._activity_schedule_with_view('mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid='sale_purchase.exception_purchase_on_sale_cancellation',
                render_context={
                    'sale_orders': sale_order_lines.mapped('order_id'),
                    'sale_order_lines': sale_order_lines,
            })
