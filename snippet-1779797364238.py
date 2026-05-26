# file: dark_web_agent.py
import socks
import socket
from stem import signal
from stem.control import controller

def get_tor_session():
    """creates a session that routes through the tor network."""
    session = requests.session()
    session.proxies = {
        'http':  'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return session

def renew_tor_identity():
    """gets