from PySide6.QtWidgets import QLabel, QVBoxLayout
from .base_view import BaseView

class SamplesView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SamplesView")
    
    def setup_ui(self):
        label = QLabel("Samples View")
        label.setStyleSheet("font-size: 24px;")
        self.main_layout.addWidget(label)
        self.main_layout.addStretch()
