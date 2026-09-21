# monBridge Payment — Odoo 19 Community

This is a first functional backend scaffold based on the supplied monBridge conception document.

Implemented business models:
- monbridge.company
- monbridge.company.balance
- monbridge.deposit
- monbridge.beneficiary
- monbridge.beneficiary.bank
- monbridge.payment
- monbridge.transaction
- monbridge.fx.quote
- monbridge.ai.extraction

The module reuses Odoo standard models such as res.partner, res.currency and ir.attachment.

## Install
Copy `monbridge_payment` into your Odoo custom addons directory, restart Odoo, update Apps, and install "monBridge Payment".

Example:
./odoo-bin -c odoo.conf -d YOUR_DB -u monbridge_payment --stop-after-init

Then restart Odoo normally.

## Important
This is the core Odoo module, not the complete production integration. Bank/PSP API integration, OCR/AI provider integration, portal UI, accounting journal configuration, reconciliation, KYC/AML controls and production-grade record rules still need to be implemented.
