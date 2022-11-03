from typing import Dict, Any

import logging

from requests import Response
import requests

LOG = logging.getLogger(__name__)


class APIClient:

    session = None

    def __init__(self, base_url: str, ca_cert: str):
        """
        Class representing an API Client
        :param base_url: The API base URL
        :param ca_cert: The verification cert path
        """
        self.base_url = base_url
        self.ca_cert = ca_cert
        self.session = requests.Session()
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
        self.session.verify = self.ca_cert
        self.session.headers.update({'Accept': 'application/json'})

    def get_url(self, path):
        if path.startswith('/'):
            path = path[1:]
        return f'{self.base_url}{path}'

    def set_headers(self, headers: Dict[str, Any]):
        self.session.headers.update(headers)

    def make_request(self, method: str, path: str, params: Dict[str, Any] = None,
                     json: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Response:
        method = method.lower()
        url = self.get_url(path)
        LOG.info(f'{method} {url}')
        kwargs = {'url': url}
        if json:
            LOG.info(f'JSON: {json}')
            kwargs['json'] = json
        if params:
            LOG.info(f'PARAMS: {params}')
            kwargs['params'] = params
        if data:
            LOG.info(f'DATA: {data}')
            kwargs['data'] = data
        LOG.info(self.session.headers)
        request = getattr(self.session, method)

        resp = request(**kwargs)
        LOG.info(f'RESPONSE: {resp.text}')
        return resp

