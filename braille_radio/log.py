import logging

# Logger konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        # logging.StreamHandler()
    ]
)

# Logger verwenden
logger = logging.getLogger(__name__)
