import io
import threading
from contextlib import redirect_stdout
from types import MethodType

import ipywidgets as widgets
from IPython.display import IFrame
from traitlets import List, Unicode

from containerized_gui.decorator import ContainerizedGUIThread, run_gui, FILE_ARG

FILE = object()


def shutdown(self):
    if self.thread.is_alive():
        self.thread.kill()
        # join to thread to wait for it to finish
        self.thread.join()


# TODO: add a run button
# TODO: input file selector
# TODO: specify output file directory
# TODO: add a stop button
# TODO: handle custom command line
def GUIContainer(
    image_name=None,
    width=1024,
    height=768,
    input_file=None,
    args=[FILE],
    output_files_handler=None,
):
    out = widgets.Output(layout={"border": "1px solid black"})
    out.output_files = List(trait=Unicode())
    out.shutdown = MethodType(shutdown, out)

    # create vnc url handler, write iframe to output widget
    def vnc_url_handler(vnc_url):
        out.append_display_data(IFrame(vnc_url, width, height))

    # def run_gui_thread(input_file):
    #     output_files = run_gui(input_file, image_name, vnc_url_handler=vnc_url_handler)
    #     out.output_files = output_files
    #     if output_files_handler is not None:
    #         # Capture any output from wrapped function and write to output widget
    #         with redirect_stdout(io.StringIO()) as stdout:
    #             output_files_handler(output_files)
    #     # Clear output widget (closes VNC iframe)
    #     # (See https://github.com/jupyter-widgets/ipywidgets/issues/3260#issuecomment-907715980 for this workaround)
    #     out.outputs = ()
    #     out.append_stdout(stdout.getvalue())

    # thread = threading.Thread(target=run_gui_thread, args=(input_file,))
    run_args = list(map(lambda a: FILE_ARG if a is FILE else a, args))
    out.thread = ContainerizedGUIThread(
        input_file,
        image_name,
        vnc_url_handler=vnc_url_handler,
        run_args=run_args,
    )
    out.thread.start()
    print("thread started")

    def cleanup():
        out.thread.join()
        out.output_files = out.thread.output_files
        out.outputs = ()

    threading.Thread(target=cleanup).start()

    return out
