"""Kaggle CPU kernel body of the E8-bar -> VB export-lever campaign.

make_kernels.py writes one kernel per prime from this file, replacing CONFIG_B64 with the base64 of its job list. The
kernel installs passagemath Singular 4.4.1, runs every job four at a time and writes /kaggle/working/summary.json.
It exits 1 when any job failed (see `failures`), so a failed export never reads as a successful kernel.

Kaggle stops a CPU session at 12 hours. Every job gets the smaller of its own deadline and the time left before
SESSION_SECONDS (12 h less a margin for setup and the final write), so the kernel always ends by itself, and
summary.json is rewritten after every finished job, so a session that ends early keeps every finished result.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import sysconfig
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

CONFIG_B64 = (
    "eyJqb2JzIjogW3sibmFtZSI6ICJzbGltZ2ItbjIxLXAzMjAwOSIsICJzY3JpcHQiOiAicmluZyByPTMyMDA5LCh0MSx0Mix0Myx0"
    "NCx0NSx0Nix0Nyx0OCksZHA7XG5pZGVhbCBKPXQzXjItdDReMi10NV4yK3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIq"
    "dDgsdDQqdDUqdDgtdDMqdDYqdDgtdDMqdDUtdDQqdDUrdDMqdDYrdDQqdDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUq"
    "dDYrdDZeMix0Myp0NCp0OC10NSp0Nip0OC10Myp0NC10NF4yLXQ1XjIrdDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEq"
    "dDUtdDEqdDYtMip0NCp0OCx0MSp0NCp0OCt0Mip0Nip0OC10MSp0My10MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1"
    "KnQ4LXQyKnQzLXQxKnQ1K3QxKnQ2LTIqdDMqdDgsdDEqdDMqdDgrdDIqdDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0"
    "Mip0Myp0NSt0MSp0NV4yLXQyKnQ0KnQ2LXQxKnQ2XjItMip0Myp0NS0yKnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3Qx"
    "KnQzKnQ1K3QyKnQ1XjIrdDEqdDQqdDYtMip0Myp0NC0yKnQ0XjItMip0NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEq"
    "dDMqdDYrdDIqdDUqdDYtMip0Myp0NC0yKnQ0XjItMip0NSp0NisyKnQ2XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDhe"
    "Myt0Ml4yLTQqdDIqdDgsdDYqdDdeMip0OC10Nip0OF4zLXQxKnQyKnQzLXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIr"
    "Myp0Nip0OF4yKzIqdDEqdDMrMip0MSp0NCs0KnQyKnQ1LTIqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDhe"
    "My10MSp0Mip0NC10Ml4yKnQ2LXQ1KnQ3XjIrdDYqdDdeMiszKnQ1KnQ4XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0"
    "NSs0KnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NCp0N14yKnQ4LXQ0KnQ4XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3"
    "XjIrdDMqdDheMiszKnQ0KnQ4XjItNCp0Mip0My0yKnQyKnQ0LTIqdDEqdDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDde"
    "Mip0OC10Myp0OF4zK3QyXjIqdDQrdDEqdDIqdDYtdDMqdDdeMi10NCp0N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0"
    "Mip0NCsyKnQxKnQ1LTIqdDEqdDYrMip0Myp0OC0yKnQ0KnQ4O1xub3B0aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXIt"
    "c2VjXCIsMTAwMCk7IGludCB0MD1ydGltZXI7XG5pZGVhbCBzPXNsaW1nYihKK21heGlkZWFsKDIxKSk7XG5cIlJFU1VMVCBtc1wi"
    "LHJ0aW1lci10MCxcInNiX3NpemVcIixuY29scyhzKTtcbmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixu"
    "Y29scyhCKTtcbnNob3J0PTA7IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL3NsaW1nYi1uMjEtcDMyMDA5L3MudHh0XCIscyk7"
    "IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL3NsaW1nYi1uMjEtcDMyMDA5L2tiYXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7"
    "Im5hbWUiOiAic2xpbWdiLW4yMi1wMzIwMDkiLCAic2NyaXB0IjogInJpbmcgcj0zMjAwOSwodDEsdDIsdDMsdDQsdDUsdDYsdDcs"
    "dDgpLGRwO1xuaWRlYWwgSj10M14yLXQ0XjItdDVeMit0Nl4yLHQxXjItdDJeMit0N14yLXQ4XjIrNCp0MisyKnQ4LHQ0KnQ1KnQ4"
    "LXQzKnQ2KnQ4LXQzKnQ1LXQ0KnQ1K3QzKnQ2K3Q0KnQ2LHQ0XjIqdDgtdDZeMip0OC10Myp0NC10NF4yLXQ1KnQ2K3Q2XjIsdDMq"
    "dDQqdDgtdDUqdDYqdDgtdDMqdDQtdDReMi10NV4yK3Q1KnQ2LHQyKnQ0KnQ4K3QxKnQ2KnQ4LXQyKnQ0K3QxKnQ1LXQxKnQ2LTIq"
    "dDQqdDgsdDEqdDQqdDgrdDIqdDYqdDgtdDEqdDMtdDEqdDQtdDIqdDYtMip0Nip0OCx0Mip0Myp0OCt0MSp0NSp0OC10Mip0My10"
    "MSp0NSt0MSp0Ni0yKnQzKnQ4LHQxKnQzKnQ4K3QyKnQ1KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ1LTIqdDUqdDgsdDIqdDMqdDUrdDEq"
    "dDVeMi10Mip0NCp0Ni10MSp0Nl4yLTIqdDMqdDUtMip0NCp0NSsyKnQzKnQ2KzIqdDQqdDYsdDIqdDReMit0MSp0Myp0NSt0Mip0"
    "NV4yK3QxKnQ0KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDVeMisyKnQ1KnQ2LHQyKnQzKnQ0K3QxKnQ0KnQ1K3QxKnQzKnQ2K3QyKnQ1"
    "KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDUqdDYrMip0Nl4yLHQ3XjIqdDheMi10OF40LTIqdDdeMip0OCs0KnQ4XjMrdDJeMi00KnQy"
    "KnQ4LHQ2KnQ3XjIqdDgtdDYqdDheMy10MSp0Mip0My10Ml4yKnQ1K3Q1KnQ3XjItdDYqdDdeMi10NSp0OF4yKzMqdDYqdDheMisy"
    "KnQxKnQzKzIqdDEqdDQrNCp0Mip0NS0yKnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NSp0N14yKnQ4LXQ1KnQ4XjMtdDEqdDIqdDQt"
    "dDJeMip0Ni10NSp0N14yK3Q2KnQ3XjIrMyp0NSp0OF4yLXQ2KnQ4XjIrMip0MSp0MysyKnQxKnQ0LTIqdDIqdDUrNCp0Mip0Nisy"
    "KnQ1KnQ4KzIqdDYqdDgsdDQqdDdeMip0OC10NCp0OF4zK3QyXjIqdDMrdDEqdDIqdDUtdDMqdDdeMi10NCp0N14yK3QzKnQ4XjIr"
    "Myp0NCp0OF4yLTQqdDIqdDMtMip0Mip0NC0yKnQxKnQ1KzIqdDEqdDYtMip0Myp0OCsyKnQ0KnQ4LHQzKnQ3XjIqdDgtdDMqdDhe"
    "Myt0Ml4yKnQ0K3QxKnQyKnQ2LXQzKnQ3XjItdDQqdDdeMiszKnQzKnQ4XjIrdDQqdDheMi0yKnQyKnQzLTQqdDIqdDQrMip0MSp0"
    "NS0yKnQxKnQ2KzIqdDMqdDgtMip0NCp0ODtcbm9wdGlvbihyZWRTQik7IHN5c3RlbShcIi0tdGlja3MtcGVyLXNlY1wiLDEwMDAp"
    "OyBpbnQgdDA9cnRpbWVyO1xuaWRlYWwgcz1zbGltZ2IoSittYXhpZGVhbCgyMikpO1xuXCJSRVNVTFQgbXNcIixydGltZXItdDAs"
    "XCJzYl9zaXplXCIsbmNvbHMocyk7XG5pZGVhbCBCPWtiYXNlKHMpOyBcIlJFU1VMVCBrYmFzZV9zaXplXCIsbmNvbHMoQik7XG5z"
    "aG9ydD0wOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9zbGltZ2ItbjIyLXAzMjAwOS9zLnR4dFwiLHMpOyB3cml0ZShcIjp3"
    "IC9rYWdnbGUvd29ya2luZy9zbGltZ2ItbjIyLXAzMjAwOS9rYmFzZS50eHRcIixCKTtcbnF1aXQ7XG4ifSwgeyJuYW1lIjogIm9y"
    "ZGVyLWlkZW50aXR5LW4xNSIsICJzY3JpcHQiOiAicmluZyByPTMyMDA5LCh0MSx0Mix0Myx0NCx0NSx0Nix0Nyx0OCksZHA7XG5p"
    "ZGVhbCBKPXQzXjItdDReMi10NV4yK3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIqdDgsdDQqdDUqdDgtdDMqdDYqdDgt"
    "dDMqdDUtdDQqdDUrdDMqdDYrdDQqdDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUqdDYrdDZeMix0Myp0NCp0OC10NSp0"
    "Nip0OC10Myp0NC10NF4yLXQ1XjIrdDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEqdDUtdDEqdDYtMip0NCp0OCx0MSp0"
    "NCp0OCt0Mip0Nip0OC10MSp0My10MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1KnQ4LXQyKnQzLXQxKnQ1K3QxKnQ2"
    "LTIqdDMqdDgsdDEqdDMqdDgrdDIqdDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0Mip0Myp0NSt0MSp0NV4yLXQyKnQ0"
    "KnQ2LXQxKnQ2XjItMip0Myp0NS0yKnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3QxKnQzKnQ1K3QyKnQ1XjIrdDEqdDQq"
    "dDYtMip0Myp0NC0yKnQ0XjItMip0NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEqdDMqdDYrdDIqdDUqdDYtMip0Myp0"
    "NC0yKnQ0XjItMip0NSp0NisyKnQ2XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDheMyt0Ml4yLTQqdDIqdDgsdDYqdDde"
    "Mip0OC10Nip0OF4zLXQxKnQyKnQzLXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIrMyp0Nip0OF4yKzIqdDEqdDMrMip0"
    "MSp0NCs0KnQyKnQ1LTIqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDheMy10MSp0Mip0NC10Ml4yKnQ2LXQ1"
    "KnQ3XjIrdDYqdDdeMiszKnQ1KnQ4XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0NSs0KnQyKnQ2KzIqdDUqdDgrMip0"
    "Nip0OCx0NCp0N14yKnQ4LXQ0KnQ4XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3XjIrdDMqdDheMiszKnQ0KnQ4XjIt"
    "NCp0Mip0My0yKnQyKnQ0LTIqdDEqdDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDdeMip0OC10Myp0OF4zK3QyXjIqdDQr"
    "dDEqdDIqdDYtdDMqdDdeMi10NCp0N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0Mip0NCsyKnQxKnQ1LTIqdDEqdDYr"
    "Mip0Myp0OC0yKnQ0KnQ4O1xub3B0aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXItc2VjXCIsMTAwMCk7IGludCB0MD1y"
    "dGltZXI7XG5pZGVhbCBzPXNsaW1nYihKK21heGlkZWFsKDE1KSk7XG5cIlJFU1VMVCBtc1wiLHJ0aW1lci10MCxcInNiX3NpemVc"
    "IixuY29scyhzKTtcbmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixuY29scyhCKTtcbnNob3J0PTA7IHdy"
    "aXRlKFwiOncgL2thZ2dsZS93b3JraW5nL29yZGVyLWlkZW50aXR5LW4xNS9zLnR4dFwiLHMpOyB3cml0ZShcIjp3IC9rYWdnbGUv"
    "d29ya2luZy9vcmRlci1pZGVudGl0eS1uMTUva2Jhc2UudHh0XCIsQik7XG5xdWl0O1xuIn0sIHsibmFtZSI6ICJvcmRlci1yb3Qx"
    "LW4xNSIsICJzY3JpcHQiOiAicmluZyByPTMyMDA5LCh0Mix0Myx0NCx0NSx0Nix0Nyx0OCx0MSksZHA7XG5pZGVhbCBKPXQzXjIt"
    "dDReMi10NV4yK3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIqdDgsdDQqdDUqdDgtdDMqdDYqdDgtdDMqdDUtdDQqdDUr"
    "dDMqdDYrdDQqdDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUqdDYrdDZeMix0Myp0NCp0OC10NSp0Nip0OC10Myp0NC10"
    "NF4yLXQ1XjIrdDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEqdDUtdDEqdDYtMip0NCp0OCx0MSp0NCp0OCt0Mip0Nip0"
    "OC10MSp0My10MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1KnQ4LXQyKnQzLXQxKnQ1K3QxKnQ2LTIqdDMqdDgsdDEq"
    "dDMqdDgrdDIqdDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0Mip0Myp0NSt0MSp0NV4yLXQyKnQ0KnQ2LXQxKnQ2XjIt"
    "Mip0Myp0NS0yKnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3QxKnQzKnQ1K3QyKnQ1XjIrdDEqdDQqdDYtMip0Myp0NC0y"
    "KnQ0XjItMip0NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEqdDMqdDYrdDIqdDUqdDYtMip0Myp0NC0yKnQ0XjItMip0"
    "NSp0NisyKnQ2XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDheMyt0Ml4yLTQqdDIqdDgsdDYqdDdeMip0OC10Nip0OF4z"
    "LXQxKnQyKnQzLXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIrMyp0Nip0OF4yKzIqdDEqdDMrMip0MSp0NCs0KnQyKnQ1"
    "LTIqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDheMy10MSp0Mip0NC10Ml4yKnQ2LXQ1KnQ3XjIrdDYqdDde"
    "MiszKnQ1KnQ4XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0NSs0KnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NCp0N14y"
    "KnQ4LXQ0KnQ4XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3XjIrdDMqdDheMiszKnQ0KnQ4XjItNCp0Mip0My0yKnQy"
    "KnQ0LTIqdDEqdDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDdeMip0OC10Myp0OF4zK3QyXjIqdDQrdDEqdDIqdDYtdDMq"
    "dDdeMi10NCp0N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0Mip0NCsyKnQxKnQ1LTIqdDEqdDYrMip0Myp0OC0yKnQ0"
    "KnQ4O1xub3B0aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXItc2VjXCIsMTAwMCk7IGludCB0MD1ydGltZXI7XG5pZGVh"
    "bCBzPXNsaW1nYihKK21heGlkZWFsKDE1KSk7XG5cIlJFU1VMVCBtc1wiLHJ0aW1lci10MCxcInNiX3NpemVcIixuY29scyhzKTtc"
    "bmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixuY29scyhCKTtcbnNob3J0PTA7IHdyaXRlKFwiOncgL2th"
    "Z2dsZS93b3JraW5nL29yZGVyLXJvdDEtbjE1L3MudHh0XCIscyk7IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL29yZGVyLXJv"
    "dDEtbjE1L2tiYXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7Im5hbWUiOiAib3JkZXItcm90Mi1uMTUiLCAic2NyaXB0IjogInJp"
    "bmcgcj0zMjAwOSwodDMsdDQsdDUsdDYsdDcsdDgsdDEsdDIpLGRwO1xuaWRlYWwgSj10M14yLXQ0XjItdDVeMit0Nl4yLHQxXjIt"
    "dDJeMit0N14yLXQ4XjIrNCp0MisyKnQ4LHQ0KnQ1KnQ4LXQzKnQ2KnQ4LXQzKnQ1LXQ0KnQ1K3QzKnQ2K3Q0KnQ2LHQ0XjIqdDgt"
    "dDZeMip0OC10Myp0NC10NF4yLXQ1KnQ2K3Q2XjIsdDMqdDQqdDgtdDUqdDYqdDgtdDMqdDQtdDReMi10NV4yK3Q1KnQ2LHQyKnQ0"
    "KnQ4K3QxKnQ2KnQ4LXQyKnQ0K3QxKnQ1LXQxKnQ2LTIqdDQqdDgsdDEqdDQqdDgrdDIqdDYqdDgtdDEqdDMtdDEqdDQtdDIqdDYt"
    "Mip0Nip0OCx0Mip0Myp0OCt0MSp0NSp0OC10Mip0My10MSp0NSt0MSp0Ni0yKnQzKnQ4LHQxKnQzKnQ4K3QyKnQ1KnQ4LXQxKnQz"
    "LXQxKnQ0LXQyKnQ1LTIqdDUqdDgsdDIqdDMqdDUrdDEqdDVeMi10Mip0NCp0Ni10MSp0Nl4yLTIqdDMqdDUtMip0NCp0NSsyKnQz"
    "KnQ2KzIqdDQqdDYsdDIqdDReMit0MSp0Myp0NSt0Mip0NV4yK3QxKnQ0KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDVeMisyKnQ1KnQ2"
    "LHQyKnQzKnQ0K3QxKnQ0KnQ1K3QxKnQzKnQ2K3QyKnQ1KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDUqdDYrMip0Nl4yLHQ3XjIqdDhe"
    "Mi10OF40LTIqdDdeMip0OCs0KnQ4XjMrdDJeMi00KnQyKnQ4LHQ2KnQ3XjIqdDgtdDYqdDheMy10MSp0Mip0My10Ml4yKnQ1K3Q1"
    "KnQ3XjItdDYqdDdeMi10NSp0OF4yKzMqdDYqdDheMisyKnQxKnQzKzIqdDEqdDQrNCp0Mip0NS0yKnQyKnQ2KzIqdDUqdDgrMip0"
    "Nip0OCx0NSp0N14yKnQ4LXQ1KnQ4XjMtdDEqdDIqdDQtdDJeMip0Ni10NSp0N14yK3Q2KnQ3XjIrMyp0NSp0OF4yLXQ2KnQ4XjIr"
    "Mip0MSp0MysyKnQxKnQ0LTIqdDIqdDUrNCp0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDQqdDdeMip0OC10NCp0OF4zK3QyXjIqdDMr"
    "dDEqdDIqdDUtdDMqdDdeMi10NCp0N14yK3QzKnQ4XjIrMyp0NCp0OF4yLTQqdDIqdDMtMip0Mip0NC0yKnQxKnQ1KzIqdDEqdDYt"
    "Mip0Myp0OCsyKnQ0KnQ4LHQzKnQ3XjIqdDgtdDMqdDheMyt0Ml4yKnQ0K3QxKnQyKnQ2LXQzKnQ3XjItdDQqdDdeMiszKnQzKnQ4"
    "XjIrdDQqdDheMi0yKnQyKnQzLTQqdDIqdDQrMip0MSp0NS0yKnQxKnQ2KzIqdDMqdDgtMip0NCp0ODtcbm9wdGlvbihyZWRTQik7"
    "IHN5c3RlbShcIi0tdGlja3MtcGVyLXNlY1wiLDEwMDApOyBpbnQgdDA9cnRpbWVyO1xuaWRlYWwgcz1zbGltZ2IoSittYXhpZGVh"
    "bCgxNSkpO1xuXCJSRVNVTFQgbXNcIixydGltZXItdDAsXCJzYl9zaXplXCIsbmNvbHMocyk7XG5pZGVhbCBCPWtiYXNlKHMpOyBc"
    "IlJFU1VMVCBrYmFzZV9zaXplXCIsbmNvbHMoQik7XG5zaG9ydD0wOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9vcmRlci1y"
    "b3QyLW4xNS9zLnR4dFwiLHMpOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9vcmRlci1yb3QyLW4xNS9rYmFzZS50eHRcIixC"
    "KTtcbnF1aXQ7XG4ifSwgeyJuYW1lIjogIm9yZGVyLXJvdDMtbjE1IiwgInNjcmlwdCI6ICJyaW5nIHI9MzIwMDksKHQ0LHQ1LHQ2"
    "LHQ3LHQ4LHQxLHQyLHQzKSxkcDtcbmlkZWFsIEo9dDNeMi10NF4yLXQ1XjIrdDZeMix0MV4yLXQyXjIrdDdeMi10OF4yKzQqdDIr"
    "Mip0OCx0NCp0NSp0OC10Myp0Nip0OC10Myp0NS10NCp0NSt0Myp0Nit0NCp0Nix0NF4yKnQ4LXQ2XjIqdDgtdDMqdDQtdDReMi10"
    "NSp0Nit0Nl4yLHQzKnQ0KnQ4LXQ1KnQ2KnQ4LXQzKnQ0LXQ0XjItdDVeMit0NSp0Nix0Mip0NCp0OCt0MSp0Nip0OC10Mip0NCt0"
    "MSp0NS10MSp0Ni0yKnQ0KnQ4LHQxKnQ0KnQ4K3QyKnQ2KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ2LTIqdDYqdDgsdDIqdDMqdDgrdDEq"
    "dDUqdDgtdDIqdDMtdDEqdDUrdDEqdDYtMip0Myp0OCx0MSp0Myp0OCt0Mip0NSp0OC10MSp0My10MSp0NC10Mip0NS0yKnQ1KnQ4"
    "LHQyKnQzKnQ1K3QxKnQ1XjItdDIqdDQqdDYtdDEqdDZeMi0yKnQzKnQ1LTIqdDQqdDUrMip0Myp0NisyKnQ0KnQ2LHQyKnQ0XjIr"
    "dDEqdDMqdDUrdDIqdDVeMit0MSp0NCp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1XjIrMip0NSp0Nix0Mip0Myp0NCt0MSp0NCp0NSt0"
    "MSp0Myp0Nit0Mip0NSp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1KnQ2KzIqdDZeMix0N14yKnQ4XjItdDheNC0yKnQ3XjIqdDgrNCp0"
    "OF4zK3QyXjItNCp0Mip0OCx0Nip0N14yKnQ4LXQ2KnQ4XjMtdDEqdDIqdDMtdDJeMip0NSt0NSp0N14yLXQ2KnQ3XjItdDUqdDhe"
    "MiszKnQ2KnQ4XjIrMip0MSp0MysyKnQxKnQ0KzQqdDIqdDUtMip0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDUqdDdeMip0OC10NSp0"
    "OF4zLXQxKnQyKnQ0LXQyXjIqdDYtdDUqdDdeMit0Nip0N14yKzMqdDUqdDheMi10Nip0OF4yKzIqdDEqdDMrMip0MSp0NC0yKnQy"
    "KnQ1KzQqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ0KnQ3XjIqdDgtdDQqdDheMyt0Ml4yKnQzK3QxKnQyKnQ1LXQzKnQ3XjItdDQq"
    "dDdeMit0Myp0OF4yKzMqdDQqdDheMi00KnQyKnQzLTIqdDIqdDQtMip0MSp0NSsyKnQxKnQ2LTIqdDMqdDgrMip0NCp0OCx0Myp0"
    "N14yKnQ4LXQzKnQ4XjMrdDJeMip0NCt0MSp0Mip0Ni10Myp0N14yLXQ0KnQ3XjIrMyp0Myp0OF4yK3Q0KnQ4XjItMip0Mip0My00"
    "KnQyKnQ0KzIqdDEqdDUtMip0MSp0NisyKnQzKnQ4LTIqdDQqdDg7XG5vcHRpb24ocmVkU0IpOyBzeXN0ZW0oXCItLXRpY2tzLXBl"
    "ci1zZWNcIiwxMDAwKTsgaW50IHQwPXJ0aW1lcjtcbmlkZWFsIHM9c2xpbWdiKEorbWF4aWRlYWwoMTUpKTtcblwiUkVTVUxUIG1z"
    "XCIscnRpbWVyLXQwLFwic2Jfc2l6ZVwiLG5jb2xzKHMpO1xuaWRlYWwgQj1rYmFzZShzKTsgXCJSRVNVTFQga2Jhc2Vfc2l6ZVwi"
    "LG5jb2xzKEIpO1xuc2hvcnQ9MDsgd3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90My1uMTUvcy50eHRcIixzKTsg"
    "d3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90My1uMTUva2Jhc2UudHh0XCIsQik7XG5xdWl0O1xuIn0sIHsibmFt"
    "ZSI6ICJvcmRlci1yb3Q0LW4xNSIsICJzY3JpcHQiOiAicmluZyByPTMyMDA5LCh0NSx0Nix0Nyx0OCx0MSx0Mix0Myx0NCksZHA7"
    "XG5pZGVhbCBKPXQzXjItdDReMi10NV4yK3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIqdDgsdDQqdDUqdDgtdDMqdDYq"
    "dDgtdDMqdDUtdDQqdDUrdDMqdDYrdDQqdDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUqdDYrdDZeMix0Myp0NCp0OC10"
    "NSp0Nip0OC10Myp0NC10NF4yLXQ1XjIrdDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEqdDUtdDEqdDYtMip0NCp0OCx0"
    "MSp0NCp0OCt0Mip0Nip0OC10MSp0My10MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1KnQ4LXQyKnQzLXQxKnQ1K3Qx"
    "KnQ2LTIqdDMqdDgsdDEqdDMqdDgrdDIqdDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0Mip0Myp0NSt0MSp0NV4yLXQy"
    "KnQ0KnQ2LXQxKnQ2XjItMip0Myp0NS0yKnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3QxKnQzKnQ1K3QyKnQ1XjIrdDEq"
    "dDQqdDYtMip0Myp0NC0yKnQ0XjItMip0NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEqdDMqdDYrdDIqdDUqdDYtMip0"
    "Myp0NC0yKnQ0XjItMip0NSp0NisyKnQ2XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDheMyt0Ml4yLTQqdDIqdDgsdDYq"
    "dDdeMip0OC10Nip0OF4zLXQxKnQyKnQzLXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIrMyp0Nip0OF4yKzIqdDEqdDMr"
    "Mip0MSp0NCs0KnQyKnQ1LTIqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDheMy10MSp0Mip0NC10Ml4yKnQ2"
    "LXQ1KnQ3XjIrdDYqdDdeMiszKnQ1KnQ4XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0NSs0KnQyKnQ2KzIqdDUqdDgr"
    "Mip0Nip0OCx0NCp0N14yKnQ4LXQ0KnQ4XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3XjIrdDMqdDheMiszKnQ0KnQ4"
    "XjItNCp0Mip0My0yKnQyKnQ0LTIqdDEqdDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDdeMip0OC10Myp0OF4zK3QyXjIq"
    "dDQrdDEqdDIqdDYtdDMqdDdeMi10NCp0N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0Mip0NCsyKnQxKnQ1LTIqdDEq"
    "dDYrMip0Myp0OC0yKnQ0KnQ4O1xub3B0aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXItc2VjXCIsMTAwMCk7IGludCB0"
    "MD1ydGltZXI7XG5pZGVhbCBzPXNsaW1nYihKK21heGlkZWFsKDE1KSk7XG5cIlJFU1VMVCBtc1wiLHJ0aW1lci10MCxcInNiX3Np"
    "emVcIixuY29scyhzKTtcbmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixuY29scyhCKTtcbnNob3J0PTA7"
    "IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL29yZGVyLXJvdDQtbjE1L3MudHh0XCIscyk7IHdyaXRlKFwiOncgL2thZ2dsZS93"
    "b3JraW5nL29yZGVyLXJvdDQtbjE1L2tiYXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7Im5hbWUiOiAib3JkZXItcm90NS1uMTUi"
    "LCAic2NyaXB0IjogInJpbmcgcj0zMjAwOSwodDYsdDcsdDgsdDEsdDIsdDMsdDQsdDUpLGRwO1xuaWRlYWwgSj10M14yLXQ0XjIt"
    "dDVeMit0Nl4yLHQxXjItdDJeMit0N14yLXQ4XjIrNCp0MisyKnQ4LHQ0KnQ1KnQ4LXQzKnQ2KnQ4LXQzKnQ1LXQ0KnQ1K3QzKnQ2"
    "K3Q0KnQ2LHQ0XjIqdDgtdDZeMip0OC10Myp0NC10NF4yLXQ1KnQ2K3Q2XjIsdDMqdDQqdDgtdDUqdDYqdDgtdDMqdDQtdDReMi10"
    "NV4yK3Q1KnQ2LHQyKnQ0KnQ4K3QxKnQ2KnQ4LXQyKnQ0K3QxKnQ1LXQxKnQ2LTIqdDQqdDgsdDEqdDQqdDgrdDIqdDYqdDgtdDEq"
    "dDMtdDEqdDQtdDIqdDYtMip0Nip0OCx0Mip0Myp0OCt0MSp0NSp0OC10Mip0My10MSp0NSt0MSp0Ni0yKnQzKnQ4LHQxKnQzKnQ4"
    "K3QyKnQ1KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ1LTIqdDUqdDgsdDIqdDMqdDUrdDEqdDVeMi10Mip0NCp0Ni10MSp0Nl4yLTIqdDMq"
    "dDUtMip0NCp0NSsyKnQzKnQ2KzIqdDQqdDYsdDIqdDReMit0MSp0Myp0NSt0Mip0NV4yK3QxKnQ0KnQ2LTIqdDMqdDQtMip0NF4y"
    "LTIqdDVeMisyKnQ1KnQ2LHQyKnQzKnQ0K3QxKnQ0KnQ1K3QxKnQzKnQ2K3QyKnQ1KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDUqdDYr"
    "Mip0Nl4yLHQ3XjIqdDheMi10OF40LTIqdDdeMip0OCs0KnQ4XjMrdDJeMi00KnQyKnQ4LHQ2KnQ3XjIqdDgtdDYqdDheMy10MSp0"
    "Mip0My10Ml4yKnQ1K3Q1KnQ3XjItdDYqdDdeMi10NSp0OF4yKzMqdDYqdDheMisyKnQxKnQzKzIqdDEqdDQrNCp0Mip0NS0yKnQy"
    "KnQ2KzIqdDUqdDgrMip0Nip0OCx0NSp0N14yKnQ4LXQ1KnQ4XjMtdDEqdDIqdDQtdDJeMip0Ni10NSp0N14yK3Q2KnQ3XjIrMyp0"
    "NSp0OF4yLXQ2KnQ4XjIrMip0MSp0MysyKnQxKnQ0LTIqdDIqdDUrNCp0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDQqdDdeMip0OC10"
    "NCp0OF4zK3QyXjIqdDMrdDEqdDIqdDUtdDMqdDdeMi10NCp0N14yK3QzKnQ4XjIrMyp0NCp0OF4yLTQqdDIqdDMtMip0Mip0NC0y"
    "KnQxKnQ1KzIqdDEqdDYtMip0Myp0OCsyKnQ0KnQ4LHQzKnQ3XjIqdDgtdDMqdDheMyt0Ml4yKnQ0K3QxKnQyKnQ2LXQzKnQ3XjIt"
    "dDQqdDdeMiszKnQzKnQ4XjIrdDQqdDheMi0yKnQyKnQzLTQqdDIqdDQrMip0MSp0NS0yKnQxKnQ2KzIqdDMqdDgtMip0NCp0ODtc"
    "bm9wdGlvbihyZWRTQik7IHN5c3RlbShcIi0tdGlja3MtcGVyLXNlY1wiLDEwMDApOyBpbnQgdDA9cnRpbWVyO1xuaWRlYWwgcz1z"
    "bGltZ2IoSittYXhpZGVhbCgxNSkpO1xuXCJSRVNVTFQgbXNcIixydGltZXItdDAsXCJzYl9zaXplXCIsbmNvbHMocyk7XG5pZGVh"
    "bCBCPWtiYXNlKHMpOyBcIlJFU1VMVCBrYmFzZV9zaXplXCIsbmNvbHMoQik7XG5zaG9ydD0wOyB3cml0ZShcIjp3IC9rYWdnbGUv"
    "d29ya2luZy9vcmRlci1yb3Q1LW4xNS9zLnR4dFwiLHMpOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9vcmRlci1yb3Q1LW4x"
    "NS9rYmFzZS50eHRcIixCKTtcbnF1aXQ7XG4ifSwgeyJuYW1lIjogIm9yZGVyLXJvdDYtbjE1IiwgInNjcmlwdCI6ICJyaW5nIHI9"
    "MzIwMDksKHQ3LHQ4LHQxLHQyLHQzLHQ0LHQ1LHQ2KSxkcDtcbmlkZWFsIEo9dDNeMi10NF4yLXQ1XjIrdDZeMix0MV4yLXQyXjIr"
    "dDdeMi10OF4yKzQqdDIrMip0OCx0NCp0NSp0OC10Myp0Nip0OC10Myp0NS10NCp0NSt0Myp0Nit0NCp0Nix0NF4yKnQ4LXQ2XjIq"
    "dDgtdDMqdDQtdDReMi10NSp0Nit0Nl4yLHQzKnQ0KnQ4LXQ1KnQ2KnQ4LXQzKnQ0LXQ0XjItdDVeMit0NSp0Nix0Mip0NCp0OCt0"
    "MSp0Nip0OC10Mip0NCt0MSp0NS10MSp0Ni0yKnQ0KnQ4LHQxKnQ0KnQ4K3QyKnQ2KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ2LTIqdDYq"
    "dDgsdDIqdDMqdDgrdDEqdDUqdDgtdDIqdDMtdDEqdDUrdDEqdDYtMip0Myp0OCx0MSp0Myp0OCt0Mip0NSp0OC10MSp0My10MSp0"
    "NC10Mip0NS0yKnQ1KnQ4LHQyKnQzKnQ1K3QxKnQ1XjItdDIqdDQqdDYtdDEqdDZeMi0yKnQzKnQ1LTIqdDQqdDUrMip0Myp0Nisy"
    "KnQ0KnQ2LHQyKnQ0XjIrdDEqdDMqdDUrdDIqdDVeMit0MSp0NCp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1XjIrMip0NSp0Nix0Mip0"
    "Myp0NCt0MSp0NCp0NSt0MSp0Myp0Nit0Mip0NSp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1KnQ2KzIqdDZeMix0N14yKnQ4XjItdDhe"
    "NC0yKnQ3XjIqdDgrNCp0OF4zK3QyXjItNCp0Mip0OCx0Nip0N14yKnQ4LXQ2KnQ4XjMtdDEqdDIqdDMtdDJeMip0NSt0NSp0N14y"
    "LXQ2KnQ3XjItdDUqdDheMiszKnQ2KnQ4XjIrMip0MSp0MysyKnQxKnQ0KzQqdDIqdDUtMip0Mip0NisyKnQ1KnQ4KzIqdDYqdDgs"
    "dDUqdDdeMip0OC10NSp0OF4zLXQxKnQyKnQ0LXQyXjIqdDYtdDUqdDdeMit0Nip0N14yKzMqdDUqdDheMi10Nip0OF4yKzIqdDEq"
    "dDMrMip0MSp0NC0yKnQyKnQ1KzQqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ0KnQ3XjIqdDgtdDQqdDheMyt0Ml4yKnQzK3QxKnQy"
    "KnQ1LXQzKnQ3XjItdDQqdDdeMit0Myp0OF4yKzMqdDQqdDheMi00KnQyKnQzLTIqdDIqdDQtMip0MSp0NSsyKnQxKnQ2LTIqdDMq"
    "dDgrMip0NCp0OCx0Myp0N14yKnQ4LXQzKnQ4XjMrdDJeMip0NCt0MSp0Mip0Ni10Myp0N14yLXQ0KnQ3XjIrMyp0Myp0OF4yK3Q0"
    "KnQ4XjItMip0Mip0My00KnQyKnQ0KzIqdDEqdDUtMip0MSp0NisyKnQzKnQ4LTIqdDQqdDg7XG5vcHRpb24ocmVkU0IpOyBzeXN0"
    "ZW0oXCItLXRpY2tzLXBlci1zZWNcIiwxMDAwKTsgaW50IHQwPXJ0aW1lcjtcbmlkZWFsIHM9c2xpbWdiKEorbWF4aWRlYWwoMTUp"
    "KTtcblwiUkVTVUxUIG1zXCIscnRpbWVyLXQwLFwic2Jfc2l6ZVwiLG5jb2xzKHMpO1xuaWRlYWwgQj1rYmFzZShzKTsgXCJSRVNV"
    "TFQga2Jhc2Vfc2l6ZVwiLG5jb2xzKEIpO1xuc2hvcnQ9MDsgd3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90Ni1u"
    "MTUvcy50eHRcIixzKTsgd3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90Ni1uMTUva2Jhc2UudHh0XCIsQik7XG5x"
    "dWl0O1xuIn1dLCAiam9iX3NlY29uZHMiOiA0MTAwMH0="
)
OUT = Path("/kaggle/working")
DIGESTS = ("s.txt", "kbase.txt")
SESSION_SECONDS = 12 * 3600 - 1200


def failures(jobs: dict[str, dict[str, Any]]) -> list[str]:
    """Jobs that did not finish: a nonzero exit (124 for the deadline), no RESULT line (Singular exits 0 on
    SIGTERM), or a missing output digest."""
    return [
        name
        for name, job in jobs.items()
        if job["rc"] != 0 or not job["results"] or any(f not in job["sha256"] for f in DIGESTS)
    ]


def _singular() -> Path:
    paths = sysconfig.get_paths()
    candidates = (Path(paths[key]) / "sage_wheels" / "bin" / "Singular" for key in ("purelib", "platlib"))
    return next(path for path in candidates if path.exists())


def _seconds_left(started: float, seconds: int) -> int:
    """The job deadline: its own limit, cut to the session time left (at least 1 s, so `timeout` ends it at once)."""
    return max(1, min(seconds, int(SESSION_SECONDS - (time.time() - started))))


def _run(binary: Path, seconds: int, job: dict[str, str]) -> tuple[str, dict[str, Any]]:
    work = OUT / job["name"]
    work.mkdir(parents=True, exist_ok=True)
    (work / "input.sing").write_text(job["script"])
    start = time.time()
    command = ["timeout", "-k", "30", str(seconds), str(binary), "-q", "--no-rc", "input.sing"]
    done = subprocess.run(command, cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
    (work / "out.log").write_text(done.stdout + done.stderr)
    digests = {f: hashlib.sha256((work / f).read_bytes()).hexdigest() for f in DIGESTS if (work / f).exists()}
    results = [line for line in done.stdout.splitlines() if line.startswith("RESULT")]
    record = {"rc": done.returncode, "seconds": round(time.time() - start, 1), "sha256": digests, "results": results}
    return job["name"], record


def main() -> None:
    config = json.loads(base64.b64decode(CONFIG_B64))
    started = time.time()
    install = [sys.executable, "-m", "pip", "install", "-q", "passagemath-singular==10.8.13"]
    subprocess.run(install, check=True)
    binary = _singular()
    version = subprocess.run(
        [str(binary), "--dump-versiontuple"], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False
    )
    jobs: dict[str, dict[str, Any]] = {}
    lock = threading.Lock()

    def write() -> dict[str, object]:
        summary: dict[str, object] = {
            "cpu_count": os.cpu_count(),
            "singular": version.stdout.strip(),
            "jobs": dict(jobs),
            "pending": [job["name"] for job in config["jobs"] if job["name"] not in jobs],
            "failed": failures(jobs),
            "total_seconds": round(time.time() - started, 1),
        }
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
        return summary

    def one(job: dict[str, str]) -> None:
        name, record = _run(binary, _seconds_left(started, config["job_seconds"]), job)
        with lock:
            jobs[name] = record
            write()

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(one, config["jobs"]))
    summary = write()
    print(json.dumps(summary, indent=1))
    if summary["failed"] or summary["pending"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
