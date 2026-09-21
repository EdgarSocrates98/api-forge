import pytest

from apiforge.sandbox.diff import SandboxError, parse_unified_diff

CREATE = """\
diff --git a/app/new.py b/app/new.py
new file mode 100644
--- /dev/null
+++ b/app/new.py
@@ -0,0 +1,2 @@
+line1
+line2
"""

MODIFY = """\
diff --git a/app/main.py b/app/main.py
--- a/app/main.py
+++ b/app/main.py
@@ -2,3 +2,3 @@
 keep
-old
+new
 keep2
"""

DELETE = """\
diff --git a/app/old.py b/app/old.py
deleted file mode 100644
--- a/app/old.py
+++ /dev/null
@@ -1,1 +0,0 @@
-gone
"""


def test_parse_create() -> None:
    patches = parse_unified_diff(CREATE)
    assert len(patches) == 1
    assert patches[0].old_path is None
    assert patches[0].new_path == "app/new.py"
    assert patches[0].hunks[0].new_start == 1


def test_parse_modify_and_delete() -> None:
    mod = parse_unified_diff(MODIFY)[0]
    assert mod.old_path == "app/main.py"
    assert mod.new_path == "app/main.py"
    assert "-old" in mod.hunks[0].lines
    delete = parse_unified_diff(DELETE)[0]
    assert delete.new_path is None


def test_binary_patch_refused() -> None:
    with pytest.raises(SandboxError, match="AF-SANDBOX-BINARY-PATCH"):
        parse_unified_diff("diff --git a/b.png b/b.png\nBinary files differ\n")


def test_mode_only_refused() -> None:
    with pytest.raises(SandboxError, match="AF-SANDBOX-MODE-ONLY"):
        parse_unified_diff("diff --git a/f.py b/f.py\nold mode 100644\nnew mode 100755\n")
