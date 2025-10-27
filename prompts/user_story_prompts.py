"""
Templates de prompts para geração e análise de Histórias de Usuário.
"""

from typing import Dict, Any


class UserStoryPrompts:
    """Classe com templates de prompts para Histórias de Usuário."""
    
    @staticmethod
    def generate_user_stories_from_requirements(requirements: str) -> str:
        """
        Gera prompt para criar Histórias de Usuário a partir de requisitos.
        
        Args:
            requirements: Texto dos requisitos
            
        Returns:
            Prompt formatado
        """
        return f"""
# CONTEXTO E OBJETIVO DO AGENTE
Você é um **analista de requisitos sênior** e especialista em **escrita de histórias de usuário para desenvolvimento de software**, com ampla experiência em levantamento de requisitos, análise funcional, UX e boas práticas ágeis (Scrum, Kanban e Lean).

Sua missão neste projeto é **criar, organizar e refinar histórias de usuário para o sistema ProgressoGov**, garantindo consistência, clareza e testabilidade. O conteúdo pode ser uma transcrição de reunião, um texto feito pelo cliente, uma demanda grande envolvendo criação de toda uma tela, uma parte de uma tela, ou funcionalidades impactadas. Você deve entregar TODAS as histórias de usuário envolvidas na solicitação.

---

# CONTEÚDO DA TRANSCRIÇÃO/REQUISITOS:

{requirements}

---

# FORMATO OBRIGATÓRIO PARA CADA HISTÓRIA DE USUÁRIO

## 1. **Nome da História de Usuário**

* Dê um nome objetivo e único para a história, no formato [Funcionalidade] – [Ação principal]. 
* Exemplo: Entrega – Cadastro de nova entrega.

---

## 2. **Padrão de História de Usuário**
Sempre escreva a história de usuário no formato:

> Como [tipo de usuário], quero [funcionalidade] para [benefício esperado].

---

## 3. **Tipo**

> Feature / Melhoria / Bug / Enabler.

---

## 4. **Critérios de Aceitação**

* Devem ser objetivos, claros e verificáveis.
* Sempre numerados (1, 2, 3...).
* Representam as condições de sucesso da história.
* Devem estar diretamente vinculados à história, evitando repetir regras de negócio ou requisitos técnicos.

---

## 5. **Permissões e Acessos**

* Lista clara das permissões necessárias para acessar ou executar cada ação da história.
* Sempre indicar se a ação é **restrita (somente quem tem permissão)** ou **liberada (qualquer usuário com login)**.
* Exemplo de formato:

> - **Consultar Projetos**: permite visualizar lista e detalhes de projetos.
> - **Manter Projetos**: permite criar, editar e excluir.
> - **Exportar Relatórios**: permite exportar dados em PDF/Excel.

**IMPORTANTE**: Sempre considere diferentes papéis de usuário:
- **Leitor**: capaz apenas de consultar dados, sem alterar ou criar nenhum registro ou manter dados
- **Gestor**: capaz de manter dados
- **Alta gestão**: representado pelo Governador do Estado e outros secretários de alto escalão. Possuem usuário leitor de múltiplos órgãos

---

## 6. **Regras de Negócios**

* Descrevem políticas, restrições ou exceções impostas pelo negócio.
* Exemplos: cálculos específicos, hierarquia de permissões, periodicidade obrigatória, prazos fixos.

---

## 7. **Requisitos Técnicos**

* Aspectos de implementação ou arquitetura que impactam a história.
* Exemplos: integração com API externa, criptografia de dados, compatibilidade com navegadores, performance mínima, uso de banco de dados específico.
* Se nenhum foi identificado através das informações passadas, informe: "Nenhum requisito técnico foi identificado."

---

## 8. **Regras de Interface**

* Definem o comportamento esperado dos componentes da tela.
* Ex.: botões habilitados/desabilitados, validações em tempo real, elementos fixos, mensagens de erro.

---

## 9. **Campos e Componentes de UI**

* Deve ser apresentado em **formato de tabela**.
* A tabela deve ser entregue em formato Markdown, para garantir fácil leitura e exportação.
* Cada linha da tabela representa um campo ou componente da tela.
* As colunas da tabela devem incluir, no mínimo:

  * **Campo** (nome do campo/componente)
  * **Tipo** (texto curto, texto longo, lista, calendário, etc.)
  * **Obrigatório** (Sim/Não)
  * **Regra/Restrição** (limite de caracteres, unicidade, formatos aceitos, etc.)
* Se necessário, podem ser adicionadas colunas extras, como **Máscara/Validação** ou **Valor Padrão**.

**Exemplo de tabela Markdown:**

| Campo | Tipo | Obrigatório | Regra/Restrição |
|-------|------|-------------|------------------|
| Nome do Projeto | Texto curto | Sim | Máximo 100 caracteres |
| Data de Início | Calendário | Sim | Data não pode ser no passado |
| Status | Lista | Sim | Valores: Ativo, Inativo, Pendente |

---

## 10. **Cenários de Teste**
Formato *BDD (Behavior Driven Development)*. São usados para detalhar a validação prática dos critérios de aceitação:

* **Dado** [contexto inicial]
* **Quando** [ação executada]
* **Então** [resultado esperado]

---

# BOAS PRÁTICAS QUE VOCÊ DEVE APLICAR

1. **Sempre considerar diferentes papéis de usuário**: Leitor, Gestor e Alta gestão (conforme detalhado na seção 5).
2. **Evitar ambiguidades**: Se algo não estiver claro, assinale isso na resposta.
3. **Garantir que cada história seja INVEST**: **I**ndependente, **N**egociável, **V**aliosa, **E**stimável, **P**equena e **T**estável.
4. **Se uma história está grande demais**, sugira como dividi-la em menores.
5. **Se houver relações entre histórias**, aponte dependências e ordem necessária de execução.
6. **Sugerir ao final quais tipos de task devem ser criadas** (Backend, Frontend, Design, Dados, QA), de forma a ajudar na criação de tasks que o time de desenvolvimento precisará criar.
7. **Se perceber possíveis complicações técnicas**, detalhe-as e dê sugestões de possíveis soluções ou caminhos a seguir.
8. **Se a demanda for de evolução/alteração**, destaque tais alterações, de forma que o time tenha a história completa, mas que saiba o que precisa ser feito especificamente.

---

# SAÍDA ESPERADA PARA CADA SOLICITAÇÃO

Para cada História de Usuário gerada, você deve fornecer:

1. **Nome da História de Usuário** (formato [Funcionalidade] – [Ação principal])
2. **História de usuário** (formato "Como [tipo de usuário], quero [funcionalidade] para [benefício esperado]")
3. **Tipo** (Feature / Melhoria / Bug / Enabler)
4. **Critérios de aceitação** (numerados e verificáveis)
5. **Permissões e Acessos** (considerando Leitor, Gestor e Alta gestão)
6. **Regras de Negócios**
7. **Requisitos Técnicos**
8. **Regras de Interface**
9. **Campos e Componentes de UI** (em formato de tabela Markdown)
10. **Cenários de Teste** (formato BDD: Dado/Quando/Então)

**IMPORTANTE**: 
- Se houver múltiplas histórias, entregue TODAS elas no mesmo formato.
- Se perceber dependências entre histórias, aponte-as claramente.
- Ao final, sugira os tipos de tasks que devem ser criadas (Backend, Frontend, Design, Dados, QA).

Agora, analise o conteúdo fornecido e gere todas as Histórias de Usuário seguindo rigorosamente este formato.
        """.strip()
    
    @staticmethod
    def analyze_existing_user_stories(user_stories: str) -> str:
        """
        Gera prompt para analisar Histórias de Usuário existentes.
        
        Args:
            user_stories: Texto das Histórias de Usuário
            
        Returns:
            Prompt formatado
        """
        return f"""
Analise as seguintes Histórias de Usuário e forneça uma avaliação detalhada:

HISTÓRIAS DE USUÁRIO:
{user_stories}

ANÁLISE SOLICITADA:
1. Qualidade das Histórias:
   - Estão no formato correto?
   - São específicas e testáveis?
   - Têm critérios de aceitação claros?

2. Cobertura de Funcionalidades:
   - Todas as funcionalidades principais estão cobertas?
   - Há lacunas ou funcionalidades faltando?
   - As histórias cobrem diferentes tipos de usuários?

3. Estrutura e Organização:
   - Estão bem organizadas por prioridade?
   - Há dependências entre histórias?
   - A estimativa de esforço está adequada?

4. Sugestões de Melhoria:
   - Histórias que precisam ser refinadas
   - Histórias que podem ser divididas
   - Histórias que podem ser combinadas
   - Critérios de aceitação adicionais necessários

5. Recomendações:
   - Próximos passos para o desenvolvimento
   - Priorização sugerida
   - Considerações técnicas importantes

Forneça uma análise detalhada e construtiva:
        """.strip()
    
    @staticmethod
    def refine_user_story(user_story: str) -> str:
        """
        Gera prompt para refinar uma História de Usuário específica.
        
        Args:
            user_story: História de Usuário a ser refinada
            
        Returns:
            Prompt formatado
        """
        return f"""
Refine a seguinte História de Usuário para torná-la mais clara, específica e testável:

HISTÓRIA ORIGINAL:
{user_story}

CRITÉRIOS DE REFINAMENTO:
1. Formato Padrão:
   - "Como [tipo de usuário], eu quero [funcionalidade] para que [benefício]"
   - Use linguagem clara e objetiva
   - Evite jargões técnicos desnecessários

2. Especificidade:
   - Seja específico sobre o que o usuário quer fazer
   - Inclua detalhes relevantes sobre o contexto
   - Evite ambiguidades

3. Testabilidade:
   - A história deve ser testável
   - Inclua critérios de aceitação claros
   - Defina o que significa "concluído"

4. Valor de Negócio:
   - O benefício deve ser claro e mensurável
   - Deve agregar valor real ao usuário
   - Deve estar alinhado com os objetivos do produto

5. Tamanho Adequado:
   - Deve ser implementável em uma iteração
   - Se muito grande, divida em histórias menores
   - Se muito pequena, considere combinar com outras

Forneça:
1. História refinada
2. Critérios de aceitação detalhados
3. Exemplos de cenários de teste
4. Justificativa das mudanças feitas
        """.strip()
    
    @staticmethod
    def generate_acceptance_criteria(user_story: str) -> str:
        """
        Gera prompt para criar critérios de aceitação para uma História de Usuário.
        
        Args:
            user_story: História de Usuário
            
        Returns:
            Prompt formatado
        """
        return f"""
Crie critérios de aceitação detalhados para a seguinte História de Usuário:

HISTÓRIA DE USUÁRIO:
{user_story}

REQUISITOS PARA OS CRITÉRIOS:
1. Especificidade:
   - Sejam específicos e mensuráveis
   - Incluam cenários de sucesso e falha
   - Sejam testáveis por desenvolvedores e testadores

2. Cobertura:
   - Cubram todos os aspectos da funcionalidade
   - Incluam validações de entrada
   - Considerem casos extremos e edge cases

3. Formato:
   - Use linguagem clara e objetiva
   - Comece com "Dado que", "Quando", "Então" quando apropriado
   - Seja conciso mas completo

4. Cenários:
   - Cenário principal (happy path)
   - Cenários alternativos
   - Cenários de erro
   - Validações de segurança (se aplicável)

5. Critérios de Qualidade:
   - Performance esperada
   - Usabilidade
   - Acessibilidade (se aplicável)
   - Compatibilidade

Forneça os critérios de aceitação organizados por categoria:
        """.strip()
    
    @staticmethod
    def estimate_user_story_effort(user_story: str) -> str:
        """
        Gera prompt para estimar o esforço de uma História de Usuário.
        
        Args:
            user_story: História de Usuário
            
        Returns:
            Prompt formatado
        """
        return f"""
Estime o esforço de desenvolvimento para a seguinte História de Usuário:

HISTÓRIA DE USUÁRIO:
{user_story}

FATORES A CONSIDERAR:
1. Complexidade Técnica:
   - Integração com sistemas existentes
   - Algoritmos complexos
   - Manipulação de dados
   - APIs externas

2. Complexidade de Interface:
   - Design de UI/UX
   - Responsividade
   - Acessibilidade
   - Interações complexas

3. Complexidade de Negócio:
   - Regras de negócio complexas
   - Validações múltiplas
   - Workflows elaborados
   - Integrações com processos

4. Riscos e Dependências:
   - Dependências externas
   - Riscos técnicos
   - Dependências de outras histórias
   - Conhecimento da equipe

ESCALA DE ESTIMATIVA (Pontos de Story):
- 1 ponto: Muito simples (1-2 horas)
- 2 pontos: Simples (2-4 horas)
- 3 pontos: Médio (4-8 horas)
- 5 pontos: Complexo (1-2 semanas)
- 8 pontos: Muito complexo (2-3 semanas)
- 13 pontos: Extremamente complexo (3+ semanas)

Forneça:
1. Estimativa em pontos
2. Justificativa da estimativa
3. Principais fatores que influenciaram
4. Riscos identificados
5. Sugestões para reduzir complexidade (se aplicável)
        """.strip()
    
    @staticmethod
    def get_prompt_templates() -> Dict[str, str]:
        """
        Retorna todos os templates de prompt disponíveis.
        
        Returns:
            Dicionário com os templates
        """
        return {
            "generate_from_requirements": "Gerar Histórias de Usuário a partir de requisitos",
            "analyze_existing": "Analisar Histórias de Usuário existentes",
            "refine_story": "Refinar uma História de Usuário específica",
            "generate_acceptance_criteria": "Gerar critérios de aceitação",
            "estimate_effort": "Estimar esforço de desenvolvimento"
        }
