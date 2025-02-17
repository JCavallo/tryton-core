===============================
Analytic Invoice Defer Scenario
===============================

Imports::

    >>> import datetime as dt
    >>> from decimal import Decimal

    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import (
    ...     create_company, get_company)
    >>> from trytond.modules.account.tests.tools import (
    ...     create_fiscalyear, create_chart, get_accounts)
    >>> from trytond.modules.account_invoice.tests.tools import (
    ...     set_fiscalyear_invoice_sequences)
    >>> from trytond.modules.account_invoice_defer.tests.tools import (
    ...     add_deferred_accounts)

    >>> today = dt.date.today()

Activate modules::

    >>> config = activate_modules(['analytic_invoice', 'account_invoice_defer'])

    >>> AnalyticAccount = Model.get('analytic_account.account')
    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceDeferred = Model.get('account.invoice.deferred')
    >>> Party = Model.get('party.party')
    >>> ProductCategory = Model.get('product.category')
    >>> ProductUom = Model.get('product.uom')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company, today))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = add_deferred_accounts(get_accounts(company))

Create analytic accounts::

    >>> root = AnalyticAccount(type='root', name='Root')
    >>> root.save()
    >>> analytic_account = AnalyticAccount(
    ...     root=root, parent=root, name="Analytic")
    >>> analytic_account.save()

Create party::

    >>> party = Party(name="Insurer")
    >>> party.save()

Create account category::

    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = accounts['expense']
    >>> account_category.account_revenue = accounts['revenue']
    >>> account_category.save()

Create product::

    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> template = ProductTemplate()
    >>> template.name = "Insurance"
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('1000')
    >>> template.account_category = account_category
    >>> template.save()
    >>> product, = template.products

Create invoice::

    >>> invoice = Invoice(type='in')
    >>> invoice.party = party
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 1
    >>> line.unit_price = Decimal('1000')
    >>> line.defer_from = period.start_date
    >>> line.defer_to = line.defer_from + dt.timedelta(days=499)
    >>> entry, = line.analytic_accounts
    >>> entry.account = analytic_account
    >>> invoice.invoice_date = today
    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> invoice_line, = invoice.lines

    >>> analytic_account.reload()
    >>> analytic_account.debit, analytic_account.credit
    (Decimal('1000.00'), Decimal('0.00'))

Check invoice deferred and run it::

    >>> deferral, = InvoiceDeferred.find([])
    >>> deferral.invoice_line == invoice_line
    True
    >>> deferral.amount
    Decimal('1000.00')
    >>> deferral.start_date == invoice_line.defer_from
    True
    >>> deferral.end_date == invoice_line.defer_to
    True
    >>> deferral.click('run')
    >>> deferral.state
    'running'
    >>> len(deferral.moves)
    13

    >>> analytic_account.reload()
    >>> analytic_account.debit in {Decimal('1730'), Decimal('1732')}
    True
    >>> analytic_account.credit
    Decimal('1000.00')
