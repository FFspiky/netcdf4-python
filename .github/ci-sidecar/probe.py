import os
import pathlib
import subprocess
import urllib.request
import urllib.error

def run(label, command, extra=None):
    print(f"\nPROBE {label}: {command}", flush=True)
    try:
        p = subprocess.run(command, env={**os.environ, **(extra or {})}, timeout=50)
        print(f"RESULT {label} exit={p.returncode}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"RESULT {label} timeout=50s", flush=True)

prefix = os.environ["CONDA_PREFIX"]
subprocess.run(["gcc", ".github/ci-sidecar/native.c", f"-I{prefix}/include",
                f"-L{prefix}/lib", f"-Wl,-rpath,{prefix}/lib", "-lnetcdf", "-lmpi", "-o", "native-probe"], check=True)
run("native-mpi-default", ["mpirun", "-np", "4", "--oversubscribe", "./native-probe"])
run("native-mpi-tcp", ["mpirun", "-np", "4", "--oversubscribe", "--mca", "pml", "ob1", "--mca", "btl", "self,tcp", "./native-probe"])
run("native-filter-default", ["./native-probe", "filter"])
plugins = str(pathlib.Path(prefix) / "lib/hdf5/plugin")
print("plugin paths", list(pathlib.Path(prefix).glob("lib/**/lib*std*")), flush=True)
run("native-filter-pluginpath", ["./native-probe", "filter"], {"HDF5_PLUGIN_PATH": plugins})
urlbase = "https://tds.scigw.unidata.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_onedegree_noaaport/GFS_Global_onedeg_noaaport_"
for day in ("20261110", "20261111"):
    url = urlbase + day + "_1800.grib2.dds"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            print("DAP", url, r.status, dict(r.headers), r.read(400).decode(errors="replace"), flush=True)
    except urllib.error.HTTPError as e:
        print("DAP", url, e.code, dict(e.headers), e.read(1000).decode(errors="replace"), flush=True)
    except Exception as e:
        print("DAP", url, repr(e), flush=True)
