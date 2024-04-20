from typing import Callable, List, Union
from PyQt6.uic import load_ui
from PyQt6.QtWidgets import QFrame
from constants.common import CREATE_KEY_SPACE_WINDOW_PATH, ErrorTitles
from constants.utils import pop_up_error
from constants.common import ErrorTitles, ReplicationClass
from backend.create_key_space_window.add_datacenter_frame import AddDatacenterFrame
from backend.main_window.cassandra_manager import CassandraManager
from constants.create_key_space_model import CreateKeySpaceModel
from constants.datacenter_model import DatacenterModel


class CreateKeySpaceWindow(QFrame):
    def __init__(self: 'CreateKeySpaceWindow',
                 cassandra_manager: CassandraManager,
                 refresh_connection_tree_model: Callable[[], None]) -> None:
        super(CreateKeySpaceWindow, self).__init__()
        load_ui.loadUi(CREATE_KEY_SPACE_WINDOW_PATH, self)
        self.cassandra_manager: CassandraManager = cassandra_manager
        self.refresh_connection_tree_model = refresh_connection_tree_model
        self.datacenter_frames: List[AddDatacenterFrame] = []

        self.add_datacenter_button.clicked.connect(self.add_datacenter_frame)
        self.submit_button.clicked.connect(self.create_key_space)

        self.replication_class_combo_box.currentIndexChanged.connect(self.show_datacenter_replication_columns)
        self.show_datacenter_replication_columns()


    def show_datacenter_replication_columns(self: 'CreateKeySpaceWindow') -> None:
        selected_option = self.replication_class_combo_box.currentText()

        match selected_option:
            case ReplicationClass.SimpleStrategy.value:
                self.datacenter_scroll_area.hide()
                self.setGeometry(0, 0, 633, 275)
            case ReplicationClass.NetworkTopologyStrategy.value:
                self.datacenter_scroll_area.show()
                self.setGeometry(0, 0, 633, 400)

    def add_datacenter_frame(self: 'CreateKeySpaceWindow') -> None:
        datacenter_frame = AddDatacenterFrame()
        datacenter_frame.remove_button.clicked.connect(lambda: self.remove_datacenter(datacenter_frame))
        self.datacenter_frames.append(datacenter_frame)
        self.scroll_area_vlayout.addWidget(datacenter_frame)

    def remove_datacenter(self: 'CreateKeySpaceWindow', datacenter_frame: AddDatacenterFrame) -> None:
        self.datacenter_frames.remove(datacenter_frame)
        datacenter_frame.deleteLater()

    def create_key_space(self: 'CreateKeySpaceWindow') -> None:
        data = self.get_data_to_create_key_space()

        if data is None:
            return

        is_success = self.cassandra_manager.create_key_space(data)
        if is_success:
            self.close()
            self.refresh_connection_tree_model()

    def get_data_to_create_key_space(self: 'CreateKeySpaceWindow') -> Union[CreateKeySpaceModel, None]:
        datacenters: List[DatacenterModel] = []

        if self.is_key_space_name_empty():
            pop_up_error(ErrorTitles.Error.value, f"Keyspace name must not be empty.")
            return

        for datacenter_frame in self.datacenter_frames:
            model = datacenter_frame.get_datacenter_model()
            if self.is_datacenter_name_empty(model.name):
                pop_up_error(ErrorTitles.Error.value, f"Datacenter name must not be empty.")
                return
            datacenters.append(model)

        return CreateKeySpaceModel(self.key_space_name_line_edit.text(),
                                   self.replication_class_combo_box.currentText(),
                                   self.replication_factor_spin_box.value(),
                                   self.durable_writes_check_box.isChecked(),
                                   datacenters)

    def is_key_space_name_empty(self: 'CreateKeySpaceWindow') -> bool:
        return self.key_space_name_line_edit.text() == ""

    def is_datacenter_name_empty(self: 'CreateKeySpaceWindow', datacenter_name: str) -> bool:
        return datacenter_name == ""