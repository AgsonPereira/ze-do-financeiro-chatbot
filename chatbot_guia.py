# chatbot_guia.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import traceback # Para imprimir o traceback completo do erro, se necessário
from flask import Flask, request, jsonify, render_template

# --- Carregar variáveis de ambiente do arquivo .env ---
load_dotenv()

# --- Configuração Inicial do Flask ---
app = Flask(__name__)

# --- Persona e Conteúdo do Chatbot ---
NOME_CHATBOT = "Zé do Financeiro"

# --- Configuração da API Key do Gemini ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODELO_GEMINI = None # Inicializa como None

if not GOOGLE_API_KEY:
    print(f"[{NOME_CHATBOT}] ALERTA: Chave da API do Google (GOOGLE_API_KEY) não encontrada no arquivo .env! {NOME_CHATBOT} vai operar em modo limitado, sem acesso ao Gemini.")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print(f"[{NOME_CHATBOT}] API Key do Gemini configurada com sucesso!")
        MODELO_GEMINI = genai.GenerativeModel('gemini-1.5-flash') # Ou 'gemini-pro'
        print(f"[{NOME_CHATBOT}] Modelo Gemini '{MODELO_GEMINI.model_name}' carregado e pronto pra desenrolar!")
    except Exception as e:
        print(f"[{NOME_CHATBOT}] Oxe! Deu um erro ao configurar o Gemini ou carregar o modelo: {e}")
        print(f"[{NOME_CHATBOT}] Detalhes do erro: {traceback.format_exc()}")
        print(f"[{NOME_CHATBOT}] Verifique sua API Key, conexão com a internet e se o modelo está disponível.")
        GOOGLE_API_KEY = None 
        MODELO_GEMINI = None


def saudacao_inicial():
    return f"Chegue mais, meu patrão/minha patroa! Sou o {NOME_CHATBOT}, seu parceiro aqui de Alagoas pra gente desenrolar as finanças do seu negócio. Pode perguntar o significado de termos financeiros, sobre Pix e Maquininha, dicas de 'Caixa Forte', ou pedir a 'lista de termos' que eu já aprendi!"

glossario_local_do_ze = {
    "mei": f"Aí sim, patrão/patroa! MEI é o Microempreendedor Individual. É tipo um atalho pra você que trampa por conta própria ter seu CNPJ, emitir nota, essas paradas todas... Sou o {NOME_CHATBOT} e tô aqui pra ajudar!",
    "cnpj": f"CNPJ, meu consagrado(a), é o Cadastro Nacional da Pessoa Jurídica. É tipo o CPF, só que pra sua empresa...",
    "conta pj": f"Conta PJ é uma conta no banco feita especialmente pra sua empresa, separada da sua conta pessoal...",
    "pix": f"O Pix (quando não estamos falando da comparação com maquininha) é aquele jeito ligeiro e quase sempre de graça pra gente pequena mandar e receber dinheiro. Cai na hora!",
    "qr code": f"QR Code (no contexto geral, não apenas de Pix) é tipo um código de barras moderninho, um quadradinho cheio de quadradinhos menores...",
    "fluxo de caixa": f"Fluxo de caixa (o termo geral, viu? Temos um módulo só pra dicas de como fazer o seu!) é o controle de toda grana que entra e sai do seu negócio...", # Ajustado para não confundir com o módulo
    "capital de giro": f"Capital de giro é aquela reserva esperta que você precisa ter pra manter o negócio funcionando no dia a dia...",
    "microcrédito": f"Microcrédito é um tipo de empréstimo com valor mais baixo, pensado pra ajudar o pequeno empreendedor..."
}

def explicar_termo_com_gemini(termo_usuario):
    if not GOOGLE_API_KEY or not MODELO_GEMINI:
        print(f"[{NOME_CHATBOT}] Tentativa de usar Gemini para '{termo_usuario}', mas não está configurado/disponível.")
        return f"Oxe, meu sistema de consulta avançada (Gemini) não tá configurado ou deu chabu na inicialização. {NOME_CHATBOT} não conseguiu procurar por '{termo_usuario}' agora."

    prompt = f"""
Você é o {NOME_CHATBOT}, um assistente financeiro digital super gente boa, com um forte sotaque e carisma de Alagoas, Maceió.
Sua missão é explicar termos financeiros de forma SIMPLES, CURTA, AMIGÁVEL e DIRETA para microempreendedores e trabalhadores autônomos.
Use uma linguagem popular e expressões regionais de Alagoas (como 'meu rei', 'minha rainha', 'visse?', 'arretado', 'desenrolar', 'aperreio', 'mangar', 'deixe de pantim', 'catita', 'buliçoso').
Explique o seguinte termo: '{termo_usuario}'

Mantenha a explicação em no máximo 3 ou 4 frases curtas.
Seja positivo e encorajador.
Evite formalidades e termos muito técnicos na explicação.
Se o termo for muito complexo, não parecer financeiro, ou se você não tiver certeza da resposta, pode dizer que esse o {NOME_CHATBOT} ainda não aprendeu direito ou que precisa estudar mais um cadinho, mas sempre de um jeito engraçado e alagoano. Não invente informações se não tiver certeza.
"""
    try:
        print(f"[{NOME_CHATBOT}] Enviando o termo '{termo_usuario}' para o Gemini...")
        generation_config = genai.types.GenerationConfig(temperature=0.7)
        response = MODELO_GEMINI.generate_content(prompt, generation_config=generation_config)
        print(f"[{NOME_CHATBOT}] Resposta recebida do Gemini para '{termo_usuario}'.")

        text_result = None
        if hasattr(response, 'text') and response.text and isinstance(response.text, str):
            text_result = response.text
        elif hasattr(response, 'parts') and response.parts:
            all_parts_text = "".join(part.text for part in response.parts if hasattr(part, 'text') and isinstance(part.text, str))
            if all_parts_text: text_result = all_parts_text
        elif hasattr(response, 'candidates') and response.candidates and \
             hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts') and \
             response.candidates[0].content.parts:
            all_parts_text_candidates = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and isinstance(part.text, str))
            if all_parts_text_candidates: text_result = all_parts_text_candidates
        
        if text_result and text_result.strip():
            final_explanation = text_result.strip()
            print(f"[{NOME_CHATBOT}] Explicação do Gemini para '{termo_usuario}': {final_explanation}")
            return final_explanation
        else:
            block_reason_msg = ""
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and \
               hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                block_reason = response.prompt_feedback.block_reason
                block_reason_msg = f"Motivo do bloqueio: {block_reason}."
                print(f"[{NOME_CHATBOT}] A solicitação para '{termo_usuario}' foi bloqueada pelo Gemini. {block_reason_msg}")
                if hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'safety_ratings'):
                    safety_info = f" (Safety Ratings: {response.candidates[0].safety_ratings})"
                    block_reason_msg += safety_info
                return f"Oxe, meu patrão/minha patroa! O sistema avançado não quis falar sobre '{termo_usuario}'. {block_reason_msg} Vamos tentar outro?"
            
            print(f"[{NOME_CHATBOT}] Resposta do Gemini para '{termo_usuario}' veio vazia ou em formato não reconhecido. {block_reason_msg} Resposta completa: {vars(response) if hasattr(response, '__dict__') else response}")
            return f"Eita gota! O {NOME_CHATBOT} tentou desenrolar sobre '{termo_usuario}' com o sistema avançado, mas a resposta veio meio... em branco ou esquisita. {block_reason_msg} Parece que nem ele pegou a ideia dessa vez. Que tal outro termo?"
    except Exception as e:
        print(f"[{NOME_CHATBOT}] Deu um erro arretado ao tentar falar com o Gemini sobre '{termo_usuario}': {e}\n{traceback.format_exc()}")
        return f"Rapaz, deu um piripaque daqueles na minha conexão com o sistema avançado pra explicar '{termo_usuario}'. A antena deve ter caído! Tenta de novo daqui a pouquinho. (Detalhe do erro: {type(e).__name__})"

def modulo_pix_maquininha(mensagem_usuario_original):
    print(f"[{NOME_CHATBOT}] Entrou no módulo Pix ou Maquininha.")
    resposta_base = f"""
Opa, meu patrão/minha patroa! Chegou na dúvida cruel: Pix ou Maquininha? Relaxe que o {NOME_CHATBOT} te dá o papo reto pra você não entrar em nenhuma roubada! 💸

**PIX: O Ligeirinho Querido** 🚀
O Pix é aquele parceiro que chegou pra facilitar a vida, visse?
* **Grana na Hora:** Vendeu, recebeu! O dinheiro cai na sua conta rapidinho, sem choro nem vela.
* **Custo Baixo (ou Zero!):** Pra gente que é MEI ou pequeno negócio, muitas vezes não tem taxa nenhuma pra receber via Pix. É economia na certa!
* **Facinho de Usar:** Com Chave Pix (CPF/CNPJ, celular, e-mail) ou QR Code, seu cliente te paga num instante.

**MAQUININHA: A Boa e Velha Companheira** 💳
A maquininha ainda tem seu valor!
* **Mais Opções pro Cliente:** Aceita cartão de débito, crédito e até parcelado.
* **Vendas Parceladas:** Quer vender aquele produto mais caro? Com a maquininha, o cliente pode parcelar.

**E AS TAXAS DA MAQUININHA, ZÉ?** 😥
Fique de olho! A maquininha tem:
* **Custo da Máquina:** Compra ou aluguel.
* **Taxa por Venda (MDR):** Um percentual sobre cada venda. Varia MUITO!
* **Prazo pra Receber:** O dinheiro do crédito pode demorar. Antecipar tem taxa.

**{NOME_CHATBOT} AJUDA A DECIDIR:** 🤔
1.  **Sua Clientela:** Preferem Pix ou cartão?
2.  **Volume de Vendas:** Muitas vendas com valor alto? Taxas da maquininha podem pesar.
3.  **Compare Custos:** Pesquise taxas de maquininhas e compare com o Pix.
4.  **Use os Dois!** Muitas vezes, ter Pix (barato) e maquininha (opções) é o ideal.

Ficou mais claro? Se tiver dúvida específica, tipo sobre taxas ou como gerar QR Code, manda que o {NOME_CHATBOT} e o Gemini tentam te ajudar!
"""
    return resposta_base

# No seu arquivo chatbot_guia.py, substitua a função modulo_caixa_forte por esta:

def modulo_caixa_forte(mensagem_usuario_original):
    print(f"[{NOME_CHATBOT}] Entrou no módulo Caixa Forte, Negócio Forte. Mensagem: '{mensagem_usuario_original}'")
    mensagem_lower = mensagem_usuario_original.lower().strip()

    # Gatilhos genéricos que indicam um pedido pela informação base do módulo
    gatilhos_base = [
        "caixa forte", "controle financeiro", "organizar finanças", 
        "gestão financeira", "saúde financeira", "dicas de caixa"
    ]

    # Verifica se a mensagem do usuário é muito similar a um gatilho base (indicando que ele quer a info geral)
    # ou se é uma pergunta mais específica.
    # Se a mensagem for EXATAMENTE um dos gatilhos base, ou muito curta e um gatilho, mostra info base.
    eh_pedido_base = False
    for gatilho in gatilhos_base:
        if mensagem_lower == gatilho:
            eh_pedido_base = True
            break
    
    # Se não for um pedido base exato, mas ainda contém um gatilho, pode ser uma pergunta específica.
    # Vamos considerar uma pergunta específica se ela for mais longa que os gatilhos simples.
    if not eh_pedido_base and any(gatilho in mensagem_lower for gatilho in gatilhos_base) and len(mensagem_lower.split()) > 3:
        # É uma pergunta específica dentro do tema Caixa Forte, vamos usar o Gemini
        print(f"[{NOME_CHATBOT}] 'Caixa Forte': Recebida pergunta específica: '{mensagem_usuario_original}'. Usando Gemini.")
        
        if not GOOGLE_API_KEY or not MODELO_GEMINI:
            return f"Oxe, meu sistema avançado tá cochilando agora. Mas sobre '{mensagem_usuario_original}', lembre das dicas básicas de separar as contas e anotar tudo, visse?"

        prompt_gemini = f"""
Você é o {NOME_CHATBOT}, um consultor financeiro gente boa de Alagoas, Maceió.
Um microempreendedor já conhece as dicas gerais sobre 'Caixa Forte e Negócio Forte' e agora tem uma pergunta mais específica sobre controle financeiro.
A pergunta do empreendedor é: '{mensagem_usuario_original}'

Sua tarefa é responder a esta pergunta específica de forma clara, simples, prática e curta (no máximo 4-5 frases).
Mantenha seu sotaque e expressões regionais de Alagoas (como 'meu rei', 'minha rainha', 'visse?', 'arretado', 'desenrolar', 'aperreio').
Seja positivo, encorajador e direto ao ponto. Se a pergunta for muito complexa para uma resposta curta ou fora do seu alcance de conhecimento prático para um MEI, diga que vai precisar estudar mais um cadinho ou sugira simplificar a pergunta, sempre no seu estilo.
Não invente dados específicos de bancos ou taxas, fale de forma geral e prática.
Por exemplo, se perguntarem sobre 'como fazer planilha', dê passos simples ou sugira colunas básicas.
"""
        try:
            print(f"[{NOME_CHATBOT}] 'Caixa Forte': Enviando pergunta específica para o Gemini: '{mensagem_usuario_original}'")
            generation_config = genai.types.GenerationConfig(temperature=0.7)
            response = MODELO_GEMINI.generate_content(prompt_gemini, generation_config=generation_config)
            
            text_result = None
            # ... (lógica de extração de texto da resposta do Gemini, igual à da função explicar_termo_com_gemini)
            if hasattr(response, 'text') and response.text and isinstance(response.text, str):
                text_result = response.text
            elif hasattr(response, 'parts') and response.parts:
                all_parts_text = "".join(part.text for part in response.parts if hasattr(part, 'text') and isinstance(part.text, str))
                if all_parts_text: text_result = all_parts_text
            elif hasattr(response, 'candidates') and response.candidates and \
                 hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts') and \
                 response.candidates[0].content.parts:
                all_parts_text_candidates = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and isinstance(part.text, str))
                if all_parts_text_candidates: text_result = all_parts_text_candidates
            
            if text_result and text_result.strip():
                resposta_especifica = text_result.strip()
                print(f"[{NOME_CHATBOT}] 'Caixa Forte': Resposta do Gemini para pergunta específica: {resposta_especifica}")
                return resposta_especifica
            else:
                # ... (lógica de tratamento de bloqueio ou resposta vazia, igual à da função explicar_termo_com_gemini)
                block_reason_msg = ""
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                    block_reason = response.prompt_feedback.block_reason
                    block_reason_msg = f"Motivo do bloqueio: {block_reason}."
                print(f"[{NOME_CHATBOT}] 'Caixa Forte': Resposta do Gemini para pergunta específica veio vazia ou em formato não reconhecido. {block_reason_msg}")
                return f"Eita, meu camarada! Tentei buscar uma luz sobre '{mensagem_usuario_original}', mas o sistema avançado hoje tá meio nublado. Que tal tentar perguntar de um jeito mais simples ou focar num ponto por vez?"
        except Exception as e:
            print(f"[{NOME_CHATBOT}] 'Caixa Forte': Erro ao chamar Gemini para pergunta específica: {e}\n{traceback.format_exc()}")
            return f"Rapaz, deu um piripaque aqui tentando responder sobre '{mensagem_usuario_original}'. Minhas antenas pro sistema avançado devem estar precisando de um ajuste! Tenta de novo daqui a pouco."
        
    # Se não for uma pergunta específica (ou seja, é um pedido base), retorna o texto padrão.
    print(f"[{NOME_CHATBOT}] 'Caixa Forte': Respondendo com informações base.")
    resposta_base = f"""
E aí, meu patrão/minha patroa! Quer deixar o caixa da sua empresa forte como um touro e o negócio rendendo que é uma beleza? Então você tá falando com o {NOME_CHATBOT} certo! Bora organizar as finanças pra não ter mais aperreio e o dimdim sobrar no fim do mês! 💰💪

**1. {NOME_CHATBOT} Pergunta: Cadê o Dinheiro da Empresa e Cadê o Seu?**
Primeira lição, e a mais importante de todas, visse? **SEPARE as contas!** O dinheiro que entra das suas vendas é da EMPRESA. O seu salário (o famoso pró-labore) você tira da empresa e bota na sua conta PESSOAL. Misturar tudo é receita pra dor de cabeça! Uma conta PJ ajuda demais nisso.

**2. Anota Tudo, Freguesia por Freguesia, Despesa por Despesa!**
Tem que anotar TUDO que entra e TUDO que sai. Isso é o famoso **Fluxo de Caixa**.
* **Entradas (Receitas):** Dinheiro das vendas, serviços.
* **Saídas (Despesas/Custos):** Aluguel, fornecedor, seu pró-labore. Tem as **despesas fixas** (todo mês) e as **variáveis** (mudam com as vendas).

**3. Ferramentas pra te Ajudar nessa Missão:**
* **App do seu Banco:** Muitos já ajudam a categorizar gastos.
* **Planilha Financeira:** No Excel ou Google Sheets. Colunas: Data, Descrição, Entrada (R$), Saída (R$), Saldo (R$).
* **Aplicativos de Controle Financeiro:** Existem vários, alguns de graça.

**4. Pra que Serve esse Tal de Caixa Forte, Zé?**
Com as contas organizadas, você consegue:
* Saber pra onde o dinheiro tá indo.
* Ver se o preço do seu produto/serviço tá dando lucro.
* Planejar melhor e não entrar em dívida à toa.
* Dormir mais tranquilo!

E aí, deu pra clarear? Se tiver alguma pergunta mais específica sobre como fazer uma planilha, exemplos de custos, ou outras dicas de controle financeiro, pode mandar a bronca que o {NOME_CHATBOT} se vira nos trinta pra te ajudar!
"""
    return resposta_base

#Alerta Vermelho AntiGolpe

def modulo_alerta_antigolpe(mensagem_usuario_original):
    print(f"[{NOME_CHATBOT}] Entrou no módulo Alerta Vermelho AntiGolpe.")
    mensagem_lower = mensagem_usuario_original.lower().strip()

    # CONTEÚDO BASE DO MÓDULO
    resposta_base = f"""
Opa, meu patrão/minha patroa! Fique esperto que nem suricato no deserto, porque no mundo digital tem muito malandro querendo passar a perna na gente boa! Mas relaxa, que o {NOME_CHATBOT} vai te dar o bizu pra você não cair em cilada e manter seu suado dinheirinho seguro. Bora aprender a farejar golpe de longe? 🕵️‍♂️🚫

**Principais Golpes que Rondam o Empreendedor:**
* **Boleto Adulterado:** Sempre confira o nome do beneficiário, o CNPJ, o valor e o banco antes de pagar. Se o código de barras estiver esquisito ou falhado, desconfie!
* **Mensagem Falsa (Phishing):** SMS, e-mail ou zap com link suspeito pedindo seus dados, senha, ou dizendo que você ganhou um prêmio incrível? CORRA QUE É CILADA, BINO! Banco e empresa séria não pedem senha assim.
* **Zap Clonado ou Perfil Falso:** "Amigo" ou "parente" pedindo dinheiro com urgência? Ligue pra pessoa (chamada de voz, não zap!) pra confirmar antes de fazer qualquer Pix.
* **Crédito Fácil que Pede Depósito Adiantado:** Promessa de empréstimo rápido sem consulta, mas tem que pagar uma "taxinha" antes? Golpe na certa! Instituição séria não cobra pra liberar empréstimo.
* **Golpe do PIX Agendado ou Comprovante Falso:** Vendeu algo? Só entregue o produto depois que o dinheiro CAIR MESMO na sua conta. Comprovante pode ser forjado!

**Dicas de Ouro do {NOME_CHATBOT} pra se Proteger:**
1.  **Desconfie Sempre:** Se a oferta é boa demais pra ser verdade, provavelmente é mentira.
2.  **Não Clique em Tudo:** Link estranho no e-mail, SMS ou zap? Melhor não clicar. Vá direto no site oficial da empresa ou do banco.
3.  **Senha é Segredo:** Sua senha é que nem escova de dente, não se empresta pra ninguém! Use senhas fortes e diferentes para cada serviço.
4.  **Autenticação de Dois Fatores (2FA):** Ative isso em tudo que der (banco, redes sociais, e-mail). É uma camada extra de segurança arretada!
5.  **Na Dúvida, NÃO FAÇA!** Se sentir que tem algo esquisito, pare, respire e peça ajuda ou verifique com a empresa/banco por um canal que VOCÊ conhece e confia.

Quer que o {NOME_CHATBOT} te conte um 'causo' de golpe pra você ver como os malandros agem, ou tem alguma dúvida específica sobre algum tipo de trambique? Manda aí que a gente tenta te deixar mais safo!
"""

    # Lógica para interações mais específicas com Gemini
    # Exemplo: se o usuário pedir um "causo" ou perguntar sobre um golpe específico.
    # Esta parte será um pouco mais elaborada.
    
    # Cenário simples: se o usuário pedir um exemplo de golpe.
    gatilhos_cenario_golpe = ["me conte um causo", "exemplo de golpe", "simulação de golpe", "como agem os golpistas"]
    if any(gatilho in mensagem_lower for gatilho in gatilhos_cenario_golpe):
        print(f"[{NOME_CHATBOT}] 'Alerta AntiGolpe': Usuário pediu um cenário de golpe. Usando Gemini.")
        if not GOOGLE_API_KEY or not MODELO_GEMINI:
            return f"Oxe, meu sistema avançado que cria os 'causos' de golpe tá tirando uma soneca. Mas a dica principal é: sempre desconfie e verifique tudo direitinho antes de clicar ou pagar!"

        prompt_gemini_cenario = f"""
Você é o {NOME_CHATBOT}, um consultor financeiro gente boa de Alagoas.
Um microempreendedor pediu um exemplo de um golpe comum para ficar mais esperto.
Descreva um cenário curto e simples de um golpe digital comum que afeta pequenos comerciantes (ex: golpe do boleto falso, phishing por whatsapp, falso empréstimo).
Use sua persona alagoana, linguagem popular, e explique rapidamente qual o 'pulo do gato' do golpista e qual o 'alerta vermelho' para o empreendedor.
Mantenha o cenário curto, em 3 a 5 frases.
"""
        try:
            print(f"[{NOME_CHATBOT}] 'Alerta AntiGolpe': Enviando pedido de cenário para o Gemini...")
            generation_config = genai.types.GenerationConfig(temperature=0.8) # Um pouco mais de criatividade para cenários
            response = MODELO_GEMINI.generate_content(prompt_gemini_cenario, generation_config=generation_config)
            
            text_result = None
            # (Reutilizar a mesma lógica de extração de texto da resposta do Gemini das outras funções)
            if hasattr(response, 'text') and response.text and isinstance(response.text, str): text_result = response.text
            elif hasattr(response, 'parts') and response.parts: text_result = "".join(part.text for part in response.parts if hasattr(part, 'text') and isinstance(part.text, str))
            elif hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts: text_result = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and isinstance(part.text, str))
            
            if text_result and text_result.strip():
                cenario_golpe = text_result.strip()
                print(f"[{NOME_CHATBOT}] 'Alerta AntiGolpe': Cenário de golpe gerado pelo Gemini: {cenario_golpe}")
                return f"{resposta_base}\n\n**O {NOME_CHATBOT} te conta um causo pra ficar ligado:**\n{cenario_golpe}\n\nLembre-se: informação e desconfiança são suas melhores armas!"
            else: # Tratamento de bloqueio ou resposta vazia
                block_reason_msg = ""
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                    block_reason_msg = f"Motivo do bloqueio: {response.prompt_feedback.block_reason}."
                print(f"[{NOME_CHATBOT}] 'Alerta AntiGolpe': Resposta do Gemini para cenário veio vazia ou em formato não reconhecido. {block_reason_msg}")
                return f"{resposta_base}\n\nOxe! Ia te contar um causo, mas meu repertório deu um branco aqui. Mas fica a dica: todo cuidado é pouco!"
        except Exception as e:
            print(f"[{NOME_CHATBOT}] 'Alerta AntiGolpe': Erro ao chamar Gemini para gerar cenário: {e}\n{traceback.format_exc()}")
            return f"{resposta_base}\n\nRapaz, minha memória pra causo de golpe falhou agora. Mas a regra é clara: desconfie sempre!"
    
    # Se não for um pedido de cenário, retorna a informação base.
    return resposta_base

def listar_termos_conhecidos():
    if not glossario_local_do_ze:
        return f"Oxe, ainda tô aprendendo os termos, {NOME_CHATBOT} aqui tá começando! Volte mais tarde."
    mensagem = f"Opa! O {NOME_CHATBOT} aqui já tem na ponta da língua um bocado de coisa, visse? Se liga nos termos que eu posso te explicar do meu caderninho:\n"
    for termo in glossario_local_do_ze.keys():
        mensagem += f"- {termo.capitalize()}\n"
    mensagem += f"\nE pode perguntar sobre 'Pix ou Maquininha' e dicas de 'Caixa Forte' também! Se jogar um termo diferente, eu dou meus pulos com meu sistema avançado pra tentar te ajudar!"
    return mensagem

def pesquisar_termo_glossario(mensagem_usuario):
    mensagem_normalizada = mensagem_usuario.lower().strip()
    print(f"[{NOME_CHATBOT}] Pesquisando termo para (glossário): '{mensagem_normalizada}'")
    
    termo_encontrado_localmente = None
    termo_candidato_local = ""

    for termo_chave in glossario_local_do_ze.keys():
        if f" {termo_chave} " in f" {mensagem_normalizada} " or mensagem_normalizada == termo_chave:
            termo_encontrado_localmente = glossario_local_do_ze[termo_chave]
            termo_candidato_local = termo_chave
            break 
    
    if termo_encontrado_localmente:
        print(f"[{NOME_CHATBOT}] Termo '{termo_candidato_local}' encontrado no glossário local.")
        return termo_encontrado_localmente
    
    palavras_lista = ["lista de termos", "quais termos", "termos que você conhece", "listar termos"]
    if any(gatilho in mensagem_normalizada for gatilho in palavras_lista):
        print(f"[{NOME_CHATBOT}] Usuário pediu a lista de termos.")
        return listar_termos_conhecidos()

    termo_para_gemini = ""
    palavras_chave_extracao = [
        "o que é", "o que significa", "explique sobre", "explique", "definição de", 
        "significado de", "fale sobre", "me fala sobre", "saber sobre", "sobre"
    ]

    for palavra_chave in palavras_chave_extracao:
        if mensagem_normalizada.startswith(palavra_chave + " "):
            termo_extraido = mensagem_normalizada.split(palavra_chave + " ", 1)[1].strip()
            for pontuacao in ["?", ".", "!"]:
                if termo_extraido.endswith(pontuacao): termo_extraido = termo_extraido[:-1].strip()
            if termo_extraido:
                termo_para_gemini = termo_extraido
                print(f"[{NOME_CHATBOT}] Termo extraído para Gemini (após palavra-chave '{palavra_chave}'): '{termo_para_gemini}'")
                break 
    
    if not termo_para_gemini and len(mensagem_normalizada.split()) <= 3:
        palavras_curtas_ignoraveis = ["oi", "ok", "sim", "não", "valeu", "obrigado", "blz", "tchau", "teste", "pix", "qr code", "maquininha", "caixa"] # Evita re-processar gatilhos de outros módulos
        if mensagem_normalizada not in palavras_curtas_ignoraveis and not any(saud in mensagem_normalizada for saud in ["bom dia", "boa tarde", "boa noite"]):
             termo_para_gemini = mensagem_normalizada
             print(f"[{NOME_CHATBOT}] Mensagem curta '{termo_para_gemini}' assumida como termo para Gemini (glossário).")

    if termo_para_gemini:
        if len(termo_para_gemini.split()) > 7: # Limite arbitrário para um "termo"
            print(f"[{NOME_CHATBOT}] Termo extraído '{termo_para_gemini}' (glossário) é muito longo. Respondendo com mensagem padrão.")
            return f"Oxe, {NOME_CHATBOT} acha que '{termo_para_gemini}' é mais uma frase do que um termo pra explicar. Tenta algo mais direto!"
        
        print(f"[{NOME_CHATBOT}] Termo '{termo_para_gemini}' não encontrado localmente (glossário). Tentando com Gemini...")
        return explicar_termo_com_gemini(termo_para_gemini)
    else:
        print(f"[{NOME_CHATBOT}] Não foi possível extrair um termo para o glossário da mensagem: '{mensagem_usuario}'. Respondendo com mensagem padrão.")
        return f"Oxe, {NOME_CHATBOT} não entendeu bem o que você quis dizer com '{mensagem_usuario}'. Tente perguntar 'o que é [termo]?', sobre 'Pix ou Maquininha', dicas de 'Caixa Forte', ou peça a 'lista de termos'."

# --- Lógica Principal do Chatbot (Roteamento) ---

def processar_mensagem_usuario(mensagem_usuario):
    mensagem_lower = mensagem_usuario.lower().strip()
    print(f"[{NOME_CHATBOT}] MENSAGEM RECEBIDA (roteador principal): '{mensagem_usuario}' (normalizada: '{mensagem_lower}')")

    if not mensagem_lower:
        return f"Manda a prosa, meu patrão/minha patroa! {NOME_CHATBOT} tá aqui todo ouvidos!"

    # 1. Verificar Saudações
    saudacoes = ["oi", "olá", "e aí", "iai", "opa", "salve", "bom dia", "boa tarde", "boa noite"]
    if mensagem_lower in saudacoes or any(mensagem_lower.startswith(s) and len(mensagem_lower.split()) <=3 for s in saudacoes) :
        print(f"[{NOME_CHATBOT}] Roteador: Mensagem reconhecida como saudação.")
        return saudacao_inicial()

    # 2. Verificar Módulo "Pix ou Maquininha"
    gatilhos_pix_maquininha = [
        "pix ou maquininha", "pix e maquininha", "maquininha ou pix", "maquininha e pix",
        "qual o melhor pix ou cartão", "pix ou cartão", "taxa pix", "taxa maquininha",
        "sobre pix", "sobre maquininha", "fale sobre pix", "fale sobre maquininha",
        "qr code", "maquininha de cartao", "maquininha de cartão", "pix vs maquininha",
        "vantagens do pix", "desvantagens da maquininha", "custo maquininha"
    ]
    if any(gatilho in mensagem_lower for gatilho in gatilhos_pix_maquininha):
        print(f"[{NOME_CHATBOT}] Roteador: Mensagem acionou o módulo Pix ou Maquininha.")
        return modulo_pix_maquininha(mensagem_usuario)

    # 3. Verificar Módulo "Caixa Forte, Negócio Forte"
    gatilhos_caixa_forte = [
        "caixa forte", "controle financeiro", "fluxo de caixa", "organizar finanças",
        "separar contas", "despesas da empresa", "custos do negócio", "planilha financeira",
        "gestão financeira", "saúde financeira", "dicas de caixa"
    ]
    if any(gatilho in mensagem_lower for gatilho in gatilhos_caixa_forte):
        print(f"[{NOME_CHATBOT}] Roteador: Mensagem acionou o módulo Caixa Forte.")
        return modulo_caixa_forte(mensagem_usuario)

    # 4. Verificar Módulo "Alerta Vermelho AntiGolpe" (NOVO)
    gatilhos_antigolpe = [
        "alerta golpe", "anti golpe", "golpe pix", "golpe boleto", "evitar golpe", 
        "segurança online", "phishing", "golpe do zap", "golpe whatsapp", "me proteger de golpe",
        "dica de segurança", "é golpe", "como saber se é golpe", "me conte um causo", "exemplo de golpe" # Adicionando gatilhos para cenário
    ]
    if any(gatilho in mensagem_lower for gatilho in gatilhos_antigolpe):
        print(f"[{NOME_CHATBOT}] Roteador: Mensagem acionou o módulo Alerta AntiGolpe.")
        return modulo_alerta_antigolpe(mensagem_usuario)

    # 5. Se não for nenhum dos anteriores, tenta o Glossário (que pode usar Gemini)
    print(f"[{NOME_CHATBOT}] Roteador: Mensagem não é saudação nem módulo específico, encaminhando para pesquisa de termo/glossário...")
    return pesquisar_termo_glossario(mensagem_usuario)

@app.route('/') # Rota para a página principal do chat
def home():
    print(f"[{NOME_CHATBOT}] Servindo a página principal do chat (index.html).")
    return render_template('index.html') # Renderiza e retorna o arquivo index.html da pasta 'templates'

# --- Endpoint para receber mensagens (simulando o WhatsApp) ---
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    resposta_bot = f"Oxe! Alguma coisa deu muito errado aqui no {NOME_CHATBOT} e ele não soube o que dizer."
    mensagem_recebida_para_log = ""
    
    try:
        if request.method == 'POST':
            dados_recebidos = request.json
            mensagem_usuario = dados_recebidos.get('mensagem', '').strip()
            mensagem_recebida_para_log = mensagem_usuario
            print(f"[{NOME_CHATBOT}] Requisição POST recebida. Mensagem: '{mensagem_usuario}'")
            
            if not mensagem_usuario:
                resposta_bot = f'Manda a mensagem aí! {NOME_CHATBOT} tá no aguardo.'
            else:
                resposta_bot = processar_mensagem_usuario(mensagem_usuario)
        
        elif request.method == 'GET':
            mensagem_teste = request.args.get('mensagem', '').strip()
            mensagem_recebida_para_log = mensagem_teste
            print(f"[{NOME_CHATBOT}] Requisição GET recebida. Mensagem: '{mensagem_teste}'")

            if not mensagem_teste:
                print(f"[{NOME_CHATBOT}] Mensagem GET vazia, respondendo com saudação.")
                resposta_bot = saudacao_inicial()
            else:
                resposta_bot = processar_mensagem_usuario(mensagem_teste)
        
        print(f"[{NOME_CHATBOT}] Resposta para '{mensagem_recebida_para_log}': '{resposta_bot[:100]}...'")
        return jsonify({'resposta_bot': resposta_bot})

    except Exception as e:
        print(f"[{NOME_CHATBOT}] ERRO GRAVE no endpoint para mensagem '{mensagem_recebida_para_log}': {e}\n{traceback.format_exc()}")
        resposta_bot = f"Eita gota! {NOME_CHATBOT} teve um piripaque feio processando sua mensagem. Tente de novo ou avise o técnico!"
        return jsonify({'resposta_bot': resposta_bot})

# --- Para rodar o aplicativo Flask localmente ---
if __name__ == '__main__':
    print(f"[{NOME_CHATBOT}] Iniciando o servidor Flask...")
    if not GOOGLE_API_KEY or not MODELO_GEMINI:
        print(f"[{NOME_CHATBOT}] ALERTA: {NOME_CHATBOT} vai operar em MODO LIMITADO pois a API do Gemini não está completamente configurada.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)