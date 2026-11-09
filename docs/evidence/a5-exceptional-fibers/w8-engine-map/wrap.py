"""Entry stub: runs wrap_body.py only in the parent, so spawned pool workers re-importing __main__ do nothing."""

import os
import runpy
import sys

if __name__ == "__main__":
    runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wrap_body.py"), run_name="wrapbody")
    sys.exit(0)
