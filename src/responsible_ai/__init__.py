"""
Infosys Responsible AI Toolkit Integration for Potato Shield

Official Toolkit: https://github.com/Infosys/Infosys-Responsible-AI-Toolkit

This module provides Python clients to interact with RAI Toolkit APIs.
NO custom implementations - only official toolkit integration.

UK-India AIxcelerate 2025-26 Compliance
"""

from .rai_client import get_rai_client, RAIToolkitClient
from .rai_middleware import get_rai_middleware, RAIMiddleware

__all__ = [
    'get_rai_client',
    'RAIToolkitClient',
    'get_rai_middleware',
    'RAIMiddleware'
]

__version__ = '1.0.0'
__rai_toolkit_version__ = '2.2.0'
