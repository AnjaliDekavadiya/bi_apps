# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Amazon S3 Cloud Storage",
  "summary"              :  """Store your Odoo attachment to Amazon S3 cloud Storage""",
  "category"             :  "Website",
  "version"              :  "1.2.6",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Amazon-S3-Cloud-Storage.html",
  "description"          :  """Store your Odoo attachment to Amazon S3 Cloud Storage
  amazon s3 storage
  amazon s3 bucket storage
  amazon cloud storage
  Store odoo attachments on amazon s3 storage
  sync odoo attachments on amazon s3 bucket
  """,
  "depends"              :  [
                             'base_setup',
                             'web_tour',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/default_data.xml',
                             'views/base_config_view.xml',
                            ],
  "images"               :  ['static/description/banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  149,
  "currency"             :  "USD",
  "external_dependencies":  {'python': ['boto3', 'botocore']},
}