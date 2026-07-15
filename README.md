# Controle de Faltas — Multieletrica

App em Streamlit ligado a uma planilha Google Sheets para registrar e acompanhar
faltas de produtos.

- **Vendedor**: digita o código do produto, o app puxa `desc` e `grupo` da aba
  `dados_rp`, ele adiciona uma observação e registra a falta. Acompanha as
  próprias faltas.
- **Comprador**: vê as faltas de todos os vendedores, **assume** uma falta como
  dele (com observação opcional) e acompanha o que assumiu.

## Planilha (Google Sheets)

Abas usadas:

| Aba        | Colunas                                                                              |
|------------|--------------------------------------------------------------------------------------|
| `data`     | `cod, desc, grupo, data, obs_vendedor, obs_comprador, vendedor, comprador`            |
| `user`     | `id_usuario, usuario, senha, cargo`  (cargo = `vendedor` ou `comprador`)              |
| `dados_rp` | `cod, desc, grupo`  (cadastro de produtos usado na busca do vendedor)                 |

> A aba `dados_rp` precisa estar preenchida com essas colunas, senão o vendedor
> não consegue buscar produtos.

## Rodar localmente

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```

### Credenciais

Crie o arquivo `.streamlit/secrets.toml` a partir de `.streamlit/secrets.toml.example`
com os dados da sua conta de serviço do Google e o link da planilha. Compartilhe
a planilha com o `client_email` da conta de serviço (permissão de editor).

## ⚠️ Repositório público

O arquivo `.streamlit/secrets.toml` contém a **chave privada** da conta de serviço
e **nunca** deve ser enviado ao repositório. Ele já está no `.gitignore`.
Antes do primeiro `git push`, rode `git status` e confirme que `secrets.toml`
**não** aparece na lista.
