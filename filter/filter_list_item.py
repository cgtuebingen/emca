from filter.filter_type import FilterType
from PySide2.QtWidgets import QFormLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QWidget


class FilterListItem(QWidget):

    """
        FilterListItem
        Represents a filter list item holding information about the filter
    """

    def __init__(self, filter_settings):
        QWidget.__init__(self)

        self._idx = filter_settings.get_idx()

        layout = QFormLayout()
        d_type = filter_settings.get_type()
        constraint = filter_settings.get_constraint()
        text = filter_settings.get_text()

        if d_type is FilterType.SCALAR:
            layout.addRow("Scalar:", QLabel(text))
            layout.addRow("val: ", QLabel(str(constraint[0])))
        elif d_type is FilterType.POINT2:
            layout.addRow("Point2:", QLabel(""))
            layout.addRow("x: ", QLabel(str(constraint[0])))
            layout.addRow("y: ", QLabel(str(constraint[1])))
        elif d_type is FilterType.POINT3:
            layout.addRow("Point3:", QLabel(text))
            layout.addRow("x: ", QLabel(str(constraint[0])))
            layout.addRow("y: ", QLabel(str(constraint[1])))
            layout.addRow("z: ", QLabel(str(constraint[2])))
        elif d_type is FilterType.COLOR3:
            layout.addRow("Color3:", QLabel(text))
            layout.addRow("r: ", QLabel(str(constraint[0])))
            layout.addRow("g: ", QLabel(str(constraint[1])))
            layout.addRow("b: ", QLabel(str(constraint[2])))
        self.setLayout(layout)

    def get_idx(self):
        """
        Returns an index referencing the filter settings index
        :return: integer
        """
        return self._idx
