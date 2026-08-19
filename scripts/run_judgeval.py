#!/usr/bin/env python3
"""
Launcher for the judge validation.

WHY A LAUNCHER AT ALL: 06_judge_panel.py starts with a digit, so it is not a
valid Python module name and cannot be imported normally. The first attempt
worked around that with importlib + exec() -- and exec() runs a module BODY,
while main() only fires under `if __name__ == "__main__"`. So it defined
everything, called nothing, exited 0, and wrote an empty log.

Silent no-op with a clean exit code. Same shape as every other instrument
failure tonight: it looked exactly like a thing that had run.

This version loads the panel module explicitly and CALLS main() explicitly, so
there is no name-magic between me and the work.
"""
import importlib.util
import sys

sys.path.insert(0, "/tmp")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


jp = load("/tmp/06_judge_panel.py", "judge_panel")
sys.modules["06_judge_panel"] = jp

# 06b does `import_module("06_judge_panel")`, which cannot work for a name
# starting with a digit. Hand it the already-loaded module instead.
src = open("/tmp/06b_validate_judges.py", encoding="utf-8").read()
src = src.replace(
    'jp = import_module("06_judge_panel") if os.path.exists("/tmp/06_judge_panel.py") else None',
    "jp = sys.modules['06_judge_panel']",
)

ns = {"__name__": "judgeval"}
exec(compile(src, "06b_validate_judges.py", "exec"), ns)

if "main" not in ns:
    print("!! main() not defined after exec -- the patch above did not apply")
    sys.exit(1)

sys.exit(ns["main"]())
