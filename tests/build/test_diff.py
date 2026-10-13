from apiforge.build.diff import sources_to_diff
from apiforge.sandbox.diff import parse_unified_diff


def test_sources_emit_new_file_patches() -> None:
    diff = sources_to_diff({"src/A.java": "package a;\nclass A {}\n"})
    patches = parse_unified_diff(diff)
    assert len(patches) == 1
    assert patches[0].old_path is None
    assert patches[0].new_path == "src/A.java"


def test_multiple_sources_sorted() -> None:
    diff = sources_to_diff({"b/B.java": "x\n", "a/A.java": "y\n"})
    assert diff.index("a/A.java") < diff.index("b/B.java")


def test_diff_round_trip_content() -> None:
    content = "line1\nline2\n"
    diff = sources_to_diff({"f.txt": content})
    patch = parse_unified_diff(diff)[0]
    added = [l[1:] for h in patch.hunks for l in h.lines if l.startswith("+")]
    assert "\n".join(added) + "\n" == content
