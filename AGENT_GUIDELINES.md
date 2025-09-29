# Orientações para Agents de IA

## Processo de Commit e Push

Sempre que for necessário realizar um commit, siga rigorosamente os passos abaixo:

1. **Atualize o repositório local:**

   - Execute `git pull` para garantir que está com a versão mais recente do repositório remoto.

2. **Adicione todas as alterações:**

   - Execute `git add .` para adicionar todas as mudanças (novos arquivos, modificações e deleções).

3. **Detecte as alterações:**

   - Verifique quais arquivos foram adicionados, modificados ou removidos usando `git status` ou `git diff --cached`.

4. **Crie o commit seguindo o padrão Conventional Commits:**

   - O **título** do commit deve ser curto, objetivo e em **português**.
   - O **corpo** do commit deve listar as mudanças detalhadamente, usando marcadores `-`, também em **português**.
   - Exemplo de commit:

     ```
     feat: adiciona autenticação OAuth2

     - Cria helpers para fluxo OAuth2
     - Adiciona configuração de cliente OAuth2
     - Atualiza README com instruções de uso
     ```

5. **Envie as alterações para o repositório remoto:**
   - Execute `git push` para subir o commit.

---

> **Nota:** Este arquivo pode receber outras instruções para agents de IA além do processo de commit.
