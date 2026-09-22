# API Forge evaluation corpus

Este corpus referencia fixtures executáveis e representativos do próprio
repositório. Eles são inputs de análise; não são executados como aplicações
durante descoberta. Cada caso deve declarar o domínio, o adapter esperado,
as evidências obrigatórias, a mutação de holdout e as limitações conhecidas.

Fontes iniciais:

- `tests/fixtures/fastapi_orders` — API Python/FastAPI;
- `tests/fixtures/spring_orders` — API Java/Spring;
- `tests/labs/orders-spring` — cenário de evolução em sandbox;
- `tests/evals/cases` — casos de gRPC, observabilidade e runtime.

O corpus não prova cobertura de produção. Ele mede regressão determinística
até que entradas reais anonimizadas sejam adicionadas com autorização.
