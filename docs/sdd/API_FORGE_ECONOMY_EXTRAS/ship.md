---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: ship
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "4d1b24eedcb33d26325caeeb254a834fe39ac2bc0ded8c06a9deea3672215de6"
deviations:
- conservative-symbol-mentions-in-test-selection
- declared-provider-descriptors
evidence:
- path: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-eval.json
  sha256: 13080050e3951cfda6a208494f8998e1aec7992ddbef023229f48ddfb6a3ea56
- path: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-tests.txt
  sha256: 83c18b57eba63c208f20fe6c4ca0cf41c49f64ef9323339cc8d4dd1a04565df7
---
# ship

Ready for review. Test selection is conservative (a generic symbol such as `render` selects every test that mentions it) — recall first. Provider descriptors are declared data; no model is called and no local model is required.
