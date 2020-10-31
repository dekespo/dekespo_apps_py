import tkinter as tk
from typing import Any, Dict

from dekespo_ai_sdk.core.dimensions import Dim2D
from dekespo_ai_sdk.core.utils import error_print

from draw.widget import ButtonData, PackData, TextData, LabelData, WidgetData, ScaleData
from draw.colour import Colour

# TODO: Should not use singleton but inherit an abstract class with fundamental methods
# TODO: Singleton should have been in a different structure hence disabled mypy
# mypy: ignore-errors
class TkinterSingleton:
    root = None
    canvas = None

    grid_frames: Dict[Dim2D, tk.Frame] = {}
    canvas_rectangles: Dict[Dim2D, Any] = {}
    widgets: Dict[int, Any] = {}

    @staticmethod
    def start(title, resizeable=(False, False)):
        if TkinterSingleton.root is None:
            TkinterSingleton.root = tk.Tk()
            TkinterSingleton.root.title(title)
            TkinterSingleton.root.resizable(width=resizeable[0], height=resizeable[1])
        else:
            error_print("Tk root is already initialised")

    @staticmethod
    def set_geometry(size: Dim2D):
        TkinterSingleton.root.geometry(f"{size.x}x{size.y}")

    @staticmethod
    def create_canvas(size=Dim2D(1, 1)):
        if TkinterSingleton.canvas is None:
            TkinterSingleton.canvas = tk.Canvas(TkinterSingleton.root)
            TkinterSingleton.resize_canvas(size)
        else:
            error_print("Canvas is already created")

    @staticmethod
    def resize_canvas(size: Dim2D):
        if TkinterSingleton.canvas is None:
            error_print("It should create canvas first")
        else:
            TkinterSingleton.canvas.configure(width=size.x, height=size.y)

    @staticmethod
    def set_weight_of_grid_element(element, grid_index: Dim2D, weight=1):
        element.rowconfigure(grid_index.y, weight=weight)
        element.columnconfigure(grid_index.x, weight=weight)

    @staticmethod
    def create_frame_with_grid(grid_index: Dim2D, frame_size: Dim2D, colour: Colour):
        if grid_index in TkinterSingleton.grid_frames:
            frame = TkinterSingleton.grid_frames[grid_index]
            frame.configure(background=colour.value)
        else:
            frame = tk.Frame(
                TkinterSingleton.root,
                width=frame_size.x,
                height=frame_size.y,
                background=colour.value,
            )
            TkinterSingleton.grid_frames[grid_index] = frame
            frame.grid(column=grid_index.x, row=grid_index.y)
            TkinterSingleton.set_weight_of_grid_element(frame, grid_index)

    @staticmethod
    def create_rectangle_at(grid_index: Dim2D, tile_size: Dim2D, colour: Colour):
        if grid_index in TkinterSingleton.canvas_rectangles:
            rectangle = TkinterSingleton.canvas_rectangles[grid_index]
            TkinterSingleton.canvas.itemconfig(
                rectangle, fill=colour.value, outline=colour.value
            )
        else:
            coordinates = (
                grid_index.x * tile_size.x + 1,
                grid_index.y * tile_size.y + 1,
                (grid_index.x + 1) * tile_size.x + 1,
                (grid_index.y + 1) * tile_size.y + 1,
            )
            rectangle = TkinterSingleton.canvas.create_rectangle(
                coordinates, fill=colour.value, outline=colour.value
            )
            TkinterSingleton.canvas_rectangles[grid_index] = rectangle

    # TODO: Should be handled in a better way
    @staticmethod
    def clear_rectangle():
        TkinterSingleton.canvas_rectangles = {}

    @staticmethod
    def create_button_with_grid(button_data: ButtonData):
        button = tk.Button(
            TkinterSingleton.root,
            text=button_data.text,
            command=lambda: button_data.callback_function(button_data.parameters),
        )
        button.grid(
            column=button_data.grid_data.index.x,
            row=button_data.grid_data.index.y,
            columnspan=button_data.grid_data.span_size.x,
            rowspan=button_data.grid_data.span_size.y,
            sticky=button_data.grid_data.sticky,
        )
        TkinterSingleton.set_weight_of_grid_element(button, button_data.grid_index)

    # TODO: Merge this with create widget with pack?
    @staticmethod
    def create_frame_with_pack(pack_data: PackData, root=None):
        if root is None:
            root = TkinterSingleton.root
        frame = tk.Frame(root)
        frame.pack(side=pack_data.side, fill=pack_data.fill, expand=pack_data.expand)
        return frame

    @staticmethod
    def create_widget_with_pack(widget_data: WidgetData, root=None):
        if root is None:
            root = TkinterSingleton.root
        widget = None
        if isinstance(widget_data, ButtonData):
            widget = TkinterSingleton.create_button(root, widget_data)
        elif isinstance(widget_data, TextData):
            widget = TkinterSingleton.create_text(root, widget_data)
        elif isinstance(widget_data, LabelData):
            widget = TkinterSingleton.create_label(root, widget_data)
        elif isinstance(widget_data, ScaleData):
            widget = TkinterSingleton.create_scale(root, widget_data)
        widget.pack(
            side=widget_data.pack_data.side,
            fill=widget_data.pack_data.fill,
            expand=widget_data.pack_data.expand,
        )
        TkinterSingleton.widgets[widget_data.id_] = widget

    @staticmethod
    def create_button(root, button_data: ButtonData):
        return tk.Button(
            root,
            text=button_data.text,
            command=lambda: button_data.callback_function(button_data.parameters),
        )

    @staticmethod
    def create_text(root, text_data: TextData):
        text = tk.Text(
            root, height=text_data.number_of_lines, width=text_data.number_of_characters
        )
        text.delete(1.0, "end-1c")
        text.insert("end-1c", text_data.text)
        return text

    @staticmethod
    def create_label(root, label_data: LabelData):
        return tk.Label(
            root,
            text=label_data.text,
        )

    @staticmethod
    def create_scale(root, scale_data: ScaleData):
        return tk.Scale(
            root,
            label=scale_data.text,
            from_=scale_data.from_,
            to=scale_data.to,
            orient=scale_data.orientation,
            command=lambda steps_per_second: scale_data.callback_function(
                scale_data.parameters, steps_per_second
            ),
        )

    @staticmethod
    def update(callback_function, in_milliseconds=1000):
        TkinterSingleton.root.after(in_milliseconds, callback_function)

    @staticmethod
    def refresh():
        TkinterSingleton.root.update()

    @staticmethod
    def loop():
        TkinterSingleton.root.mainloop()

    @staticmethod
    def create_menu_window(title):
        menu_window = tk.Toplevel(TkinterSingleton.root)
        menu_window.title(title)
        menu_window.resizable(width=False, height=False)
        return menu_window
