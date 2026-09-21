"""Terraform extractor: literal attrs as facts, interpolation as diagnostics."""

from pathlib import Path

from apiforge.adapters.terraform.extract import extract_terraform

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "terraform_api"


def test_api_gateway_and_lambda_facts() -> None:
    inv = extract_terraform(FIXTURE)
    kinds = {f.kind for f in inv.facts}
    assert kinds == {
        "tf.apigateway.rest_api",
        "tf.apigateway.method",
        "tf.apigateway.integration",
        "tf.apigateway.stage",
        "tf.lambda.function",
        "tf.lambda.permission",
    }
    method = next(f for f in inv.facts if f.kind == "tf.apigateway.method")
    assert method.attrs["authorization"] == "NONE"
    fn = next(f for f in inv.facts if f.kind == "tf.lambda.function")
    assert fn.attrs["env_keys"] == ("LOG_LEVEL", "ORDERS_TABLE")
    assert "value-not-read" not in str(fn.attrs)


def test_interpolation_is_unresolved_diagnostic() -> None:
    inv = extract_terraform(FIXTURE)
    unresolved = [d for d in inv.diagnostics if d.code == "AF-TF-UNRESOLVED"]
    assert unresolved  # source_arn interpolation is named, never resolved
    assert any("source_arn" in d.message for d in unresolved)


def test_parse_error_is_named(tmp_path: Path) -> None:
    (tmp_path / "bad.tf").write_text('resource "x" "y" { unclosed')
    inv = extract_terraform(tmp_path)
    assert any(d.code == "AF-TF-PARSE" for d in inv.diagnostics)


def test_non_api_resources_ignored(tmp_path: Path) -> None:
    (tmp_path / "x.tf").write_text(
        'resource "aws_s3_bucket" "b" {\n  bucket = "x"\n}\n'
    )
    inv = extract_terraform(tmp_path)
    assert inv.facts == ()
    assert inv.input_hashes["x.tf"]
