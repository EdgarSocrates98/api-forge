# Fronteiras do MVP

Idioma: [English](mvp-boundaries.md) · [Português (Brasil)](mvp-boundaries.pt-BR.md)

A vertical slice é deliberadamente limitada. Tudo que estiver fora desta
lista deve aparecer como diagnóstico `unresolved` ou recusa nomeada — nunca
como conclusão fabricada.

## Incluído

- documentos OpenAPI 3.1 em JSON ou YAML estrito, sem aliases, merge keys,
  chaves duplicadas ou tags customizadas;
- fonte FastAPI descoberta somente por `ast.parse`: decorators
  `FastAPI`/`APIRouter`, paths e prefixes literais, `include_router` resolvido
  em imports locais, chaves sensíveis a trailing slash e rotas duplicadas
  preservadas;
- API-IR canônico indexado por método em minúsculas + path literal, com zero,
  uma ou várias projeções por lado e proveniência completa;
- diff de contrato limitado: operações e responses removidos/adicionados,
  deltas de propriedades obrigatórias de request e opcionais de response,
  somente refs locais `#/components/schemas/...`;
- quatro regras de divergência executáveis (`AF-CONTRACT-001`,
  `AF-CODE-001..003`) dirigidas pelo catálogo empacotado;
- persistência reproduzível de case com load verificado por hash.

## Explicitamente fora do escopo

- **Executar código analisado.** Não há import, `eval` ou runtime ASGI.
- **Chamadas de modelo.** O core nunca importa `openai`, `anthropic`, `boto3`,
  `litellm` ou qualquer SDK; não há LLM no caminho de análise.
- **Rede.** Não há `$ref` via HTTP, telemetria ou checks de atualização.
- **Inferência de framework além de FastAPI.** Outros frameworks são adapters
  futuros, não fallbacks.
- **Acesso cloud.** Não há probing de credenciais nem chamadas ao provedor.
- **Mutação.** Entradas são somente leitura; as únicas escritas vão para um
  `out_dir` validado que não pode sobrepor inputs.

## Contrato de incerteza

Quando a extração não consegue provar algo — prefixo dinâmico, falha de parse
ou ciclo de include — o pipeline emite diagnóstico `unresolved` nomeando o
blind spot. Regras que dependem da evidência ausente também rebaixam para
`unresolved`, em vez de afirmar ausência. Ausência de evidência não é
evidência de ausência.
