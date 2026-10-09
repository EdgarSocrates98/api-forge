# Uninstall — api-forge

```bash
apiforge uninstall            # remove só arquivos gerenciados
apiforge uninstall --purge    # + remove o estado local (.apiforge/install/)
```

O ledger SHA-256 decide ownership: arquivos que você criou ou modificou
depois da instalação ficam no lugar (reportados como `kept`). Diretórios
que esvaziam são podados; os seus permanecem.
