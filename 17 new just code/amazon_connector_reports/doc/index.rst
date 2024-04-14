Features
============

1. Request and retrieve 109 **Amazon Reports** (Amazon Developer Account is needed) (https://developer-docs.amazon.com/sp-api/docs/report-type-values)
2. Convert Amazon Reports content to Odoo models and store them in the database. Get headers of your files and get views from it. Refresh data if you want. Store different data by date etc.
3. Convert Amazon Reports to Odoo Document Spreadsheet. For example "Restock inventory report" to see how much to restock from your FBM to FBA. Create Dashboards from Amazon and Odoo data from Spreadsheets. Get the full picture of your performance. Build performance measures, pricing rules etc. based on data.
4. Additionally: Processing **Flat File V2 Settlement Report**. Get all your invoices reconciled!
5. Generate Scheduler to automatically request and retrieve Amazon Reports. No need to refresh the data manually or re-generate
   
Instruction
===========

**Instruction video:** `Amazon Report Extension <https://youtu.be/FJXnl4rQmvY>`_

This module provides the core feature of requesting and retrieving Amazon Reports.

**1. Report Categories and Types**

.. image:: amz_report_type_categ.png
   :alt: Amazon Report Category
   :align: center
   :width: 1000
- **Report Category**: Amazon Report Category

.. image:: amz_report_type.png
   :alt: Amazon Report Type
   :align: center
   :width: 1000
- **Report Type**: Amazon Report Type

**2. Request Amazon Reports**

.. image:: create_report_log.png
   :alt: Choose Report to Request
   :align: center
   :width: 1000
- **Creating Report Log**: Choose Report to Request

.. image:: request_reports.png
   :alt: Requesting report
   :align: center
   :width: 1000
- **Requesting report**: User can either request manual generated reports or auto-generated reports (by Amazon).

.. image:: settlement_report_list.png
   :alt: Example of Report List
   :align: center
   :width: 1000
- **Auto Generated Reports**: An example of auto-generated reports (by Amazon).

**3. Operations on Amazon Reports**

.. image:: report_operations.png
   :alt: Operations on Amazon Reports
   :align: center
   :width: 1000
- **Operations on Reports**: User can perform operations on Amazon Reports.

.. image:: report_spreadsheet.png
   :alt: Report Odoo Spreadsheet
   :align: center
   :width: 1000
- **Report Odoo Spreadsheet**: User can convert Amazon Reports to Odoo Spreadsheet.

.. image:: generated_report_lines2.png
   :alt: Report Odoo Database Record Lines
   :align: center
   :width: 1000
- **Report Odoo Database Record Lines**: User can generate Odoo records for report's content (*see 4. for configuration of Odoo models*).

**4. Operations on Amazon Report Type**

.. image:: generate_crons.png
   :alt: Generate Scheduler
   :align: center
   :width: 1000

.. image:: scheduler_result.png
   :alt: Requesting report
   :align: center
   :width: 1000
- **Generate Scheduler**: Choose Marketplace and Processing Type to generate scheduler.

.. image:: generate_odoo_models.png
   :alt: Generate Odoo Models
   :align: center
   :width: 1000
- **Generate Odoo Models**: Will create Odoo models for and fields the this report type (needs at least one requested report in system)

.. image:: choose_fields.png
   :alt: Choose Column to create Fields
   :align: center
   :width: 1000
- **Choose Report Columns to create Fields**: This will define the fields for Report Lines (see *3. Report Odoo Database Record Lines*).
