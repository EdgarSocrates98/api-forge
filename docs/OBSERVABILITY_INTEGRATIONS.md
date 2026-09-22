# Observabilidade e integrações externas

O API Forge separa o núcleo determinístico do host que controla rede, credenciais e SDKs.

## Fluxo seguro

```text
ReadPlan / CircuitMetrics
        |
        v
provider query + safety budgets + circuit breaker
        |
        v
HostExportBinding
  provider/backend compatíveis
  endpoint HTTPS allowlisted
  CredentialStatus available
  enabled=true
  approval_id obrigatório
        |
        v
callback autenticado do host
        |
        v
receipt sent/failed com evidência
```

Sem binding válido o resultado é `blocked` ou `disabled` e `network_called=false`.
O API Forge nunca resolve secrets, cria headers de autenticação, instala SDK ou
abre socket no núcleo.

## Backends atuais

- OTel: payload OTLP-like preparado pelo builder, pronto para exporter do host.
- Datadog: série de métricas com tags de provider e estado.
- Dynatrace: gauges com dimensões de provider e estado.
- CloudWatch: leitura planejada/normalizada; exportação é evolução futura.

## Ativação real ainda necessária

1. Implementar callbacks host-owned usando HTTP/SDK oficial, timeout e retry do host.
2. Resolver credenciais somente pelo broker do host e redigir headers/logs.
3. Configurar endpoints por ambiente e allowlists sem placeholders.
4. Executar em conta/tenant aprovado com evidência e rollback.
5. Validar semantic conventions, rate limits, retenção e custo por backend.

Veja o mapa completo em [API_FORGE_EVOLUTION_MAP.md](API_FORGE_EVOLUTION_MAP.md).
