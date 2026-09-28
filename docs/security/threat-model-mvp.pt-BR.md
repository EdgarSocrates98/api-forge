# Modelo de ameaças — MVP

Idioma: [English](threat-model-mvp.md) · [Português (Brasil)](threat-model-mvp.pt-BR.md)

O API Forge analisa entradas potencialmente hostis: um contrato e uma árvore
de código que o operador não escreveu. O caminho de análise não executa código
de entrada nem acessa a rede, removendo as classes maiores; as restantes e
suas mitigações estão abaixo.

| Ameaça | Mitigação |
|---|---|
| YAML/JSON malicioso (billion laughs, tags customizadas, construtores inseguros) | Loader estrito rejeita aliases, merge keys e tags; usa `SafeConstructor`, escalares compatíveis com JSON e recusa chaves duplicadas e números não finitos |
| Código-fonte hostil | Somente `ast.parse`; o módulo analisado nunca é importado ou executado; decorators são comparados por nome |
| Path traversal em `out_dir` | Componentes `..` são recusados (`AF-CASE-PATH-TRAVERSAL`); paths declarados em `case.json` são rechecados no load |
| Escapes por symlink | Cadeia ancestral de `out_dir` verifica symlinks (`AF-CASE-SYMLINK`); extractor não segue links para fora da raiz |
| Sobreposição input/output | `out_dir` que contém ou está contido por input é recusado (`AF-CASE-INPUT-OUTPUT-OVERLAP`) |
| Vazamento de secrets | Artefatos contêm paths, hashes e literais extraídos da AST; não emitem variáveis de ambiente nem conteúdo fora da metadata de rotas |
| Exaustão de recursos | Stream YAML é rejeitado construct-by-construct; AST usa dois passes limitados; refs externas não são percorridas sem limite |
| Case adulterado | `load_case` re-hasha artefatos declarados (`AF-CASE-HASH-MISMATCH`); manifest é escrito por último |
| Adulteração de policy | Catálogo tem schema fechado (`AF-POLICY-SCHEMA`); receipts fixam `policy_sha256` |
| Escape de path em patch | Paths de patch são validados contra a raiz copiada antes de escrever (`AF-SANDBOX-PATH-OUTSIDE`); diffs binários e mode-only são recusados |
| Symlinks em árvores copiadas | Inventário ignora symlinks e copia com `follow_symlinks=False` |
| Injeção de frontmatter | SDD usa loader YAML estrito; `stamp` reescreve somente a linha de hash upstream |
| Abuso de override de gate | `set-phase` estrito registra `gate`, `reason` e `actor` em `gate-overrides.json` |
| Drift do índice de worktrees | `worktree_list` reconcilia `index.json` com `git worktree list --porcelain` e expõe divergências |
| Java ou Go malformado | tree-sitter não executa código nem chama toolchain; parse errors viram diagnósticos `AF-SPRING-PARSE`/`AF-GO-PARSE` |
| Abuso de credencial/rede AWS | Somente `collect *` importa boto3; `analyze`/`model` leem dumps offline; dumps usam diretório explícito e nomes `*.json` |
| Vazamento em dumps coletados | `collect lambda` remove `Code.Location`; `model lambda`/`model terraform` extraem apenas nomes de env vars |
| Injeção de intrínsecos | Tags SAM são dados `{tag, value}` sob loader seguro; Terraform não avalia interpolação |
| Escape de código gerado | `build` escreve somente em `com/apiforge/generated/`, recusa destinos existentes e promove apenas em worktree com policy |
| Drift de perfil de agente | Gate verifica frontmatter, áreas, executors, rotas e referência a `AGENT_PROTOCOL.md` |
| Falsificação de economy ledger | Ledger JSONL é append-only; `economy report` recalcula agregados e marca `tokens_unresolved` sem transcript |
| Exfiltração por reports | Leitor gitleaks emite apenas regra/arquivo/contagem; valores e texto de match nunca são extraídos |
| Falsificação de report | `report verify` re-hasha corpo, evidência e catálogo; assinatura prova correspondência, não autoria |
| Execução de ferramenta externa | `run tool` executa somente binários allowlisted com argv fixo e timeout limitado; `--dry-run` mostra argv |
| Conclusões fabricadas | Diagnósticos `unresolved` nomeiam incerteza; `confirmed` exige `fact_ids` de evidência |
| Task spec/histórico adulterado | Selo Ed25519 vincula bytes exatos; revisão altera o selo e `task accept` exige ator distinto e evidência |
| Poisoning de cache stale | Chave é `sha256(extractor_version|framework|source_digest)`; corrupção vira miss e o extractor continua fonte da verdade |
| Poisoning do cache econômico em camadas (local ou tier compartilhado `APIFORGE_CACHE_HOME`) | todo objeto é re-hasheado na leitura; divergência ou entrada ilegível vira miss corrompido e é recalculada; probes de dependência decidem frescor antes do TTL; saída com `--no-cache` é idêntica byte a byte |
| Evidência live usada quando a prova local basta, ou para mutar | `evidence gate` concede `live_read_only` só para perguntas sobre efeito em runtime e recusa `live_mutation` (`AF-EVIDENCE-MUTATION-REFUSED`); `verify escalate` nunca passa de `live_read_only` |
| Expansão de entidades em JUnit XML (XXE / billion laughs) | `slice tests` tokeniza só o subconjunto de testcase sem parser XML e recusa qualquer DOCTYPE ou ENTITY (`AF-SLICE-XML-REFUSED`) |
| Manifest de frescor upstream forjado | `knowledge watch` só lê o manifest local, registra seu sha256, nunca busca nem reescreve pack; entrada ausente é `unresolved`, não fresh |
| Burla do orçamento no resume | `economy_checkpoint.json` é contrato validado (`AF-ECONOMY-CHECKPOINT-INVALID` se adulterado); o teto de chamadas usa o `calls_used` persistido pelo control plane; o resume nunca baixa o perfil do checkpoint |
| Adulteração de grafo | Cada linha carrega hash de `{id,kind,props}`; load recusa `AF-GRAPH-HASH-MISMATCH` |
| Claim falso de `DONE` | `brief show` deriva status da máquina de estados; `DONE` exige aceitação por ator distinto e evidência |

## Limitações conhecidas

- O extractor FastAPI é estático: rotas fora de decorators/`include_router`
  aparecem como `unresolved`.
- A avaliação JSON Schema é limitada às regras de diff documentadas; não se
  tenta equivalência arbitrária.
- `load_case` verifica integridade e correspondência ao manifest, não autoria;
  não há chave de assinatura.
