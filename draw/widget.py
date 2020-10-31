from dataclasses import dataclass
from typing import Any, Union

from dekespo_ai_sdk.core.dimensions import Dim2D


@dataclass
class GridData:
    index: Dim2D = Dim2D(0, 0)
    span_size: Dim2D = Dim2D(1, 1)
    sticky: str = "nsew"


@dataclass
class PackData:
    side: str = "left"
    fill: str = "both"
    expand: bool = True


@dataclass
class WidgetData:
    text: str


@dataclass
class _WidgetDataDefaults:
    id_: int = -1
    grid_data: Union[GridData, None] = None
    pack_data: Union[PackData, None] = None


@dataclass
class _ButtonDataBase:
    callback_function: Any
    parameters: Any


@dataclass
class _TextDataBase:
    number_of_characters: int
    number_of_lines: int


@dataclass
class _ScaleDataBase:
    callback_function: Any
    parameters: Any
    from_: int
    to: int
    orientation: str


@dataclass
class ButtonData(_WidgetDataDefaults, _ButtonDataBase, WidgetData):
    pass


@dataclass
class TextData(_WidgetDataDefaults, _TextDataBase, WidgetData):
    pass


@dataclass
class LabelData(_WidgetDataDefaults, WidgetData):
    pass


@dataclass
class ScaleData(_WidgetDataDefaults, _ScaleDataBase, WidgetData):
    pass
