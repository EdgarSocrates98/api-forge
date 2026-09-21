DIFF_ADDING_ROUTE = """\
diff --git a/app/routes/orders.py b/app/routes/orders.py
--- a/app/routes/orders.py
+++ b/app/routes/orders.py
@@ -8,0 +9,4 @@
+
+@router.get("/extra")
+def extra():
+    return {}
"""

DIFF_TOUCHING_EVIL = """\
diff --git a/../evil.py b/../evil.py
new file mode 100644
--- /dev/null
+++ b/../evil.py
@@ -0,0 +1,1 @@
+evil
"""

DIFF_BINARY = """\
diff --git a/bin.png b/bin.png
new file mode 100644
Binary files /dev/null and b/bin.png differ
"""

DIFF_MODE_ONLY = """\
diff --git a/app/main.py b/app/main.py
old mode 100644
new mode 100755
"""

DIFF_MISSING_TARGET = """\
diff --git a/app/absent.py b/app/absent.py
--- a/app/absent.py
+++ b/app/absent.py
@@ -1,1 +1,1 @@
-old
+new
"""
