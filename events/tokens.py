# Optionally kept for clarity; we'll use Django's default_token_generator in views and signals
from django.contrib.auth.tokens import default_token_generator

token_generator = default_token_generator