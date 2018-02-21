import logging
import secrets
import string
from urllib.parse import quote

import requests
from flask import jsonify, redirect, request, session, url_for


logger = logging.getLogger(__name__)


class OpenIDConnect:
    def __init__(self, discovery_url):
        logger.debug("OIDC: Discovering configuration")
        self.configuration = requests.get(discovery_url).json()

    def init_app(self, app):
        # Register authentication handler
        @app.route(f"{app.config['SERVICE_URL']}/authenticate/oidc")
        def authenticate():
            if not app.config['FEAT_TOGGLE_OIDC']:
                response = jsonify({'error': "OpenID Connect authentication is "
                                             "disabled"})
                response.status_code = 501
                return response

            base = self.configuration['authorization_endpoint']

            args = {
                'client_id': app.config['OIDC_CLIENT_ID'],
                'response_type': 'code',
                'scope': 'openid email',
                'redirect_uri': (f"{app.config['OIDC_REDIRECT_BASE']}"
                                 f"{url_for('return_')}"),
                'state': self.create_random_token(),
                'nonce': self.create_random_token(),
            }

            # Store state
            session['state'] = args['state']

            query_params = '&'.join({
                f"{quote(key)}={quote(val)}" for key, val in args.items()})
            return redirect(f"{base}?{query_params}")

        # Register return handler
        @app.route(f"{app.config['SERVICE_URL']}/authenticate/oidc/return")
        def return_():
            if not app.config['FEAT_TOGGLE_OIDC']:
                response = jsonify({'error': "OpenID Connect authentication is "
                                             "disabled"})
                response.status_code = 501
                return response

            if request.args['state'] != session['state']:
                response = jsonify({'error': "Invalid state"})
                response.status_code = 401
                return response

            # Exchange code for access token and id token
            r = requests.post(self.configuration['token_endpoint'], data={
                'code': request.args['code'],
                'client_id': app.config['OIDC_CLIENT_ID'],
                'client_secret': app.config['OIDC_CLIENT_SECRET'],
                'redirect_uri': (f"{app.config['OIDC_REDIRECT_BASE']}"
                                 f"{url_for('return_')}"),
                'grant_type': 'authorization_code',
            })
            r.raise_for_status()
            return jsonify(r.json())

    @staticmethod
    def create_random_token(n=12):
        chars = string.ascii_letters + string.digits
        return ''.join([secrets.choice(chars) for _ in range(n)])
