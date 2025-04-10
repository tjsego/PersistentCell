from simservice.managers import ServiceManagerLocal
from simservice.service_wraps import TypeProcessWrap
from simservice.service_factory import process_factory
from PersistentCellService import PersistentCellService

SERVICE_NAME = "PersistentCellService"


class PersistentCellServiceWrap(TypeProcessWrap):
    _process_cls = PersistentCellService


ServiceManagerLocal.register_service(SERVICE_NAME, PersistentCellServiceWrap)


def persistent_cell_simservice(*args, **kwargs):
    return process_factory(SERVICE_NAME, *args, **kwargs)
