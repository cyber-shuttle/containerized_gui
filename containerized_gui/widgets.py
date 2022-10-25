import io
import threading
from contextlib import redirect_stdout

import ipywidgets as widgets
from IPython.display import IFrame
from traitlets import List, Unicode

from containerized_gui.decorator import run_gui

FILE = object()

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

    # create vnc url handler, write iframe to output widget
    def vnc_url_handler(vnc_url):
        out.append_display_data(IFrame(vnc_url, width, height))

    def run_gui_thread(input_file):
        output_files = run_gui(input_file, image_name, vnc_url_handler=vnc_url_handler)
        out.output_files = output_files
        if output_files_handler is not None:
            # Capture any output from wrapped function and write to output widget
            with redirect_stdout(io.StringIO()) as stdout:
                output_files_handler(output_files)
        # Clear output widget (closes VNC iframe)
        # (See https://github.com/jupyter-widgets/ipywidgets/issues/3260#issuecomment-907715980 for this workaround)
        out.outputs = ()
        out.append_stdout(stdout.getvalue())

    thread = threading.Thread(target=run_gui_thread, args=(input_file,))
    thread.start()
    return out
