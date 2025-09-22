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
Analise o seguinte texto de requisitos e gere Histórias de Usuário bem estruturadas seguindo o padrão:

"Como [tipo de usuário], eu quero [funcionalidade] para que [benefício]"

REQUISITOS:
{requirements}

INSTRUÇÕES:
1. Identifique todos os tipos de usuários mencionados
2. Extraia as funcionalidades principais
3. Para cada funcionalidade, crie uma História de Usuário clara e específica
4. Inclua critérios de aceitação quando apropriado
5. Organize as histórias por prioridade ou módulo
6. Use linguagem clara e objetiva
7. Certifique-se de que cada história seja testável e implementável

FORMATO DE SAÍDA:
Para cada História de Usuário, inclua:
- Título da História
- História no formato padrão
- Critérios de aceitação (se aplicável)
- Prioridade (Alta/Média/Baixa)
- Estimativa de esforço (1-5 pontos)

Gere as Histórias de Usuário agora:
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
