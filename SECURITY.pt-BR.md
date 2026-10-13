# Política de segurança

## Escopo

O API Forge é uma plataforma de engenharia offline-first. Seu núcleo
determinístico analisa código-fonte, contratos e evidências persistidas; ele
não executa aplicações-alvo, chama SDKs de modelos nem altera o estado de
cloud, bancos de dados, brokers ou provedores Git.

Esta política cobre:

- o pacote Python e a CLI em `src/apiforge/`;
- a superfície MCP, os agentes e as skills do repositório;
- adaptadores externos somente leitura e seus receipts;
- a fronteira dedicada de CI em `scripts/` e `.github/workflows/`;
- o host conteinerizado de change-control.

Um resultado de análise estática, fixture, probe de runtime local ou receipt
não constitui prova de segurança em produção. Deploy, permissões do provedor,
saúde de runtime e hardening operacional continuam sendo responsabilidade do
responsável pelo deploy e exigem evidência independente.

## Versões suportadas

| Versão | Status de suporte |
| --- | --- |
| `0.1.x` | Correções de segurança aceitas |
| Versões anteriores | Atualize antes de reportar uma vulnerabilidade, quando possível |

O runtime suportado é a versão do Python declarada em `pyproject.toml`.

## Como reportar uma vulnerabilidade

Não divulgue suspeitas em issue ou pull request público. Prefira um GitHub
Security Advisory privado para este repositório:

<https://github.com/EdgarSocrates98/api-forge/security/advisories/new>

Se advisories privados não estiverem disponíveis, envie o relatório para
`edgarsocrates98@gmail.com` com o assunto `API Forge security report`.

Inclua, quando for seguro compartilhar:

- descrição concisa e impacto;
- commit, release ou componente afetado;
- passos de reprodução ou uma prova de conceito mínima e não destrutiva;
- permissões, configuração e ambiente necessários;
- logs ou receipts sem secrets, tokens e dados pessoais;
- mitigação sugerida, se conhecida.

Permita que os mantenedores investiguem em privado antes da divulgação
pública. Não envie credenciais, chaves privadas, access tokens ou dados de
produção.

## Processo de tratamento

Os reports são triados em privado, reproduzidos em branch ou sandbox isolado e
registrados com as evidências relevantes e limitações não resolvidas. Uma
correção deve incluir um teste de regressão ou uma justificativa explícita
para não adicioná-lo com segurança. Mutações externas nunca são usadas na
reprodução sem gate de política e aprovação explícitos.

A resolução pode incluir commit corrigido, orientação de mitigação, release
note e divulgação coordenada. Um receipt comprova a correspondência entre os
artefatos reportados e a execução de verificação; não comprova autoria nem que
um deploy de produção afetado foi corrigido.

## Fronteiras e expectativas de segurança

- Trate bundles, contratos, payloads de provedores e artefatos gerados como
  entradas não confiáveis.
- Mantenha secrets fora de cases, bundles, receipts, fixtures, logs e corpos
  de PR.
- Use adaptadores somente leitura para observações externas. Eles não
  autorizam merge, push, deploy, dispatch de workflow ou outra mutação.
- A criação de PR e o auto-merge opcional ficam restritos ao host de CI
  dedicado, exigem configuração explícita e emitem um receipt
  `af-github-pr-receipt/1`. O core e os agentes não recebem essa autoridade.
- Configure autenticação Bearer e TLS, ou um proxy TLS confiável, antes de
  expor o host de change-control além do loopback.
- Mantenha exemplos anonimizados; não faça commit de payloads de provedor com
  identidades, URLs assinadas ou credenciais.
- Não interprete análise local `supported` como afirmação de segurança em
  produção. Freshness do provedor, segurança do deploy, saúde de runtime e
  SLOs exigem evidência externa independente.

## Reports fora do escopo

Os itens abaixo não são, por si só, vulnerabilidades do core:

- uma capacidade intencionalmente `heuristic`, `unresolved` ou `unsupported`
  quando a limitação está documentada;
- uma recusa que expõe seu código `AF-*`, campo rejeitado e unlock seguro;
- ausência de evidência de produção quando nenhum alvo de produção ou acesso
  ao provedor foi configurado;
- configuração insegura introduzida pelo responsável por um deploy downstream,
  salvo quando os defaults documentados do repositório afirmam impedi-la.

Reports que contenham secrets ou dados pessoais devem ser retirados e
rotacionados imediatamente pelo provedor afetado.

Idioma: [English](SECURITY.md) · [Português (Brasil)](SECURITY.pt-BR.md)
