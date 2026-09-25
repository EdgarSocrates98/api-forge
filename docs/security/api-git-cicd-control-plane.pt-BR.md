# Segurança do control plane de API + Git + CI/CD

Idioma: [English](api-git-cicd-control-plane.md) · [Português (Brasil)](api-git-cicd-control-plane.pt-BR.md)

O recurso de change-control é uma fronteira de evidência, não um engine de
deploy. Seu caminho padrão é replay local a partir de `af-change-bundle/1`; o
bundle é uma entrada não confiável e é validado antes de chegar ao core
determinístico.

## Fronteira somente leitura

`GitHubReadOnlyAdapter` recebe um `ReadOnlyTransport` injetado. O transporte
HTTP empacotado pode emitir somente requests `GET`, e o adapter lê observações
de compare, pull request e check run. Ele nunca faz merge, push, dispatch de
workflow, alteração de branch, publicação de status, deploy ou autofix.
Credenciais ficam no transporte e não fazem parte do contrato persistido;
campos de payload que correspondem a token, authorization, secret ou password
são redigidos antes do hash.

## Confiança e evidência

Payloads de provedor são observações, não prova de saúde de runtime, sucesso de
deploy, permissão, custo ou capacidade de rollback. `af-external-read-receipt/1`
adiciona hash de resposta e janela de freshness limitados; ainda não prova
autoria, permissão de mutação ou SLOs de produção. `heuristic`, `unresolved` e
`blocked` continuam sendo estados terminais válidos.

O verificador local confirma que o resultado referencia artefatos existentes.
A coleta live produz um `ChangeCollectionReceipt` ao lado do bundle
sanitizado; ele vincula o hash do bundle e hashes das fontes do provedor, mas
continua sendo observação e não prova de autoria, identidade, permissão,
freshness ou deploy. Um gate específico do provedor ainda precisa de política
de freshness aprovada, prova de identidade/permissão, plano de rollback e
verificação independente antes de promover um estado de capacidade de
produção.

## Classes de entrada cobertas

A implementação trata JSON do provedor e paths de bundles fornecidos pelo
repositório como não confiáveis. Paths são validados pela fronteira de análise
e armazenamento de case; JSON é fechado por contratos Pydantic; entrada
ausente, malformada ou falha de transporte retorna código `AF-*`, campo
rejeitado e `unlock` seguro. Nenhum caminho de erro deve expor traceback pela
CLI pública.

## Host IDE/UI local

O host embutido usa loopback por padrão e serve somente rotas fixas. Bind
remoto exige Bearer token e TLS, salvo quando o operador o coloca atrás de um
proxy HTTPS confiável. Ele não expõe paths arbitrários, credenciais ou
endpoints de mutação. O documento HTML e a projeção JSON para IDE derivam do
mesmo `ChangeControlResult`; uma superfície não pode transformar `review`,
`blocked` ou `unresolved` em sucesso.

## Fronteira de mutação

`scripts/github_pr_host.py` é o único host de mutação do repositório. Ele não é
importado por `src/apiforge`, exige `APIFORGE_HOST_APPROVED=true`, faz lookup
idempotente antes de criar PR e emite `af-github-pr-receipt/1`. O pedido de
auto-merge é controlado por `APIFORGE_AUTO_MERGE=true` e continua sujeito à
branch protection. O core e os agentes nunca recebem essa autoridade.
