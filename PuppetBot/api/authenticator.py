from abc import ABCMeta
from base import BaseClass
from warrant.aws_srp import AWSSRP
import boto3
import time 


class Authenticator(BaseClass):
    __metadata__ = ABCMeta

    def __init__(self, ctx, refresh_interval=30):
        super(Authenticator, self).__init__(ctx)
        self._logger.info('Using {} for authentication'.format(self.__class__.__name__))
        self._refresh_interval = refresh_interval
        self.last_update_timestamp = 0 
        self.session = None 
        self._clients = {}

    def _time_for_refresh(self):
        if ( (time.time() - self.last_update_timestamp) >= self._refresh_interval):

            self.last_update_timestamp = time.time()  
            return True

    def get_client(self, client_type):
        # client should have a refresh method 
        client = self.session.client(client_type)
        self._clients[client_type] = client
        return client

    def refresh_clients(self):
        for client_type in self._clients:
            self._clients[client_type] = self.session.client(client_type)

    def refresh(self):
        if self._time_for_refresh():    
            self.refresh_logic()
            self._logger.info('Authenticator refresh successful')
            self.refresh_clients()
            
                

    def refresh_logic(self):
        raise NotImplementedError


class CognitoAuthenticator(Authenticator):

    def __init__(self, ctx):
        """
            Args :
                config : 
                    {
                        'username': ,
                        'password': ,
                        'cognito_pool_id': ,
                        'client_id': ,
                        'region_name': ,
                        'identity_pool_id': ,
                        'refresh_interval':  
                    }
        """
        super(CognitoAuthenticator, self).__init__(ctx)
        self._pool_full_name = 'cognito-idp.{}.amazonaws.com/{}'.format(
                                        self._cognito_pool_id.split('_')[0], self._cognito_pool_id)
        self._cognito_identity_client = boto3.client('cognito-identity',region_name=self._region_name)
        self._identity_id = self._get_cognito_identity_id()
        self.refresh()

    def _get_auth_token(self):
        aws = AWSSRP(username=self._username,
                    password=self._password,
                    pool_id=self._cognito_pool_id,
                    client_id=self._client_id,
                    pool_region=self._region_name)

        token = aws.authenticate_user()
        return token['AuthenticationResult']['IdToken']

    def _get_cognito_identity_id(self):
        auth_token = self._get_auth_token()
        response = self._cognito_identity_client.get_id(
                                            IdentityPoolId=self._identity_pool_id,
                                            Logins={
                                                self._pool_full_name: auth_token
                                            })
        return response['IdentityId']

    def refresh_logic(self):
        auth_token = self._get_auth_token()    
        response = self._cognito_identity_client.get_credentials_for_identity(
                                            IdentityId=self._identity_id,
                                            Logins={
                                                self._pool_full_name: auth_token
                                            })

        self.credentials = response['Credentials']
        self.session = boto3.Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                                aws_secret_access_key=response['Credentials']['SecretKey'],
                                aws_session_token=response['Credentials']['SessionToken'],
                                region_name=self._region_name)

