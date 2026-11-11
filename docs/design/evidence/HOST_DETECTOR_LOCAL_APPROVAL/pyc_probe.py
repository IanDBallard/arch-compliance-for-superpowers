"""Probe: the default SourceFileLoader runs an unchecked hash-based .pyc; a source-only loader runs the source.

Run: python -I docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py
"""
import importlib.machinery
import importlib.util
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

d = Path(tempfile.mkdtemp())
src = d / "det.py"
other = d / "other.py"
src.write_text("WHO = 'source'\n", encoding="utf-8")
other.write_text("WHO = 'pyc'\n", encoding="utf-8")
cache = importlib.util.cache_from_source(str(src))
py_compile.compile(str(other), cfile=cache, invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)


def load(name, loader=None):
    spec = importlib.util.spec_from_file_location(name, src, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.WHO


class SourceOnly(importlib.machinery.SourceFileLoader):
    def get_code(self, fullname):
        return compile(self.get_data(self.path), self.path, "exec", dont_inherit=True)


print("default loader runs:", load("m1"))
print("source-only loader runs:", load("m2", SourceOnly("m2", str(src))))
shutil.rmtree(d)
