from draw.tkinter_singleton import TkinterSingleton
from draw.colour import Colour

from core.shapes import Shape2D
from core.graph import Graph

from .utils import Status, Utils, GuiUtils, GraphData, Options

# TODO: Make sure to have more user friendly (automatic start with reset,
#  should first step show red and etc)
# pylint: disable=too-many-instance-attributes
class GuiPathProcessor:

    # TODO: Generalise this to any Graph Search Algorithm
    @property
    def depth_first_search(self):
        return self._depth_first_search

    def __init__(self):
        self._status_dictionary = Utils.get_default_status_dictionary()
        self._current_options = Utils.get_default_options_dictionary()
        TkinterSingleton.create_canvas()
        self._graph_data = GuiPathProcessor._set_gui(self._current_options)
        GuiUtils.create_buttons_layer(self._status_dictionary, self._current_options)
        GuiUtils.create_slider_layer(self._current_options)
        TkinterSingleton.refresh()
        self._start_path_index = 0
        self._current_path_index = self._start_path_index
        # TODO: Should run _reset instead?
        self._run_dfs()

    @staticmethod
    def _set_gui(current_options):
        tile_size = current_options[Options.TILE_SIZE]
        grid_size = current_options[Options.GRID_SIZE]
        TkinterSingleton.resize_canvas(tile_size.vectoral_multiply(grid_size))
        TkinterSingleton.canvas.configure(background=Colour.GREEN.value)
        TkinterSingleton.canvas.pack(fill="both", expand=True)
        graph_data = GraphData(tile_size, grid_size, None)
        TkinterSingleton.clear_rectangle()
        raw_grid_data = Utils.create_rectangle_canvas(graph_data)
        graph_data.graph = Graph(raw_grid_data, Shape2D.Type.RECTANGLE)
        return graph_data

    def _run_dfs(self):
        self._depth_first_search = Utils.initialize_depth_first_search(self._graph_data)
        self._graph_search_closed_set = self._depth_first_search.get_closed_set()

    def _set_options(self):
        self._graph_data = GuiPathProcessor._set_gui(self._current_options)
        TkinterSingleton.refresh()
        self._status_dictionary[Status.OPTIONS_SET] = False
        self._reset()

    def process(self):
        if self._status_dictionary[Status.OPTIONS_SET]:
            self._set_options()
        elif self._status_dictionary[Status.SHOULD_RESET]:
            self._reset()
        elif self._status_dictionary[Status.SHOULD_RESTART]:
            self._restart()
        elif self._status_dictionary[Status.SHOULD_GO_BACK]:
            self._go_back()
        elif self._status_dictionary[Status.SHOULD_GO_NEXT]:
            self._go_next()
        elif self._status_dictionary[Status.ON_PAUSE]:
            self._on_pause()
        elif self._is_last_step():
            self._on_last_step()
        elif self._status_dictionary[Status.SHOULD_PLAY_FORWARD]:
            self._on_play_forward()
        else:
            self._on_play_backward()

    def _update_path(self):
        TkinterSingleton.update(
            self.process,
            in_milliseconds=round(
                1000 / self._current_options[Options.STEPS_PER_SECOND]
            ),
        )

    def _reset(self):
        self._depth_first_search.kill_thread()
        self._depth_first_search.join()
        Utils.create_rectangle_canvas(self._graph_data)
        self._current_path_index = self._start_path_index
        self._run_dfs()
        self._status_dictionary[Status.SHOULD_RESET] = False
        self._update_path()

    def _restart(self):
        Utils.create_rectangle_canvas(self._graph_data)
        self._current_path_index = self._start_path_index
        self._status_dictionary[Status.SHOULD_RESTART] = False
        self._update_path()

    def _go_back(self):
        self._back_red_colouring()
        self._back_black_colouring()
        self._status_dictionary[Status.SHOULD_GO_BACK] = False
        self._status_dictionary[Status.ON_PAUSE] = True
        self._on_pause()

    def _go_next(self):
        self._next_white_colouring()
        self._next_red_colouring()
        self._status_dictionary[Status.SHOULD_GO_NEXT] = False
        self._status_dictionary[Status.ON_PAUSE] = True
        self._on_pause()

    def _on_pause(self):
        self._update_path()

    def _is_last_step(self):
        return self._current_path_index == len(self._graph_search_closed_set)

    def _on_last_step(self):
        previous_point = self._graph_search_closed_set[self._current_path_index - 1]
        self._create_rectangle_at(previous_point, Colour.RED)
        self._status_dictionary[Status.ON_PAUSE] = True
        self._update_path()

    def _on_play_forward(self):
        self._next_white_colouring()
        self._next_red_colouring()
        self._update_path()

    def _on_play_backward(self):
        self._back_red_colouring()
        self._back_black_colouring()
        self._update_path()

    def _next_white_colouring(self):
        if self._current_path_index > self._start_path_index:
            previous_point = self._graph_search_closed_set[self._current_path_index - 1]
            self._create_rectangle_at(previous_point, Colour.WHITE)

    def _next_red_colouring(self):
        if self._current_path_index < len(self._graph_search_closed_set):
            # TODO: This part goes up to some 33 ms until dfs thread is done, find what causes this?
            current_point = self._graph_search_closed_set[self._current_path_index]
            self._create_rectangle_at(current_point, Colour.RED)
            self._current_path_index += 1

    def _back_red_colouring(self):
        if self._current_path_index > self._start_path_index + 1:
            self._current_path_index -= 1
            previous_point = self._graph_search_closed_set[self._current_path_index - 1]
            self._create_rectangle_at(previous_point, Colour.RED)

    def _back_black_colouring(self):
        current_point = self._graph_search_closed_set[self._current_path_index]
        self._create_rectangle_at(current_point, Colour.BLACK)

    def _create_rectangle_at(self, point, colour: Colour):
        TkinterSingleton.create_rectangle_at(point, self._graph_data.tile_size, colour)
