"""Prepare each lab Autonomous Database for OML4Py notebook compute.

For every database created by adb_create.py: download its mTLS wallet into
$OCI_LAB_DIR/wallet-<name>/ (wallet password in wallet-<name>.pass, mode
600), connect as ADMIN, create the notebook user LABML with OML_DEVELOPER
(the role that admits OML Notebooks and embedded Python execution), store
the LABML password in adb-<name>.labml (mode 600), and prove the embedded
Python path by registering and running a script through pyqEval. Prints each
database's service URLs and the script result; prints no secret.

Usage: $PYTHON scripts/oci_lab/adb_oml_setup.py
"""

from __future__ import annotations

import io
import json
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import oci
import oracledb
from adb_create import DATABASES, LAB_DIR, password

PROBE = """def probe():
    import platform, numpy as np, pandas as pd, sklearn
    return pd.DataFrame({"python": [platform.python_version()], "numpy": [np.__version__],
                         "pandas": [pd.__version__], "sklearn": [sklearn.__version__],
                         "cpus": [os.cpu_count() if (os := __import__("os")) else 0],
                         "sum": [float(np.arange(1_000_000, dtype=np.float64).sum())]})"""


def secret(path: Path) -> str:
    if not path.exists():
        path.touch(mode=0o600)
        path.write_text(password())
    return path.read_text().strip()


def main() -> None:
    config = oci.config.from_file()
    db = oci.database.DatabaseClient(config)
    by_name = {
        d.display_name: d
        for d in oci.pagination.list_call_get_all_results(db.list_autonomous_databases, config["tenancy"]).data
        if d.lifecycle_state == "AVAILABLE"
    }
    for display, name, _workload in DATABASES:
        adb = by_name[display]
        wallet_dir = LAB_DIR / f"wallet-{display}"
        wallet_pass = secret(LAB_DIR / f"wallet-{display}.pass")
        if not (wallet_dir / "tnsnames.ora").exists():
            body = db.generate_autonomous_database_wallet(
                adb.id, oci.database.models.GenerateAutonomousDatabaseWalletDetails(password=wallet_pass)
            ).data.content
            wallet_dir.mkdir(mode=0o700, exist_ok=True)
            zipfile.ZipFile(io.BytesIO(body)).extractall(wallet_dir)
            for f in wallet_dir.iterdir():
                f.chmod(0o600)
        cu = adb.connection_urls
        urls = {k: getattr(cu, k) for k in cu.attribute_map if k.endswith("_url") and getattr(cu, k)}
        oml_host = urllib.parse.urlparse(urls["machine_learning_user_management_url"]).hostname or ""
        conn = oracledb.connect(
            user="ADMIN",
            password=(LAB_DIR / f"adb-{display}.admin").read_text().strip(),
            dsn=f"{name}_low",
            config_dir=str(wallet_dir),
            wallet_location=str(wallet_dir),
            wallet_password=wallet_pass,
        )
        labml = secret(LAB_DIR / f"adb-{display}.labml")
        with conn.cursor() as cur:
            cur.execute("select count(*) from dba_users where username = 'LABML'")
            row = cur.fetchone()
            if row is None or row[0] == 0:
                cur.execute(f'create user labml identified by "{labml}" quota unlimited on data')
            for grant in ("create session", "dwrole", "oml_developer"):
                cur.execute(f"grant {grant} to labml")
            # SQL-invoked embedded Python calls back to the OML REST service;
            # pyqAppendHostACE takes the host root domain (the hostname
            # without its first label) and grants LABML connect on it.
            cur.callproc("pyqAppendHostACE", ["LABML", oml_host.split(".", 1)[1]])
        conn.close()
        conn = oracledb.connect(
            user="LABML",
            password=labml,
            dsn=f"{name}_low",
            config_dir=str(wallet_dir),
            wallet_location=str(wallet_dir),
            wallet_password=wallet_pass,
        )
        req = urllib.request.Request(
            f"https://{oml_host}/omlusers/api/oauth2/v1/token",
            data=json.dumps({"grant_type": "password", "username": "LABML", "password": labml}).encode(),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed https host from the service
            token = json.load(resp)["accessToken"]
        with conn.cursor() as cur:
            cur.callproc("pyqSetAuthToken", [token])
            cur.callproc("sys.pyqScriptCreate", ["lab_probe", PROBE, False, True])  # replace=True
            cur.execute("select * from table(pyqEval(par_lst => null, out_fmt => 'JSON', scr_name => 'lab_probe'))")
            row = cur.fetchone()
            result = row[-1].read() if row and hasattr(row[-1], "read") else row
        conn.close()
        print(display, "urls:", sorted(urls))
        print(display, "pyqEval:", result)


if __name__ == "__main__":
    main()
