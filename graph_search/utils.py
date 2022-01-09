import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import List

from draw.tkinter_singleton import TkinterSingleton
from draw.colour import Colour
from draw.widget import PackData, ButtonData, WidgetData, TextData, LabelData, ScaleData

from dekespo_ai_sdk.core.dimensions import Dim2D
from dekespo_ai_sdk.core.graph import Graph
from dekespo_ai_sdk.core.neighbour import NeighbourData, NeighbourType

from dekespo_ai_sdk.algorithms.graph_search.api import GraphSearch


class Status(Enum):
    ON_PAUSE = auto()
    SHOULD_RESTART = auto()
    SHOULD_GO_BACK = auto()
    SHOULD_GO_NEXT = auto()
    SHOULD_PLAY_FORWARD = auto()
    SHOULD_RESET = auto()
    OPTIONS_SET = auto()


class Options(Enum):
    TILE_SIZE = auto()
    GRID_SIZE = auto()
    STEPS_PER_SECOND = auto()


@dataclass
class GraphData:
    tile_size: Dim2D
    grid_size: Dim2D
    graph: Graph


# pylint: disable=too-few-public-methods
class Scale:
    @staticmethod
    def on_scale(current_options, steps_per_second):
        current_options[Options.STEPS_PER_SECOND] = int(steps_per_second)


class Button:
    @staticmethod
    def back(status_dictionary):
        status_dictionary[Status.SHOULD_GO_BACK] = True

    @staticmethod
    def next(status_dictionary):
        status_dictionary[Status.SHOULD_GO_NEXT] = True

    @staticmethod
    def play_forward(status_dictionary):
        status_dictionary[Status.ON_PAUSE] = False
        status_dictionary[Status.SHOULD_PLAY_FORWARD] = True

    @staticmethod
    def play_backward(status_dictionary):
        status_dictionary[Status.ON_PAUSE] = False
        status_dictionary[Status.SHOULD_PLAY_FORWARD] = False

    @staticmethod
    def pause(status_dictionary):
        status_dictionary[Status.ON_PAUSE] = True

    @staticmethod
    def restart(status_dictionary):
        status_dictionary[Status.SHOULD_RESTART] = True

    @staticmethod
    def reset(status_dictionary):
        status_dictionary[Status.SHOULD_RESET] = True

    @staticmethod
    def open_options(args):
        # TODO: Instead use a button and use this for cancelling
        def remove_window(args):
            menu_window, status_dictionary = args
            current_options[Options.TILE_SIZE].x = int(
                TkinterSingleton.widgets["tile_size_x"].get("1.0", "end-1c")
            )
            current_options[Options.TILE_SIZE].y = int(
                TkinterSingleton.widgets["tile_size_y"].get("1.0", "end-1c")
            )
            current_options[Options.GRID_SIZE].x = int(
                TkinterSingleton.widgets["grid_size_x"].get("1.0", "end-1c")
            )
            current_options[Options.GRID_SIZE].y = int(
                TkinterSingleton.widgets["grid_size_y"].get("1.0", "end-1c")
            )
            status_dictionary[Status.OPTIONS_SET] = True
            menu_window.destroy()

        status_dictionary, current_options = args
        menu_window = TkinterSingleton.create_menu_window("Options")

        def create_text_data(value, id_, number_of_characters=3, number_of_lines=1):
            return TextData(
                value,
                id_=id_,
                number_of_characters=number_of_characters,
                number_of_lines=number_of_lines,
            )

        tile_size_frame = TkinterSingleton.create_frame_with_pack(
            PackData(side=None), menu_window
        )
        tile_size_widgets = [
            LabelData("Tile Size: "),
            create_text_data(current_options[Options.TILE_SIZE].x, "tile_size_x"),
            LabelData("x"),
            create_text_data(current_options[Options.TILE_SIZE].y, "tile_size_y"),
        ]
        GuiUtils.create_widgets(tile_size_widgets, tile_size_frame)
        grid_size_frame = TkinterSingleton.create_frame_with_pack(
            PackData(side=None), menu_window
        )
        grid_size_widgets = [
            LabelData("Grid Size: "),
            create_text_data(current_options[Options.GRID_SIZE].x, "grid_size_x"),
            LabelData("x"),
            create_text_data(current_options[Options.GRID_SIZE].y, "grid_size_y"),
        ]
        GuiUtils.create_widgets(grid_size_widgets, grid_size_frame)
        menu_window.protocol(
            "WM_DELETE_WINDOW",
            lambda args=[menu_window, status_dictionary]: remove_window(args),
        )
        menu_window.focus_set()
        menu_window.grab_set()


class Utils:
    @staticmethod
    def create_rectangle_canvas(graph_data: GraphData) -> List[List]:
        raw_data: List = []
        for y in range(graph_data.grid_size.y):
            row_raw_data: List = []
            for x in range(graph_data.grid_size.x):
                TkinterSingleton.create_rectangle_at(
                    Dim2D(x, y), graph_data.tile_size, Colour.BLACK
                )
                row_raw_data.append(0)
            raw_data.append(row_raw_data)
        return raw_data

    @staticmethod
    def get_random_edge_point(grid_size):
        four_sides = ["top", "bottom", "left", "right"]
        chosen_side = four_sides[random.randint(0, len(four_sides) - 1)]
        return {
            "top": Dim2D(random.randint(0, grid_size.x - 1), 0),
            "bottom": Dim2D(random.randint(0, grid_size.x - 1), grid_size.y - 1),
            "left": Dim2D(0, random.randint(0, grid_size.y - 1)),
            "right": Dim2D(grid_size.x - 1, random.randint(0, grid_size.y - 1)),
        }[chosen_side]

    @staticmethod
    def initialize_depth_first_search(graph_data: GraphData):
        start_point = Utils.get_random_edge_point(graph_data.grid_size)
        neighbour_data = NeighbourData(NeighbourType.CROSS, random_output=True)
        depth_first_search = GraphSearch(
            graph_data.graph, start_point
        ).depth_first_search(neighbour_data, runs_with_thread=True)
        depth_first_search.event_set()
        depth_first_search.start()
        return depth_first_search

    @staticmethod
    def get_default_status_dictionary():
        return {
            Status.ON_PAUSE: True,
            Status.SHOULD_RESTART: False,
            Status.SHOULD_GO_BACK: False,
            Status.SHOULD_GO_NEXT: False,
            Status.SHOULD_PLAY_FORWARD: True,
            Status.SHOULD_RESET: False,
            Status.OPTIONS_SET: False,
        }

    @staticmethod
    def get_default_options_dictionary():
        return {
            Options.TILE_SIZE: Dim2D(10, 10),
            Options.GRID_SIZE: Dim2D(60, 60),
            Options.STEPS_PER_SECOND: 60,
        }


class GuiUtils:
    @staticmethod
    def create_widgets(widgets_data: List[WidgetData], frame):
        default_pack_data = PackData()
        for data in widgets_data:
            if data.pack_data is None:
                data.pack_data = default_pack_data
            TkinterSingleton.create_widget_with_pack(data, frame)

    # TODO: Make this more resuable for different windows
    @staticmethod
    def create_buttons_layer(status_dictionary, current_options):
        player_frame = TkinterSingleton.create_frame_with_pack(PackData(side=None))
        player_buttons = [
            ButtonData("back", Button.back, status_dictionary),
            ButtonData("next", Button.next, status_dictionary),
            ButtonData("play_forward", Button.play_forward, status_dictionary),
            ButtonData("play_backward", Button.play_backward, status_dictionary),
            ButtonData("pause", Button.pause, status_dictionary),
            ButtonData("restart", Button.restart, status_dictionary),
        ]
        GuiUtils.create_widgets(player_buttons, player_frame)

        others_frame = TkinterSingleton.create_frame_with_pack(PackData(side=None))
        others_buttons = [
            ButtonData("reset", Button.reset, status_dictionary),
            ButtonData(
                "options", Button.open_options, [status_dictionary, current_options]
            ),
        ]
        GuiUtils.create_widgets(others_buttons, others_frame)

    @staticmethod
    def create_slider_layer(current_options):
        slider_frame = TkinterSingleton.create_frame_with_pack(PackData(side=None))
        sliders = [
            ScaleData(
                text="Number of steps in second",
                id_="speed_scaler",
                callback_function=Scale.on_scale,
                parameters=current_options,
                from_=1,
                to=1000,
                orientation="horizontal",
            )
        ]
        GuiUtils.create_widgets(sliders, slider_frame)
        TkinterSingleton.widgets["speed_scaler"].set(
            current_options[Options.STEPS_PER_SECOND]
        )
