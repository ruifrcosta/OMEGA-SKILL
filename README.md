```
   ____  __  ___________  ______    __________  ______  ___
  / __ \/  |/  / ____/  |/  /   |  /_  __/ __ \/  _/  |/  /
 / / / / /|_/ / __/ / /|_/ / /| |   / / / / / // // /|_/ / 
/ /_/ / /  / / /___/ /  / / ___ |  / / / /_/ // // /  / /  
\____/_/  /_/_____/_/  /_/_/  |_| /_/  \____/___/_/  /_/   
                                                           
   SISTEMA OPERACIONAL DE ENGENHARIA AUTÓNOMA │ KERNEL v2.0
```

# OMEGA — SISTEMA OPERACIONAL DE ENGENHARIA DE SOFTWARE AUTÓNOMO, DESIGN IMPECAVEL & GOVERNANÇA PMO

O **OMEGA** é um motor de desenvolvimento, arquitetura, design visual e governança de portfólio de nível Big Tech (altamente inspirado na cultura e padrões da Stripe, Vercel, Linear e OpenAI). 

Ele unifica todas as capacidades sob um único modelo de **Governança Zero-Trust**, sincroniza o estado dinamicamente através do padrão de **6-Core Memory Bank** do espaço de trabalho e implementa um **Universal PMO Engine** para entregas e cadências proporcionais (Híbrido, Agile, Waterfall, SAFe, Lean).

---

## 📂 ÍNDICE GERAL DO MANUAL

1. [Manual de Instalação e Atualização](#-manual-de-instalação-e-atualização)
2. [Manual de Ativação (Prompts e Gatilhos)](#-manual-de-ativação-prompts-e-gatilhos)
3. [Os Três Pilares da Engenharia OMEGA](#-os-três-pilares-da-engenharia-omega)
4. [Catálogo Completo de Comandos (Impeccable Vocabulary)](#-catálogo-completo-de-comandos)
5. [O Cofre PMO (Índice de 18 Arquivos Mandatórios)](#-o-cofre-pmo-índice-de-18-arquivos-mandatórios)
6. [O Motor de Estética e Dials Visuais](#-o-motor-de-estética-e-dials-visuais)

---

## 📦 MANUAL DE INSTALAÇÃO E ATUALIZAÇÃO

O OMEGA pode ser instalado globalmente ou localmente em qualquer ambiente baseado em **Claude Code**, **Antigravity SDK** ou terminal CLI padrão.

### 1. Instalação Automática (Recomendada)
Para instalar o OMEGA instantaneamente a partir do ecossistema aberto de AI Skills, execute:

```bash
# Instalação global (registado no sistema e disponível para todos os projetos)
npx skills add ruifrcosta/OMEGA-SKILL -g -y

# Instalação local no diretório do projeto atual
npx skills add ruifrcosta/OMEGA-SKILL -y
```

### 2. Instalação Manual (Git Fallback)
Caso prefira instalar diretamente a partir do repositório fonte para fins de contribuição ou desenvolvimento offline:

```bash
# Clone para a pasta de skills globais do Antigravity
git clone https://github.com/ruifrcosta/OMEGA-SKILL.git ~/.gemini/config/skills/OMEGA-SKILL

# Clone para a pasta de skills globais do Claude Code
git clone https://github.com/ruifrcosta/OMEGA-SKILL.git ~/.claude/skills/OMEGA-SKILL
```

### 3. Manual de Atualização (Skills Update)
Para garantir que a sua instância local ou global possui as últimas atualizações de segurança, novos comandos do Taste Engine e correções de governança:

```bash
# Verificar se existem atualizações disponíveis para as skills instaladas
npx skills check

# Atualizar todas as skills para a versão mais recente
npx skills update

# Para forçar a reinstalação e atualização manual de uma skill específica
npx skills add ruifrcosta/OMEGA-SKILL --force
```

---

## 🚀 MANUAL DE ATIVAÇÃO (PROMPTS E GATILHOS)

O OMEGA entra em execução de forma autónoma através de palavras-chave, ou pode ser convocado explicitamente utilizando prompts de engenharia principal ou comandos da CLI.

### A. Gatilhos de Ativação Rápida
O assistente ativará o OMEGA ao detetar qualquer um destes termos nas suas solicitações:
*   *Arquitetura*: "Desenhar ADR", "mapear bounded contexts", "aplicar CQRS", "blueprints do sistema".
*   *UI/UX*: "Interface minimalista", "escala OKLCH", "polir interface", "estética Stripe/Vercel", "Bento Grid".
*   *Governança/PMO*: "Definir modelo de delivery", "criar RACI", "esboçar execution plan", "mapear dependências".
*   *Segurança*: "Auditar CORS", "aplicar Zero Trust", "checklist OWASP", "criptografar senhas".

---

### B. Prompts Prontos para Ativar a Skill

#### 🟢 Prompt 1: Scaffolding de Novo Projeto (Modelo PMO Híbrido)
> *"Usa a skill OMEGA para inicializar a estrutura PMO completa do meu projeto. Deteta a minha stack e cria os 18 arquivos mandatórios de raiz (PROJECT_GOVERNANCE, DELIVERY_MODEL, etc.) aplicando governança baseada em risco."*

#### 🔵 Prompt 2: Engenharia Frontend (Taste Engine & OKLCH)
> *"Usa a skill OMEGA para desenhar uma dashboard de produto. Aplica o Taste Engine com dials (Variance: 3, Motion: 5, Density: 4). Garanta contraste absoluto usando cores OKLCH e respeite a regra 'Sem Cartões'."*

#### 🔴 Prompt 3: Auditoria Crítica de Arquitetura e Segurança
> *"OMEGA, entra em Critical Engineering Review Mode. Faz uma auditoria completa na minha API e banco de dados. Quero portões de severidade ativados e validação contra o OWASP Top 10."*

#### 🟡 Prompt 4: Sincronismo e Alinhamento de Memória
> *"Usa a skill OMEGA para atualizar o Memory Bank. Executa o drift detection comparando a implementação atual do código com os ficheiros activeContext.md e progress.md."*

---

## 🏛️ OS TRÊS PILARES DA ENGENHARIA OMEGA

### 🚦 Pilar I — Governança Crítica (Review Mode & Gates)
Sempre que uma arquitetura ou stack é definida, o OMEGA ativa o **Critical Engineering Review Mode**:
1.  **Diagnóstico Interno**: Avalia se a arquitetura proposta suporta escala 10x e detecta complexidades artificiais ou teatralidades de microsserviços.
2.  **Portões de Decisão (Severity Gates)**:
    *   **🔴 CRITICAL** (Falha de segurança, quebra de DDD ou risco de perda de dados): **Bloqueia a execução** imediatamente, relata o problema e exige correção de design.
    *   **🟡 HIGH** (Subotimização sob carga ou workarounds complexos): **Alerta e propõe** uma solução de engenharia opinada e aguarda confirmação rápida.
    *   **🟢 MEDIUM** (Débito técnico controlável): **Gera um TODO** no arquivo de progresso e continua a execução.
    *   **🔵 LOW** (Melhoria cosmética ou de comentários): **Avança silenciosamente**.

### 🏢 Pilar II — Universal PMO Governance Operating System
Gerenciamento de entregas de nível corporativo adaptado para múltiplos frameworks:
*   **Maturidade e Risco**: O OMEGA ajusta a densidade documental e o controlo com base na criticidade e regulamentação (Waterfall para alta conformidade, Agile para descoberta contínua, Hybrid para transição de legados).
*   **AI-Native PMO**: Varreduras inteligentes para prever gargalos de entrega, scope creep e fadiga cognitiva de equipes antes de virar um incidente.

### 🧠 Pilar III — Decoupled 6-Core Memory Bank
Para garantir persistência em sessões stateless, o OMEGA descentraliza a memória da skill e a armazena diretamente no repositório de trabalho do usuário (`memory-bank/`):
1.  `projectbrief.md` — Requisitos fundamentais e escopo.
2.  `productContext.md` — O porquê e as metas de experiência do utilizador.
3.  `systemPatterns.md` — Blueprints e padrões de arquitetura (DDD, CQRS).
4.  `techContext.md` — Stack, infraestrutura, versões e limitações do ambiente.
5.  `activeContext.md` — Foco do sprint atual, decisões e lições aprendidas.
6.  `progress.md` — Status das tarefas (`[ ]` planeado, `[/]` em progresso, `[x]` concluído).

---

## 🛠️ CATÁLOGO COMPLETO DE COMANDOS (IMPECCABLE VOCABULARY)

O OMEGA possui 23 comandos estáticos de refinamento visível e tomada de decisão:

| Comando | Domínio | Raciocínio de Engenharia |
|---|---|---|
| **`craft [funcionalidade]`** | Construção | Planeia, desenha a UX e constrói a funcionalidade de ponta a ponta. |
| **`shape [funcionalidade]`** | Arquitetura UI | Esboça o fluxo de tela e layouts baseados em espaçamento 4/8dp antes do código. |
| **`critique [alvo]`** | Avaliação UX | Pontuação heurística de usabilidade e detecção de padrões genéricos. |
| **`polish [alvo]`** | Refinamento | Ajustes finais em transições de micro-interações e alinhamento tipográfico. |
| **`audit [alvo]`** | Qualidade | Varredura de acessibilidade (a11y), Core Web Vitals e conformidade estrutural. |
| **`bolder [alvo]`** | Expressão | Adiciona contraste visual e pesos tipográficos a interfaces excessivamente neutras. |
| **`quieter [alvo]`** | Contenção | Remove ruídos visuais, containers desnecessários e reduz a densidade da tela. |
| **`distill [alvo]`** | Simplicidade | Remove complexidades de código, abstrações redundantes e loops prematuros. |
| **`harden [alvo]`** | Robustez | Adiciona tratamento estrito de erros, internacionalização e testes de estresse. |
| **`live`** | Live Server | Abre uma sessão em tempo real no navegador para testar variantes visuais. |

---

## 📂 O COFRE PMO: ÍNDICE DE 18 ARQUIVOS MANDATÓRIOS

Os projetos sob a governança do OMEGA mantêm em sua raiz de trabalho a seguinte matriz de indexação de entrega e conformidade:

| Arquivo | Função de Engenharia |
|---|---|
| **[PROJECT_GOVERNANCE.md](file:///PROJECT_GOVERNANCE.md)** | RACI, modelo de escalonamento, governança baseada em risco e assinaturas. |
| **[DELIVERY_MODEL.md](file:///DELIVERY_MODEL.md)** | Justificativa do framework, cadência das cerimónias, branching e rollback. |
| **[EXECUTION_PLAN.md](file:///EXECUTION_PLAN.md)** | Backlog unificado, sequenciamento de milestones e análise de caminho crítico. |
| **[PROJECT_STATUS.md](file:///PROJECT_STATUS.md)** | Estado atual do sprint, gráficos de burn-down e impedimentos ativos. |
| **[ROADMAP.md](file:///ROADMAP.md)** | Linha do tempo estratégica de releases e entregas por época. |
| **[RISKS.md](file:///RISKS.md)** | Matriz de probabilidade e impacto de riscos técnicos e de negócio. |
| **[DECISIONS.md](file:///DECISIONS.md)** | Log histórico de tomadas de decisão e links rápidos para os ADRs ativos. |
| **[CHANGELOG.md](file:///CHANGELOG.md)** | Ficheiro de versionamento público dos incrementos entregues. |
| **[TEAM_STRUCTURE.md](file:///TEAM_STRUCTURE.md)** | Alocação de papéis, lideranças e equipes multidisciplinares (squads). |
| **[DEPENDENCIES.md](file:///DEPENDENCIES.md)** | Mapa de bloqueadores de terceiros, pacotes e acoplamentos sistémicos. |
| **[RELEASE_PLAN.md](file:///RELEASE_PLAN.md)** | Protocolo de publicação de pacotes e gating de segurança pré-produção. |
| **[ARCHITECTURE_STATUS.md](file:///ARCHITECTURE_STATUS.md)** | Auditoria e integridade da separação física de bounded contexts. |
| **[TECH_STACK_ANALYSIS.md](file:///TECH_STACK_ANALYSIS.md)** | Análise auto-detetada de frameworks, ORMs, custos e bibliotecas obsoletas. |
| **[COST_ANALYSIS.md](file:///COST_ANALYSIS.md)** | FinOps, custos de infraestrutura em nuvem e token savings. |
| **[WORKFLOW_ENGINE.md](file:///WORKFLOW_ENGINE.md)** | CI/CD scripts de pipelines e validações automatizadas de builds. |
| **[QA_STATUS.md](file:///QA_STATUS.md)** | Cobertura de testes, k6 benchmark e modelos de combinatória de testes PICT. |
| **[SECURITY_STATUS.md](file:///SECURITY_STATUS.md)** | Modelos de ameaças ativas, logs RBAC e validação contra o OWASP Top 10. |
| **[OBSERVABILITY_STATUS.md](file:///OBSERVABILITY_STATUS.md)** | Monitoramento, SLOs mapeados e dashboards recomendados no Grafana. |

---

## 🎨 O MOTOR DE ESTÉTICA E DIALS VISUAIS

OMEGA rejeita frameworks e layouts genéricos ("AI slop") e força um rigoroso motor de estética baseado em três dials parametrizáveis:

```css
/* Dials de Design OMEGA */
DESIGN_VARIANCE   3  /* 1 = Simétrico/Linear  ↔  10 = Caótico/Asimétrico */
MOTION_INTENSITY  5  /* 1 = Estático          ↔  10 = Cinematográfico */
VISUAL_DENSITY    4  /* 1 = Galeria de Arte   ↔  10 = Cockpit */
```

### Paleta Curada HSL/OKLCH por Domínio
*   **Healthcare**: DM Sans/Figtree • tons de esmeralda (`#059669` / `#34D399`)
*   **Finance**: IBM Plex Sans • tons sóbrios de azul (`#1D4ED8` / `#60A5FA`)
*   **Productivity**: Geist/Geist Mono • tons de violeta (`#7C3AED` / `#A78BFA`)

### Curvas de Easing Não-Lineares (Banish transition: all)
```css
/* Transições suaves e profissionais */
--ease-out:    cubic-bezier(0.23, 1, 0.32, 1);
--ease-inout:  cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

---

_OMEGA v2.0 • Relentless Engineering & PMO Governance Operating System • Permanent Memory Bank_
