from draw.tkinter_singleton import TkinterSingleton

from .gui_path_processor import GuiPathProcessor


def main():
    TkinterSingleton.start(title="Graph Search Program")

    gui_path_processor = GuiPathProcessor()
    gui_path_processor.process()

    TkinterSingleton.loop()
    gui_path_processor.depth_first_search.kill_thread()
    gui_path_processor.depth_first_search.join()


if __name__ == "__main__":
    main()
