# RC3 Auth — Primeira entrega administrativa

## Entregue

- autenticação OIDC nativa do Streamlit;
- login e logout na barra lateral;
- allowlist de administradores por e-mail;
- menu administrativo condicional;
- página administrativa protegida;
- identidade disponível para auditoria;
- nenhum formulário de edição.

## Secrets

Use `.streamlit/secrets.example.toml` como modelo. Os valores reais devem
ser colocados em `.streamlit/secrets.toml` localmente ou em Settings >
Secrets no Streamlit Community Cloud.

## Segurança

O menu oculto não é a única proteção. A página administrativa valida a
autorização novamente. Contas autenticadas fora da allowlist recebem
acesso negado.

## Limitação

Esta é a Opção A experimental. JSON e JSONL continuam sujeitos à
persistência efêmera do Streamlit Community Cloud.
