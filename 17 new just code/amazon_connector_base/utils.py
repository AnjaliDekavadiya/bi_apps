import json
import requests
import logging


from odoo.addons.sale_amazon import utils


def submit_feed(account, feed, feed_type, marketplace_ids=[], feed_options=''):
    """ Submit the provided feed to the SP-API.

    :param recordset account: The Amazon account on behalf of which the feed should be submitted, as
                              an `amazon.account` record.
    :param str feed: The XML feed to submit.
    :param str feed_type: The type of the feed to submit. E.g., 'POST_ORDER_ACKNOWLEDGEMENT_DATA'.
    :return: The feed id returned by the SP-API.
    :rtype: str
    """
    def _create_feed_document():
        """ Create a feed document.

        :return: The feed document id and the pre-signed URL to upload the feed to.
        :rtype: tuple[str, str]
        """
        _payload = {'contentType': feed_content_type}
        _response_content = utils.make_sp_api_request(
            account, 'createFeedDocument', payload=_payload, method='POST'
        )
        return _response_content['feedDocumentId'], _response_content['url']

    def _upload_feed_data():
        """ Upload the XML feed to the URL returned by Amazon.

        :return: None
        """
        headers = {'content-Type': feed_content_type}
        try:
            response = requests.put(upload_url, data=feed, headers=headers, timeout=60)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                _logger.exception("Invalid API request with data:\n%s", feed)
                raise ValidationError(_("The communication with the API failed."))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Could not establish the connection to the feed URL.")
            raise ValidationError(_("Could not establish the connection to the feed URL."))

    def _create_feed():
        """ Create the feed and return its id.

        :return: The feed id.
        :rtype: str
        """
        if marketplace_ids:
            _marketplace_api_refs = marketplace_ids
        else:
            _marketplace_api_refs = account.active_marketplace_ids.mapped('api_ref')
        _payload = {
            'feedType': feed_type,
            'marketplaceIds': _marketplace_api_refs,
            'inputFeedDocumentId': feed_document_id,
        }
        if feed_options:
            _payload['feedOptions'] = json.loads(feed_options)
        _response_content = utils.make_sp_api_request(
            account, 'createFeed', payload=_payload, method='POST'
        )
        return _response_content['feedId']

    feed_content_type = 'text/xml; charset=UTF-8'
    feed_document_id, upload_url = _create_feed_document()
    _upload_feed_data()
    feed_id = _create_feed()
    return feed_id


utils.submit_feed = submit_feed


def create_report(
        account, report_type,
        start_date=False, end_date=False,
        marketplace_ids=[]
    ):
    """ Requesting of Report Type (from Start => End) to the SP-API.

    :param recordset account: The Amazon account on behalf of which the feed should be submitted, as
                              an `amazon.account` record.
    :param str report_type: The type of the feed to submit. E.g., 'GET_MERCHANT_LISTINGS_ALL_DATA'.
    :return: The report id returned by the SP-API.
    :rtype: str
    """

    if marketplace_ids:
        _marketplace_api_refs = marketplace_ids
    else:
        _marketplace_api_refs = account.active_marketplace_ids.mapped('api_ref')
    _payload = {
        'reportType': report_type,
        'marketplaceIds': _marketplace_api_refs,
    }
    if start_date:
        _payload["dataStartTime"] = start_date
    if end_date:
        _payload["dataEndTime"] = end_date
    _response_content = utils.make_sp_api_request(
        account, 'createReport', payload=_payload, method='POST'
    )
    logging.info(_response_content)
    return _response_content["reportId"]


def get_report(account, report_id):
    _response_content = utils.make_sp_api_request(
        account, operation='getReport', path_parameter=report_id
    )
    return _response_content


def get_report_document(account, report_document_id):
    _response_content = utils.make_sp_api_request(
        account, operation='getReportDocument',
        path_parameter=report_document_id
    )
    return _response_content

utils.create_report = create_report
utils.get_report = get_report
utils.get_report_document = get_report_document
