import pystac
from pystac.errors import STACValidationError

class StacValidator:
    def __init__(self, url):
        self.url = url
    
    def validate(self):
        try:
            catalog = pystac.Catalog.from_file(self.url)
            catalog.validate()
            return True
        except (ValueError, STACValidationError):
            return False