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
    "eyJqb2JzIjogW3sibmFtZSI6ICJzbGltZ2ItbjIyLXAzMjAwOSIsICJzY3JpcHQiOiAicmluZyByPTMyMDA5LCh0MSx0Mix0Myx0"
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
    "c2VjXCIsMTAwMCk7IGludCB0MD1ydGltZXI7XG5pZGVhbCBzPXNsaW1nYihKK21heGlkZWFsKDIyKSk7XG5cIlJFU1VMVCBtc1wi"
    "LHJ0aW1lci10MCxcInNiX3NpemVcIixuY29scyhzKTtcbmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixu"
    "Y29scyhCKTtcbnNob3J0PTA7IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL3NsaW1nYi1uMjItcDMyMDA5L3MudHh0XCIscyk7"
    "IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL3NsaW1nYi1uMjItcDMyMDA5L2tiYXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7"
    "Im5hbWUiOiAib3JkZXItaWRlbnRpdHktbjE1IiwgInNjcmlwdCI6ICJyaW5nIHI9MzIwMDksKHQxLHQyLHQzLHQ0LHQ1LHQ2LHQ3"
    "LHQ4KSxkcDtcbmlkZWFsIEo9dDNeMi10NF4yLXQ1XjIrdDZeMix0MV4yLXQyXjIrdDdeMi10OF4yKzQqdDIrMip0OCx0NCp0NSp0"
    "OC10Myp0Nip0OC10Myp0NS10NCp0NSt0Myp0Nit0NCp0Nix0NF4yKnQ4LXQ2XjIqdDgtdDMqdDQtdDReMi10NSp0Nit0Nl4yLHQz"
    "KnQ0KnQ4LXQ1KnQ2KnQ4LXQzKnQ0LXQ0XjItdDVeMit0NSp0Nix0Mip0NCp0OCt0MSp0Nip0OC10Mip0NCt0MSp0NS10MSp0Ni0y"
    "KnQ0KnQ4LHQxKnQ0KnQ4K3QyKnQ2KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ2LTIqdDYqdDgsdDIqdDMqdDgrdDEqdDUqdDgtdDIqdDMt"
    "dDEqdDUrdDEqdDYtMip0Myp0OCx0MSp0Myp0OCt0Mip0NSp0OC10MSp0My10MSp0NC10Mip0NS0yKnQ1KnQ4LHQyKnQzKnQ1K3Qx"
    "KnQ1XjItdDIqdDQqdDYtdDEqdDZeMi0yKnQzKnQ1LTIqdDQqdDUrMip0Myp0NisyKnQ0KnQ2LHQyKnQ0XjIrdDEqdDMqdDUrdDIq"
    "dDVeMit0MSp0NCp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1XjIrMip0NSp0Nix0Mip0Myp0NCt0MSp0NCp0NSt0MSp0Myp0Nit0Mip0"
    "NSp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1KnQ2KzIqdDZeMix0N14yKnQ4XjItdDheNC0yKnQ3XjIqdDgrNCp0OF4zK3QyXjItNCp0"
    "Mip0OCx0Nip0N14yKnQ4LXQ2KnQ4XjMtdDEqdDIqdDMtdDJeMip0NSt0NSp0N14yLXQ2KnQ3XjItdDUqdDheMiszKnQ2KnQ4XjIr"
    "Mip0MSp0MysyKnQxKnQ0KzQqdDIqdDUtMip0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDUqdDdeMip0OC10NSp0OF4zLXQxKnQyKnQ0"
    "LXQyXjIqdDYtdDUqdDdeMit0Nip0N14yKzMqdDUqdDheMi10Nip0OF4yKzIqdDEqdDMrMip0MSp0NC0yKnQyKnQ1KzQqdDIqdDYr"
    "Mip0NSp0OCsyKnQ2KnQ4LHQ0KnQ3XjIqdDgtdDQqdDheMyt0Ml4yKnQzK3QxKnQyKnQ1LXQzKnQ3XjItdDQqdDdeMit0Myp0OF4y"
    "KzMqdDQqdDheMi00KnQyKnQzLTIqdDIqdDQtMip0MSp0NSsyKnQxKnQ2LTIqdDMqdDgrMip0NCp0OCx0Myp0N14yKnQ4LXQzKnQ4"
    "XjMrdDJeMip0NCt0MSp0Mip0Ni10Myp0N14yLXQ0KnQ3XjIrMyp0Myp0OF4yK3Q0KnQ4XjItMip0Mip0My00KnQyKnQ0KzIqdDEq"
    "dDUtMip0MSp0NisyKnQzKnQ4LTIqdDQqdDg7XG5vcHRpb24ocmVkU0IpOyBzeXN0ZW0oXCItLXRpY2tzLXBlci1zZWNcIiwxMDAw"
    "KTsgaW50IHQwPXJ0aW1lcjtcbmlkZWFsIHM9c2xpbWdiKEorbWF4aWRlYWwoMTUpKTtcblwiUkVTVUxUIG1zXCIscnRpbWVyLXQw"
    "LFwic2Jfc2l6ZVwiLG5jb2xzKHMpO1xuaWRlYWwgQj1rYmFzZShzKTsgXCJSRVNVTFQga2Jhc2Vfc2l6ZVwiLG5jb2xzKEIpO1xu"
    "c2hvcnQ9MDsgd3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItaWRlbnRpdHktbjE1L3MudHh0XCIscyk7IHdyaXRlKFwi"
    "OncgL2thZ2dsZS93b3JraW5nL29yZGVyLWlkZW50aXR5LW4xNS9rYmFzZS50eHRcIixCKTtcbnF1aXQ7XG4ifSwgeyJuYW1lIjog"
    "Im9yZGVyLXJvdDEtbjE1IiwgInNjcmlwdCI6ICJyaW5nIHI9MzIwMDksKHQyLHQzLHQ0LHQ1LHQ2LHQ3LHQ4LHQxKSxkcDtcbmlk"
    "ZWFsIEo9dDNeMi10NF4yLXQ1XjIrdDZeMix0MV4yLXQyXjIrdDdeMi10OF4yKzQqdDIrMip0OCx0NCp0NSp0OC10Myp0Nip0OC10"
    "Myp0NS10NCp0NSt0Myp0Nit0NCp0Nix0NF4yKnQ4LXQ2XjIqdDgtdDMqdDQtdDReMi10NSp0Nit0Nl4yLHQzKnQ0KnQ4LXQ1KnQ2"
    "KnQ4LXQzKnQ0LXQ0XjItdDVeMit0NSp0Nix0Mip0NCp0OCt0MSp0Nip0OC10Mip0NCt0MSp0NS10MSp0Ni0yKnQ0KnQ4LHQxKnQ0"
    "KnQ4K3QyKnQ2KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ2LTIqdDYqdDgsdDIqdDMqdDgrdDEqdDUqdDgtdDIqdDMtdDEqdDUrdDEqdDYt"
    "Mip0Myp0OCx0MSp0Myp0OCt0Mip0NSp0OC10MSp0My10MSp0NC10Mip0NS0yKnQ1KnQ4LHQyKnQzKnQ1K3QxKnQ1XjItdDIqdDQq"
    "dDYtdDEqdDZeMi0yKnQzKnQ1LTIqdDQqdDUrMip0Myp0NisyKnQ0KnQ2LHQyKnQ0XjIrdDEqdDMqdDUrdDIqdDVeMit0MSp0NCp0"
    "Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1XjIrMip0NSp0Nix0Mip0Myp0NCt0MSp0NCp0NSt0MSp0Myp0Nit0Mip0NSp0Ni0yKnQzKnQ0"
    "LTIqdDReMi0yKnQ1KnQ2KzIqdDZeMix0N14yKnQ4XjItdDheNC0yKnQ3XjIqdDgrNCp0OF4zK3QyXjItNCp0Mip0OCx0Nip0N14y"
    "KnQ4LXQ2KnQ4XjMtdDEqdDIqdDMtdDJeMip0NSt0NSp0N14yLXQ2KnQ3XjItdDUqdDheMiszKnQ2KnQ4XjIrMip0MSp0MysyKnQx"
    "KnQ0KzQqdDIqdDUtMip0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDUqdDdeMip0OC10NSp0OF4zLXQxKnQyKnQ0LXQyXjIqdDYtdDUq"
    "dDdeMit0Nip0N14yKzMqdDUqdDheMi10Nip0OF4yKzIqdDEqdDMrMip0MSp0NC0yKnQyKnQ1KzQqdDIqdDYrMip0NSp0OCsyKnQ2"
    "KnQ4LHQ0KnQ3XjIqdDgtdDQqdDheMyt0Ml4yKnQzK3QxKnQyKnQ1LXQzKnQ3XjItdDQqdDdeMit0Myp0OF4yKzMqdDQqdDheMi00"
    "KnQyKnQzLTIqdDIqdDQtMip0MSp0NSsyKnQxKnQ2LTIqdDMqdDgrMip0NCp0OCx0Myp0N14yKnQ4LXQzKnQ4XjMrdDJeMip0NCt0"
    "MSp0Mip0Ni10Myp0N14yLXQ0KnQ3XjIrMyp0Myp0OF4yK3Q0KnQ4XjItMip0Mip0My00KnQyKnQ0KzIqdDEqdDUtMip0MSp0Nisy"
    "KnQzKnQ4LTIqdDQqdDg7XG5vcHRpb24ocmVkU0IpOyBzeXN0ZW0oXCItLXRpY2tzLXBlci1zZWNcIiwxMDAwKTsgaW50IHQwPXJ0"
    "aW1lcjtcbmlkZWFsIHM9c2xpbWdiKEorbWF4aWRlYWwoMTUpKTtcblwiUkVTVUxUIG1zXCIscnRpbWVyLXQwLFwic2Jfc2l6ZVwi"
    "LG5jb2xzKHMpO1xuaWRlYWwgQj1rYmFzZShzKTsgXCJSRVNVTFQga2Jhc2Vfc2l6ZVwiLG5jb2xzKEIpO1xuc2hvcnQ9MDsgd3Jp"
    "dGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90MS1uMTUvcy50eHRcIixzKTsgd3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtp"
    "bmcvb3JkZXItcm90MS1uMTUva2Jhc2UudHh0XCIsQik7XG5xdWl0O1xuIn0sIHsibmFtZSI6ICJvcmRlci1yb3QyLW4xNSIsICJz"
    "Y3JpcHQiOiAicmluZyByPTMyMDA5LCh0Myx0NCx0NSx0Nix0Nyx0OCx0MSx0MiksZHA7XG5pZGVhbCBKPXQzXjItdDReMi10NV4y"
    "K3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIqdDgsdDQqdDUqdDgtdDMqdDYqdDgtdDMqdDUtdDQqdDUrdDMqdDYrdDQq"
    "dDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUqdDYrdDZeMix0Myp0NCp0OC10NSp0Nip0OC10Myp0NC10NF4yLXQ1XjIr"
    "dDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEqdDUtdDEqdDYtMip0NCp0OCx0MSp0NCp0OCt0Mip0Nip0OC10MSp0My10"
    "MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1KnQ4LXQyKnQzLXQxKnQ1K3QxKnQ2LTIqdDMqdDgsdDEqdDMqdDgrdDIq"
    "dDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0Mip0Myp0NSt0MSp0NV4yLXQyKnQ0KnQ2LXQxKnQ2XjItMip0Myp0NS0y"
    "KnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3QxKnQzKnQ1K3QyKnQ1XjIrdDEqdDQqdDYtMip0Myp0NC0yKnQ0XjItMip0"
    "NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEqdDMqdDYrdDIqdDUqdDYtMip0Myp0NC0yKnQ0XjItMip0NSp0NisyKnQ2"
    "XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDheMyt0Ml4yLTQqdDIqdDgsdDYqdDdeMip0OC10Nip0OF4zLXQxKnQyKnQz"
    "LXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIrMyp0Nip0OF4yKzIqdDEqdDMrMip0MSp0NCs0KnQyKnQ1LTIqdDIqdDYr"
    "Mip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDheMy10MSp0Mip0NC10Ml4yKnQ2LXQ1KnQ3XjIrdDYqdDdeMiszKnQ1KnQ4"
    "XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0NSs0KnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NCp0N14yKnQ4LXQ0KnQ4"
    "XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3XjIrdDMqdDheMiszKnQ0KnQ4XjItNCp0Mip0My0yKnQyKnQ0LTIqdDEq"
    "dDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDdeMip0OC10Myp0OF4zK3QyXjIqdDQrdDEqdDIqdDYtdDMqdDdeMi10NCp0"
    "N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0Mip0NCsyKnQxKnQ1LTIqdDEqdDYrMip0Myp0OC0yKnQ0KnQ4O1xub3B0"
    "aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXItc2VjXCIsMTAwMCk7IGludCB0MD1ydGltZXI7XG5pZGVhbCBzPXNsaW1n"
    "YihKK21heGlkZWFsKDE1KSk7XG5cIlJFU1VMVCBtc1wiLHJ0aW1lci10MCxcInNiX3NpemVcIixuY29scyhzKTtcbmlkZWFsIEI9"
    "a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixuY29scyhCKTtcbnNob3J0PTA7IHdyaXRlKFwiOncgL2thZ2dsZS93b3Jr"
    "aW5nL29yZGVyLXJvdDItbjE1L3MudHh0XCIscyk7IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL29yZGVyLXJvdDItbjE1L2ti"
    "YXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7Im5hbWUiOiAib3JkZXItcm90My1uMTUiLCAic2NyaXB0IjogInJpbmcgcj0zMjAw"
    "OSwodDQsdDUsdDYsdDcsdDgsdDEsdDIsdDMpLGRwO1xuaWRlYWwgSj10M14yLXQ0XjItdDVeMit0Nl4yLHQxXjItdDJeMit0N14y"
    "LXQ4XjIrNCp0MisyKnQ4LHQ0KnQ1KnQ4LXQzKnQ2KnQ4LXQzKnQ1LXQ0KnQ1K3QzKnQ2K3Q0KnQ2LHQ0XjIqdDgtdDZeMip0OC10"
    "Myp0NC10NF4yLXQ1KnQ2K3Q2XjIsdDMqdDQqdDgtdDUqdDYqdDgtdDMqdDQtdDReMi10NV4yK3Q1KnQ2LHQyKnQ0KnQ4K3QxKnQ2"
    "KnQ4LXQyKnQ0K3QxKnQ1LXQxKnQ2LTIqdDQqdDgsdDEqdDQqdDgrdDIqdDYqdDgtdDEqdDMtdDEqdDQtdDIqdDYtMip0Nip0OCx0"
    "Mip0Myp0OCt0MSp0NSp0OC10Mip0My10MSp0NSt0MSp0Ni0yKnQzKnQ4LHQxKnQzKnQ4K3QyKnQ1KnQ4LXQxKnQzLXQxKnQ0LXQy"
    "KnQ1LTIqdDUqdDgsdDIqdDMqdDUrdDEqdDVeMi10Mip0NCp0Ni10MSp0Nl4yLTIqdDMqdDUtMip0NCp0NSsyKnQzKnQ2KzIqdDQq"
    "dDYsdDIqdDReMit0MSp0Myp0NSt0Mip0NV4yK3QxKnQ0KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDVeMisyKnQ1KnQ2LHQyKnQzKnQ0"
    "K3QxKnQ0KnQ1K3QxKnQzKnQ2K3QyKnQ1KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDUqdDYrMip0Nl4yLHQ3XjIqdDheMi10OF40LTIq"
    "dDdeMip0OCs0KnQ4XjMrdDJeMi00KnQyKnQ4LHQ2KnQ3XjIqdDgtdDYqdDheMy10MSp0Mip0My10Ml4yKnQ1K3Q1KnQ3XjItdDYq"
    "dDdeMi10NSp0OF4yKzMqdDYqdDheMisyKnQxKnQzKzIqdDEqdDQrNCp0Mip0NS0yKnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0NSp0"
    "N14yKnQ4LXQ1KnQ4XjMtdDEqdDIqdDQtdDJeMip0Ni10NSp0N14yK3Q2KnQ3XjIrMyp0NSp0OF4yLXQ2KnQ4XjIrMip0MSp0Mysy"
    "KnQxKnQ0LTIqdDIqdDUrNCp0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDQqdDdeMip0OC10NCp0OF4zK3QyXjIqdDMrdDEqdDIqdDUt"
    "dDMqdDdeMi10NCp0N14yK3QzKnQ4XjIrMyp0NCp0OF4yLTQqdDIqdDMtMip0Mip0NC0yKnQxKnQ1KzIqdDEqdDYtMip0Myp0OCsy"
    "KnQ0KnQ4LHQzKnQ3XjIqdDgtdDMqdDheMyt0Ml4yKnQ0K3QxKnQyKnQ2LXQzKnQ3XjItdDQqdDdeMiszKnQzKnQ4XjIrdDQqdDhe"
    "Mi0yKnQyKnQzLTQqdDIqdDQrMip0MSp0NS0yKnQxKnQ2KzIqdDMqdDgtMip0NCp0ODtcbm9wdGlvbihyZWRTQik7IHN5c3RlbShc"
    "Ii0tdGlja3MtcGVyLXNlY1wiLDEwMDApOyBpbnQgdDA9cnRpbWVyO1xuaWRlYWwgcz1zbGltZ2IoSittYXhpZGVhbCgxNSkpO1xu"
    "XCJSRVNVTFQgbXNcIixydGltZXItdDAsXCJzYl9zaXplXCIsbmNvbHMocyk7XG5pZGVhbCBCPWtiYXNlKHMpOyBcIlJFU1VMVCBr"
    "YmFzZV9zaXplXCIsbmNvbHMoQik7XG5zaG9ydD0wOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9vcmRlci1yb3QzLW4xNS9z"
    "LnR4dFwiLHMpOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9vcmRlci1yb3QzLW4xNS9rYmFzZS50eHRcIixCKTtcbnF1aXQ7"
    "XG4ifSwgeyJuYW1lIjogIm9yZGVyLXJvdDQtbjE1IiwgInNjcmlwdCI6ICJyaW5nIHI9MzIwMDksKHQ1LHQ2LHQ3LHQ4LHQxLHQy"
    "LHQzLHQ0KSxkcDtcbmlkZWFsIEo9dDNeMi10NF4yLXQ1XjIrdDZeMix0MV4yLXQyXjIrdDdeMi10OF4yKzQqdDIrMip0OCx0NCp0"
    "NSp0OC10Myp0Nip0OC10Myp0NS10NCp0NSt0Myp0Nit0NCp0Nix0NF4yKnQ4LXQ2XjIqdDgtdDMqdDQtdDReMi10NSp0Nit0Nl4y"
    "LHQzKnQ0KnQ4LXQ1KnQ2KnQ4LXQzKnQ0LXQ0XjItdDVeMit0NSp0Nix0Mip0NCp0OCt0MSp0Nip0OC10Mip0NCt0MSp0NS10MSp0"
    "Ni0yKnQ0KnQ4LHQxKnQ0KnQ4K3QyKnQ2KnQ4LXQxKnQzLXQxKnQ0LXQyKnQ2LTIqdDYqdDgsdDIqdDMqdDgrdDEqdDUqdDgtdDIq"
    "dDMtdDEqdDUrdDEqdDYtMip0Myp0OCx0MSp0Myp0OCt0Mip0NSp0OC10MSp0My10MSp0NC10Mip0NS0yKnQ1KnQ4LHQyKnQzKnQ1"
    "K3QxKnQ1XjItdDIqdDQqdDYtdDEqdDZeMi0yKnQzKnQ1LTIqdDQqdDUrMip0Myp0NisyKnQ0KnQ2LHQyKnQ0XjIrdDEqdDMqdDUr"
    "dDIqdDVeMit0MSp0NCp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1XjIrMip0NSp0Nix0Mip0Myp0NCt0MSp0NCp0NSt0MSp0Myp0Nit0"
    "Mip0NSp0Ni0yKnQzKnQ0LTIqdDReMi0yKnQ1KnQ2KzIqdDZeMix0N14yKnQ4XjItdDheNC0yKnQ3XjIqdDgrNCp0OF4zK3QyXjIt"
    "NCp0Mip0OCx0Nip0N14yKnQ4LXQ2KnQ4XjMtdDEqdDIqdDMtdDJeMip0NSt0NSp0N14yLXQ2KnQ3XjItdDUqdDheMiszKnQ2KnQ4"
    "XjIrMip0MSp0MysyKnQxKnQ0KzQqdDIqdDUtMip0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDUqdDdeMip0OC10NSp0OF4zLXQxKnQy"
    "KnQ0LXQyXjIqdDYtdDUqdDdeMit0Nip0N14yKzMqdDUqdDheMi10Nip0OF4yKzIqdDEqdDMrMip0MSp0NC0yKnQyKnQ1KzQqdDIq"
    "dDYrMip0NSp0OCsyKnQ2KnQ4LHQ0KnQ3XjIqdDgtdDQqdDheMyt0Ml4yKnQzK3QxKnQyKnQ1LXQzKnQ3XjItdDQqdDdeMit0Myp0"
    "OF4yKzMqdDQqdDheMi00KnQyKnQzLTIqdDIqdDQtMip0MSp0NSsyKnQxKnQ2LTIqdDMqdDgrMip0NCp0OCx0Myp0N14yKnQ4LXQz"
    "KnQ4XjMrdDJeMip0NCt0MSp0Mip0Ni10Myp0N14yLXQ0KnQ3XjIrMyp0Myp0OF4yK3Q0KnQ4XjItMip0Mip0My00KnQyKnQ0KzIq"
    "dDEqdDUtMip0MSp0NisyKnQzKnQ4LTIqdDQqdDg7XG5vcHRpb24ocmVkU0IpOyBzeXN0ZW0oXCItLXRpY2tzLXBlci1zZWNcIiwx"
    "MDAwKTsgaW50IHQwPXJ0aW1lcjtcbmlkZWFsIHM9c2xpbWdiKEorbWF4aWRlYWwoMTUpKTtcblwiUkVTVUxUIG1zXCIscnRpbWVy"
    "LXQwLFwic2Jfc2l6ZVwiLG5jb2xzKHMpO1xuaWRlYWwgQj1rYmFzZShzKTsgXCJSRVNVTFQga2Jhc2Vfc2l6ZVwiLG5jb2xzKEIp"
    "O1xuc2hvcnQ9MDsgd3JpdGUoXCI6dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90NC1uMTUvcy50eHRcIixzKTsgd3JpdGUoXCI6"
    "dyAva2FnZ2xlL3dvcmtpbmcvb3JkZXItcm90NC1uMTUva2Jhc2UudHh0XCIsQik7XG5xdWl0O1xuIn0sIHsibmFtZSI6ICJvcmRl"
    "ci1yb3Q1LW4xNSIsICJzY3JpcHQiOiAicmluZyByPTMyMDA5LCh0Nix0Nyx0OCx0MSx0Mix0Myx0NCx0NSksZHA7XG5pZGVhbCBK"
    "PXQzXjItdDReMi10NV4yK3Q2XjIsdDFeMi10Ml4yK3Q3XjItdDheMis0KnQyKzIqdDgsdDQqdDUqdDgtdDMqdDYqdDgtdDMqdDUt"
    "dDQqdDUrdDMqdDYrdDQqdDYsdDReMip0OC10Nl4yKnQ4LXQzKnQ0LXQ0XjItdDUqdDYrdDZeMix0Myp0NCp0OC10NSp0Nip0OC10"
    "Myp0NC10NF4yLXQ1XjIrdDUqdDYsdDIqdDQqdDgrdDEqdDYqdDgtdDIqdDQrdDEqdDUtdDEqdDYtMip0NCp0OCx0MSp0NCp0OCt0"
    "Mip0Nip0OC10MSp0My10MSp0NC10Mip0Ni0yKnQ2KnQ4LHQyKnQzKnQ4K3QxKnQ1KnQ4LXQyKnQzLXQxKnQ1K3QxKnQ2LTIqdDMq"
    "dDgsdDEqdDMqdDgrdDIqdDUqdDgtdDEqdDMtdDEqdDQtdDIqdDUtMip0NSp0OCx0Mip0Myp0NSt0MSp0NV4yLXQyKnQ0KnQ2LXQx"
    "KnQ2XjItMip0Myp0NS0yKnQ0KnQ1KzIqdDMqdDYrMip0NCp0Nix0Mip0NF4yK3QxKnQzKnQ1K3QyKnQ1XjIrdDEqdDQqdDYtMip0"
    "Myp0NC0yKnQ0XjItMip0NV4yKzIqdDUqdDYsdDIqdDMqdDQrdDEqdDQqdDUrdDEqdDMqdDYrdDIqdDUqdDYtMip0Myp0NC0yKnQ0"
    "XjItMip0NSp0NisyKnQ2XjIsdDdeMip0OF4yLXQ4XjQtMip0N14yKnQ4KzQqdDheMyt0Ml4yLTQqdDIqdDgsdDYqdDdeMip0OC10"
    "Nip0OF4zLXQxKnQyKnQzLXQyXjIqdDUrdDUqdDdeMi10Nip0N14yLXQ1KnQ4XjIrMyp0Nip0OF4yKzIqdDEqdDMrMip0MSp0NCs0"
    "KnQyKnQ1LTIqdDIqdDYrMip0NSp0OCsyKnQ2KnQ4LHQ1KnQ3XjIqdDgtdDUqdDheMy10MSp0Mip0NC10Ml4yKnQ2LXQ1KnQ3XjIr"
    "dDYqdDdeMiszKnQ1KnQ4XjItdDYqdDheMisyKnQxKnQzKzIqdDEqdDQtMip0Mip0NSs0KnQyKnQ2KzIqdDUqdDgrMip0Nip0OCx0"
    "NCp0N14yKnQ4LXQ0KnQ4XjMrdDJeMip0Myt0MSp0Mip0NS10Myp0N14yLXQ0KnQ3XjIrdDMqdDheMiszKnQ0KnQ4XjItNCp0Mip0"
    "My0yKnQyKnQ0LTIqdDEqdDUrMip0MSp0Ni0yKnQzKnQ4KzIqdDQqdDgsdDMqdDdeMip0OC10Myp0OF4zK3QyXjIqdDQrdDEqdDIq"
    "dDYtdDMqdDdeMi10NCp0N14yKzMqdDMqdDheMit0NCp0OF4yLTIqdDIqdDMtNCp0Mip0NCsyKnQxKnQ1LTIqdDEqdDYrMip0Myp0"
    "OC0yKnQ0KnQ4O1xub3B0aW9uKHJlZFNCKTsgc3lzdGVtKFwiLS10aWNrcy1wZXItc2VjXCIsMTAwMCk7IGludCB0MD1ydGltZXI7"
    "XG5pZGVhbCBzPXNsaW1nYihKK21heGlkZWFsKDE1KSk7XG5cIlJFU1VMVCBtc1wiLHJ0aW1lci10MCxcInNiX3NpemVcIixuY29s"
    "cyhzKTtcbmlkZWFsIEI9a2Jhc2Uocyk7IFwiUkVTVUxUIGtiYXNlX3NpemVcIixuY29scyhCKTtcbnNob3J0PTA7IHdyaXRlKFwi"
    "OncgL2thZ2dsZS93b3JraW5nL29yZGVyLXJvdDUtbjE1L3MudHh0XCIscyk7IHdyaXRlKFwiOncgL2thZ2dsZS93b3JraW5nL29y"
    "ZGVyLXJvdDUtbjE1L2tiYXNlLnR4dFwiLEIpO1xucXVpdDtcbiJ9LCB7Im5hbWUiOiAib3JkZXItcm90Ni1uMTUiLCAic2NyaXB0"
    "IjogInJpbmcgcj0zMjAwOSwodDcsdDgsdDEsdDIsdDMsdDQsdDUsdDYpLGRwO1xuaWRlYWwgSj10M14yLXQ0XjItdDVeMit0Nl4y"
    "LHQxXjItdDJeMit0N14yLXQ4XjIrNCp0MisyKnQ4LHQ0KnQ1KnQ4LXQzKnQ2KnQ4LXQzKnQ1LXQ0KnQ1K3QzKnQ2K3Q0KnQ2LHQ0"
    "XjIqdDgtdDZeMip0OC10Myp0NC10NF4yLXQ1KnQ2K3Q2XjIsdDMqdDQqdDgtdDUqdDYqdDgtdDMqdDQtdDReMi10NV4yK3Q1KnQ2"
    "LHQyKnQ0KnQ4K3QxKnQ2KnQ4LXQyKnQ0K3QxKnQ1LXQxKnQ2LTIqdDQqdDgsdDEqdDQqdDgrdDIqdDYqdDgtdDEqdDMtdDEqdDQt"
    "dDIqdDYtMip0Nip0OCx0Mip0Myp0OCt0MSp0NSp0OC10Mip0My10MSp0NSt0MSp0Ni0yKnQzKnQ4LHQxKnQzKnQ4K3QyKnQ1KnQ4"
    "LXQxKnQzLXQxKnQ0LXQyKnQ1LTIqdDUqdDgsdDIqdDMqdDUrdDEqdDVeMi10Mip0NCp0Ni10MSp0Nl4yLTIqdDMqdDUtMip0NCp0"
    "NSsyKnQzKnQ2KzIqdDQqdDYsdDIqdDReMit0MSp0Myp0NSt0Mip0NV4yK3QxKnQ0KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDVeMisy"
    "KnQ1KnQ2LHQyKnQzKnQ0K3QxKnQ0KnQ1K3QxKnQzKnQ2K3QyKnQ1KnQ2LTIqdDMqdDQtMip0NF4yLTIqdDUqdDYrMip0Nl4yLHQ3"
    "XjIqdDheMi10OF40LTIqdDdeMip0OCs0KnQ4XjMrdDJeMi00KnQyKnQ4LHQ2KnQ3XjIqdDgtdDYqdDheMy10MSp0Mip0My10Ml4y"
    "KnQ1K3Q1KnQ3XjItdDYqdDdeMi10NSp0OF4yKzMqdDYqdDheMisyKnQxKnQzKzIqdDEqdDQrNCp0Mip0NS0yKnQyKnQ2KzIqdDUq"
    "dDgrMip0Nip0OCx0NSp0N14yKnQ4LXQ1KnQ4XjMtdDEqdDIqdDQtdDJeMip0Ni10NSp0N14yK3Q2KnQ3XjIrMyp0NSp0OF4yLXQ2"
    "KnQ4XjIrMip0MSp0MysyKnQxKnQ0LTIqdDIqdDUrNCp0Mip0NisyKnQ1KnQ4KzIqdDYqdDgsdDQqdDdeMip0OC10NCp0OF4zK3Qy"
    "XjIqdDMrdDEqdDIqdDUtdDMqdDdeMi10NCp0N14yK3QzKnQ4XjIrMyp0NCp0OF4yLTQqdDIqdDMtMip0Mip0NC0yKnQxKnQ1KzIq"
    "dDEqdDYtMip0Myp0OCsyKnQ0KnQ4LHQzKnQ3XjIqdDgtdDMqdDheMyt0Ml4yKnQ0K3QxKnQyKnQ2LXQzKnQ3XjItdDQqdDdeMisz"
    "KnQzKnQ4XjIrdDQqdDheMi0yKnQyKnQzLTQqdDIqdDQrMip0MSp0NS0yKnQxKnQ2KzIqdDMqdDgtMip0NCp0ODtcbm9wdGlvbihy"
    "ZWRTQik7IHN5c3RlbShcIi0tdGlja3MtcGVyLXNlY1wiLDEwMDApOyBpbnQgdDA9cnRpbWVyO1xuaWRlYWwgcz1zbGltZ2IoSitt"
    "YXhpZGVhbCgxNSkpO1xuXCJSRVNVTFQgbXNcIixydGltZXItdDAsXCJzYl9zaXplXCIsbmNvbHMocyk7XG5pZGVhbCBCPWtiYXNl"
    "KHMpOyBcIlJFU1VMVCBrYmFzZV9zaXplXCIsbmNvbHMoQik7XG5zaG9ydD0wOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9v"
    "cmRlci1yb3Q2LW4xNS9zLnR4dFwiLHMpOyB3cml0ZShcIjp3IC9rYWdnbGUvd29ya2luZy9vcmRlci1yb3Q2LW4xNS9rYmFzZS50"
    "eHRcIixCKTtcbnF1aXQ7XG4ifV0sICJqb2Jfc2Vjb25kcyI6IDQxMDAwfQ=="
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
