from drf_spectacular.openapi import OpenApiAuthenticationExtension
from rest_framework_simplejwt.tokens import RefreshToken

class JWTAuthExtension(OpenApiAuthenticationExtension):
    target_class = 'rest_framework_simplejwt.authentication.JWTAuthentication'
    name = 'JWT'
    
    def __init__(self, view):
        super().__init__(view)
        self.type = 'apiKey'
        self.in_ = 'header'
        self.name = 'Authorization'
    
    def get_security_definition(self):
        return {
            'type': self.type,
            'in': self.in_,
            'name': self.name,
            'description': 'JWT Bearer token'
        }

