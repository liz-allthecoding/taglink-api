from unittest import TestCase
from typing import Dict, Any, Optional, List
from enum import Enum

import os
import yaml
import logging

from integration_tests.api_client import APIClient

LOG = logging.getLogger(__name__)

with open("integration_tests/test.yaml") as test:
    config = yaml.safe_load(test.read())

TEST_ENV = os.environ['TEST_ENV']
BASE_URL = config.get('base_urls').get(TEST_ENV)
CA_CERT = config.get('ca_certs').get(TEST_ENV)
USERNAME = config.get('username').get(TEST_ENV)
PASSWORD = config.get('password').get(TEST_ENV)
ACCOUNT_EMAIL_1 = config.get('account_email_1').get(TEST_ENV)
ACCOUNT_EMAIL_2 = config.get('account_email_2').get(TEST_ENV)
ACCOUNT_PASSWORD = config.get('account_password').get(TEST_ENV)


class ContentType(str, Enum):
    JSON = 'application/json'
    X_WWW_FORM_URL_ENCODED = 'application/x-www-form-urlencoded'


class IntegrationTestsBase(TestCase):
    __test__ = False

    accounts = {}
    admin_token = None
    links = {}
    tags = {}

    def setUp(self):
        self.api_client = APIClient(base_url=BASE_URL, ca_cert=CA_CERT)
        self.username = USERNAME
        self.password = PASSWORD
        self.account_emails = [ACCOUNT_EMAIL_1, ACCOUNT_EMAIL_2]
        self.account_password = ACCOUNT_PASSWORD

    def store_link(self, link: Dict[str, Any], account_email: str) -> None:
        if self.links.get(account_email) is None:
            self.links[account_email] = []
        self.links[account_email].append(link)

    def store_tag(self, tag: Dict[str, Any], account_email: str) -> None:
        if self.tags.get(account_email) is None:
            self.tags[account_email] = []
        self.tags[account_email].append(tag)

    def set_api_headers(self, content_type: str = ContentType.JSON, token: Optional[str] = None) -> None:
        if content_type == ContentType.X_WWW_FORM_URL_ENCODED:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        else:
            headers = {'Accept': 'application/json',
                       'Content-Type': 'application/json'}

        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            headers['Authorization'] = None

        self.api_client.set_headers(headers)

    def get_admin_token(self) -> str:
        data = {
            'username': self.username,
            'password': self.password,
            'scope': 'admin',
            'grant_type': '',
            'client_id': '',
            'client_secret': ''
        }
        resp = self.api_client.make_request('post', 'token', data=data)
        self.assertEqual(200, resp.status_code)

        token = resp.json()

        self.assertIsNotNone(token['access_token'])
        self.assertIsNotNone(token['token_type'])
        self.assertIsNotNone(token['expires'])
        self.admin_token = token['access_token']

        return self.admin_token

    def get_account_token(self, account_id: str) -> str:
        account = self.get_account(account_id, token=self.admin_token)
        LOG.info(account)
        self.set_api_headers(content_type=ContentType.X_WWW_FORM_URL_ENCODED)
        data = {
            'username': account['email'],
            'password': self.account_password,
            'scope': 'account',
            'grant_type': '',
            'client_id': '',
            'client_secret': ''
        }
        LOG.info(data)
        resp = self.api_client.make_request('post', 'token', data=data)
        self.assertEqual(200, resp.status_code)
        token = resp.json()

        self.assertIsNotNone(token['access_token'])
        self.assertIsNotNone(token['token_type'])
        self.assertIsNotNone(token['expires'])
        account_token = token['access_token']

        return account_token

    def create_account(self, email: str) -> None:
        self.set_api_headers(content_type=ContentType.JSON, token=self.admin_token)
        json = {
            'email': email,
            'password': self.account_password
        }

        resp = self.api_client.make_request('post', 'account', json=json)
        self.assertEqual(200, resp.status_code)
        account = resp.json()

        self.assertIsNotNone(account['account_id'])
        self.assertIsNotNone(account['email'])
        self.assertIsNotNone(account['hashed_password'])

        self.accounts[email] = account

    def get_account(self, account_id: str, token: str) -> Dict[str, Any]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        resp = self.api_client.make_request('get', f'account/{account_id}')
        self.assertEqual(200, resp.status_code)
        account = resp.json()

        return account

    def get_accounts(self, token: str, email: Optional[str] = None) -> List[Dict[str, Any]]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        params = {}
        if email is not None:
            params['email'] = email
        resp = self.api_client.make_request('get', 'account', params=params)
        self.assertEqual(200, resp.status_code)
        accounts = resp.json()
        return accounts

    def delete_account(self, account_id: str, token: str) -> None:
        self.set_api_headers(content_type=ContentType.JSON, token=token)

        resp = self.api_client.make_request('delete', f'account/{account_id}')
        resp_json = resp.json()
        self.assertEqual(resp_json, "OK")

    def delete_accounts(self) -> None:
        accounts = self.get_accounts(token=self.admin_token)
        for account in accounts:
            if account['email'] in self.account_emails:
                self.delete_account(account['account_id'], token=self.admin_token)

    def create_link(self, link: str, token: str, tag: str = None, tag_id: str = None,
                    account_id: str = None) -> Dict[str, Any]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        json = {
            'link': link,
        }

        if account_id is not None:
            json['account_id'] = account_id

        if tag is not None:
            json['tag'] = tag

        if tag_id is not None:
            json['tag_id'] = tag_id

        resp = self.api_client.make_request('post', 'link', json=json)
        self.assertEqual(200, resp.status_code)
        link = resp.json()
        return link

    def get_link(self, link_id: str, token: str) -> Dict[str, Any]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        resp = self.api_client.make_request('get', f'link/{link_id}')
        self.assertEqual(200, resp.status_code)
        link = resp.json()
        return link

    def get_links(self, token: str, tag: str = None, tag_id: str = None,
                  account_id: str = None) -> List[Dict[str, Any]]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        params = {}
        if tag is not None:
            params['tag'] = tag
        if tag_id is not None:
            params['tag_id'] = tag_id
        if account_id is not None:
            params['account_id'] = account_id
        resp = self.api_client.make_request('get', 'link', params=params)
        self.assertEqual(200, resp.status_code)
        links = resp.json()
        return links

    def delete_link(self, link_id: str, token: str) -> None:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        resp = self.api_client.make_request('delete', f'link/{link_id}')
        self.assertEqual(200, resp.status_code)

    def get_tags(self, token: str, tag: str = None, account_id: str = None) -> List[Dict[str, Any]]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        params = {}
        if tag is not None:
            params['tag'] = tag
        if account_id is not None:
            params['account_id'] = account_id
        resp = self.api_client.make_request('get', 'tag', params=params)
        self.assertEqual(200, resp.status_code)
        tags = resp.json()
        return tags

    def create_tag(self, tag: str, token: str, account_id: str = None) -> Dict[str, Any]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        json = {
            'tag': tag,
        }

        if account_id is not None:
            json['account_id'] = account_id

        resp = self.api_client.make_request('post', 'tag', json=json)
        self.assertEqual(200, resp.status_code)
        tag = resp.json()
        return tag

    def get_tag(self, tag_id: str, token: str) -> Dict[str, Any]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        resp = self.api_client.make_request('get', f'tag/{tag_id}')
        self.assertEqual(200, resp.status_code)
        tag = resp.json()
        return tag

    def delete_tag(self, tag_id: str, token: str) -> None:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        resp = self.api_client.make_request('delete', f'tag/{tag_id}')
        self.assertEqual(200, resp.status_code)

    def create_taglink(self, tag_id: str, link_id: str, token: str, account_id: str = None) -> Dict[str, Any]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        json = {
            'tag_id': tag_id,
            'link_id': link_id
        }

        if account_id is not None:
            json['account_id'] = account_id

        resp = self.api_client.make_request('post', 'taglink', json=json)
        self.assertEqual(200, resp.status_code)
        taglink = resp.json()
        return taglink

    def get_taglinks(self, token: str, tag_id: str = None, link_id: str = None,
                     account_id: str = None) -> List[Dict[str, Any]]:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        params = {}
        if tag_id is not None:
            params['tag_id'] = tag_id
        if link_id is not None:
            params['link_id'] = link_id
        if account_id is not None:
            params['account_id'] = account_id
        resp = self.api_client.make_request('get', f'taglink', params=params)
        self.assertEqual(200, resp.status_code)
        taglinks = resp.json()
        return taglinks

    def delete_taglinks(self, token: str, tag_id: str = None, link_id: str = None) -> None:
        self.set_api_headers(content_type=ContentType.JSON, token=token)
        params = {}
        if tag_id is not None:
            params['tag_id'] = tag_id
        if link_id is not None:
            params['link_id'] = link_id
        resp = self.api_client.make_request('delete', f'taglink', params=params)
        self.assertEqual(200, resp.status_code)



