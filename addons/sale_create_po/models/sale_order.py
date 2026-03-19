# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_purchase_order(self):
        """Create purchase order(s) from this sale order, one PO per vendor (Method B).
        Uses product supplier info to determine vendor; reuses sale_purchase helpers
        for order/line values and links PO lines to SO lines via sale_line_id.
        """
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda l: l.product_id and not l.display_type
        )
        if not lines:
            raise UserError(_("There are no product lines to create a purchase order from."))

        # Map: partner_id -> list of (sale_order_line, supplierinfo)
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
