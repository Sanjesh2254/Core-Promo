// Copyright (c) 2026, core promo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Setting", {
 refresh: function(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button("Create Purchase Invoice", function() {

                frappe.call({
                    method: "core_promo.core_promo.doctype.task_work_log.task_work_log.create_purchase_invoice",
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.msgprint("Purchase Invoice Created: " + r.message);
                        }
                    }
                });

            }, "Create");

        }

    }
});
