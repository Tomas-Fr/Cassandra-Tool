from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import DATACENTER_REPLICATION_FRAME_PATH
from constants.datacenter_model import DatacenterModel


class AddDatacenterFrame(QFrame):
    def __init__(self: 'AddDatacenterFrame') -> None:
        super(AddDatacenterFrame, self).__init__()
        load_ui.loadUi(DATACENTER_REPLICATION_FRAME_PATH, self)

    def get_datacenter_model(self: 'AddDatacenterFrame') -> DatacenterModel:
        return DatacenterModel(
            name = self.datacenter_name_line_edit.text(),
            replication_factor = self.replication_factor_spin_box.value()
        )
