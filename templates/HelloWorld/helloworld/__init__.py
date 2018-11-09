from .controllers import (
    include_hello,
)
from .exception_handler import includeme as include_exception_handler


def includeme():
    include_hello()
    include_exception_handler()
