# omega-skill

## Software factory

`/factory run` constroi cada issue aberta do GitHub com a label `factory`, pelo percurso
intake, spec, build, gate, review, approve, um pull request por issue. O estado fica em
`factory/jobs/` (fora do controlo de versoes); `factory/bin/job` e o unico que o escreve.
Verificacoes: `factory/checks.sh`. Painel: `cd factory && python3 -m http.server`, depois
abrir http://localhost:8000/dashboard.html.

Cada job trabalha na sua propria git worktree, um checkout completo do repositorio em
`.worktrees/<job-id>` (fora do controlo de versoes). Uma ferramenta lancada a partir da raiz
que nao leia o `.gitignore` tambem ve essas copias: excluir `.worktrees/` na sua configuracao.
