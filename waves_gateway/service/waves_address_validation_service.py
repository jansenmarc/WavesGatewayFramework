"""
WavesAddressValidationService
"""

from doc_inherit import class_doc_inherit

from waves_gateway.common import Injectable
from .address_validation_service import AddressValidationService

import pywaves


@Injectable()
@class_doc_inherit
class WavesAddressValidationService(AddressValidationService):
    """inherit"""

    def validate_address(self, address: str) -> bool:
        try:
            pywaves.Address(address=address)
            return True
        except ValueError:
            return False
