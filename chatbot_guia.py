# chatbot_guia.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import traceback
from flask import Flask, request, jsonify, render_template, session

# --- Carregar variáveis de ambiente do arquivo .env ---
load_dotenv()

# --- Configuração Inicial do Flask ---
app = Flask(__name__)
app.secret_key = 'minha_chave_secreta_super_forte_e_aleatoria_123!@#_corrigida' 

# --- Persona e Conteúdo do Chatbot ---
NOME_CHATBOT = "Zé do Financeiro"

# --- Configuração da API Key do Gemini ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODELO_GEMINI = None 

if not GOOGLE_API_KEY:
    print(f"[{NOME_CHATBOT}] ALERTA: Chave da API do Google (GOOGLE_API_KEY) não encontrada...")
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print(f"[{NOME_CHATBOT}] API Key do Gemini configurada com sucesso!")
        MODELO_GEMINI = genai.GenerativeModel('gemini-1.5-flash')
        print(f"[{NOME_CHATBOT}] Modelo Gemini '{MODELO_GEMINI.model_name}' carregado!")
    except Exception as e:
        print(f"[{NOME_CHATBOT}] Oxe! Deu um erro ao configurar o Gemini ou carregar o modelo: {e}")
        GOOGLE_API_KEY = None 
        MODELO_GEMINI = None

VALID_INTENTS = [
    "SAUDACAO", "GLOSSARIO_TERMO", "PIX_MAQUININHA", "CAIXA_FORTE", 
    "ALERTA_ANTIGOLPE", "LISTAR_FUNCIONALIDADES", "DESPEDIDA", 
    "PLANEJADOR_SONHOS", "NENHUMA_ESPECIFICA"
]

# --- Função Auxiliar para Tratamento do Usuário ---
def obter_tratamento_usuario():
    nome_usuario = session.get('user_name')
    if nome_usuario:
        return nome_usuario.strip().capitalize()
    return "meu patrão/minha patroa"

def obter_intencao_com_gemini(mensagem_usuario):
    if not GOOGLE_API_KEY or not MODELO_GEMINI:
        print(f"[{NOME_CHATBOT}] Gemini não configurado. Não é possível obter intenção.")
        return "NENHUMA_ESPECIFICA" 
    tratamento_atual = obter_tratamento_usuario()
    prompt_classificacao = f"""
Você é um assistente inteligente que analisa a mensagem de um usuário para um chatbot chamado "{NOME_CHATBOT}" e identifica qual a principal intenção do usuário. O {NOME_CHATBOT} é um guia de bolso para microempreendedores de Alagoas, com uma linguagem amigável e regional. O usuário pode ser chamado de '{tratamento_atual}'.
As possíveis intenções que o {NOME_CHATBOT} pode atender são:
1. SAUDACAO: Se o usuário está apenas cumprimentando (ex: "oi", "bom dia Zé", "e aí {tratamento_atual}").
2. GLOSSARIO_TERMO: Se o usuário quer saber o significado de um termo financeiro específico (ex: "o que é MEI?", "me explique capital de giro para {tratamento_atual}", "bitcoin").
3. PIX_MAQUININHA: Se a pergunta é sobre Pix, maquininhas de cartão, taxas, QR code, comparação entre eles.
4. CAIXA_FORTE: Se a pergunta é sobre controle financeiro, fluxo de caixa, organizar finanças da empresa, separar contas.
5. ALERTA_ANTIGOLPE: Se a pergunta é sobre golpes financeiros, segurança online, phishing, como se proteger.
6. LISTAR_FUNCIONALIDADES: Se o usuário pergunta o que o Zé pode fazer, sobre o que ele fala, ou pede ajuda geral.
7. DESPEDIDA: Se o usuário está se despedindo (ex: "tchau {tratamento_atual}", "até mais").
8. PLANEJADOR_SONHOS: Se o usuário quer ajuda para planejar uma meta financeira, um sonho para o negócio, ou um objetivo de investimento (ex: "quero comprar uma máquina nova", "me ajuda a planejar um objetivo", "simulador de planejamento", "planejamento financeiro para meta", "quero realizar um sonho no meu negócio").
Mensagem do Usuário: "{mensagem_usuario}"
Analise a mensagem do usuário e retorne APENAS UMA das seguintes palavras-chave:
SAUDACAO, GLOSSARIO_TERMO, PIX_MAQUININHA, CAIXA_FORTE, ALERTA_ANTIGOLPE, LISTAR_FUNCIONALIDADES, DESPEDIDA, PLANEJADOR_SONHOS, ou NENHUMA_ESPECIFICA.
Se a intenção parecer GLOSSARIO_TERMO, mas o termo específico não estiver claro (ex: "o que é?", "me explique"), retorne NENHUMA_ESPECIFICA.
"""
    try:
        # ... (resto da função obter_intencao_com_gemini como na versão anterior)
        print(f"[{NOME_CHATBOT}] Enviando mensagem para Gemini para classificação de intenção: '{mensagem_usuario}'")
        generation_config_intent = genai.types.GenerationConfig(temperature=0.2) 
        response = MODELO_GEMINI.generate_content(prompt_classificacao, generation_config=generation_config_intent)
        intent_keyword_bruta = None
        if hasattr(response, 'text') and response.text and isinstance(response.text, str): intent_keyword_bruta = response.text
        elif hasattr(response, 'parts') and response.parts: intent_keyword_bruta = "".join(part.text for part in response.parts if hasattr(part, 'text') and isinstance(part.text, str))
        elif hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts: intent_keyword_bruta = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and isinstance(part.text, str))

        if intent_keyword_bruta:
            intent_keyword_limpa = intent_keyword_bruta.strip().upper().replace(".","")
            if intent_keyword_limpa in VALID_INTENTS:
                print(f"[{NOME_CHATBOT}] Intenção identificada pelo Gemini: {intent_keyword_limpa}")
                return intent_keyword_limpa
            else:
                print(f"[{NOME_CHATBOT}] Gemini retornou uma intenção inválida: '{intent_keyword_limpa}'. Resposta bruta: '{intent_keyword_bruta}'")
                return "NENHUMA_ESPECIFICA"
        else:
            block_reason_msg = ""
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason: block_reason_msg = f"Motivo do bloqueio: {response.prompt_feedback.block_reason}."
            print(f"[{NOME_CHATBOT}] Resposta do Gemini para classificação de intenção veio vazia. {block_reason_msg}")
            return "NENHUMA_ESPECIFICA"
    except Exception as e:
        print(f"[{NOME_CHATBOT}] Erro ao chamar Gemini para classificação de intenção: {e}\n{traceback.format_exc()}")
        return "NENHUMA_ESPECIFICA"

def saudacao_inicial():
    tratamento = obter_tratamento_usuario()
    if session.get('user_name'):
        return f"De volta por aqui, {tratamento}! Sou o {NOME_CHATBOT}. Em que posso te ajudar hoje? Além de bater um papo sobre finanças, posso te ajudar com o Planejador de Sonhos!"
    else:
        return f"Chegue mais, {tratamento}! Sou o {NOME_CHATBOT}. Para nosso papo ficar mais arretado, como posso te chamar? (Ou pode me perguntar algo direto, como sobre o 'Planejador de Sonhos'!)"

glossario_local_do_ze_TEMPLATE = {
    "mei": "MEI, {tratamento}, é a sigla para Microempreendedor Individual. É um jeito simplificado para você que trabalha por conta própria formalizar seu negócio, ter um CNPJ, emitir notas fiscais e ter acesso a benefícios como aposentadoria e auxílio-doença. É uma mão na roda pra começar com o pé direito, visse?",
    "cnpj": "CNPJ, {tratamento}, significa Cadastro Nacional da Pessoa Jurídica. É tipo o CPF da sua empresa, um número único que identifica seu negócio perante o governo e outras instituições. Com o CNPJ, sua empresa existe oficialmente!",
    "conta pj": "Conta PJ, {tratamento}, é uma conta bancária específica para Pessoa Jurídica, ou seja, para sua empresa. É fundamental separar o dinheiro da empresa do seu dinheiro pessoal. Com uma conta PJ, fica tudo mais organizado e profissional.",
    "pix": "O Pix (definição geral), {tratamento}, é um sistema de pagamento instantâneo criado pelo Banco Central do Brasil. Com ele, você envia e recebe dinheiro em poucos segundos, a qualquer hora do dia, todos os dias da semana, usando chaves (como CPF/CNPJ, celular, e-mail) ou QR Code. É ligeiro e muitas vezes de graça ou com taxas baixinhas!",
    "qr code": "QR Code (definição geral), {tratamento}, é um tipo de código de barras bidimensional, aquele quadradinho cheio de outros quadradinhos. Ele pode ser lido pela câmera do celular e serve para um monte de coisa: fazer pagamentos com Pix, acessar cardápios, abrir sites, compartilhar informações... Uma praticidade arretada!",
    "fluxo de caixa": "Fluxo de caixa (o termo geral), {tratamento}, é o controle de toda a grana que entra e sai do seu negócio durante um período. É como um extrato detalhado, mostrando de onde veio e para onde foi cada centavo. Essencial pra saber se a empresa tá no azul ou no vermelho!",
    "capital de giro": "Capital de giro, {tratamento}, é aquela grana que sua empresa precisa ter disponível para cobrir as despesas do dia a dia enquanto o dinheiro das vendas não entra. É o que mantém o negócio funcionando: pagar fornecedores, salários, contas de água, luz, aluguel, comprar matéria-prima. Sem ele, a empresa pode passar um baita aperreio!",
    "microcrédito": "Microcrédito, {tratamento}, é um tipo de empréstimo com valor mais baixo, pensado especialmente para ajudar pequenos empreendedores, como você, a investir no negócio, seja para comprar equipamentos, matéria-prima ou melhorar o ponto. Geralmente tem condições mais acessíveis, mas é bom pesquisar direitinho!"
}

def explicar_termo_com_gemini(termo_usuario):
    tratamento = obter_tratamento_usuario()
    if not GOOGLE_API_KEY or not MODELO_GEMINI:
        return f"Oxe, {tratamento}, meu sistema de consulta avançada (Gemini) não tá configurado ou deu chabu na inicialização."
    prompt = f"""
Você é o {NOME_CHATBOT}, um assistente financeiro digital super gente boa de Alagoas. Fale com o usuário de forma personalizada, chamando-o(a) por '{tratamento}'.
Sua missão é explicar termos financeiros de forma SIMPLES, CURTA, AMIGÁVEL e DIRETA para microempreendedores.
Use uma linguagem popular e expressões regionais de Alagoas.
Explique o seguinte termo para {tratamento}: '{termo_usuario}'
Mantenha a explicação em no máximo 3 ou 4 frases curtas.
Seja positivo e encorajador.
Se não souber ou o termo não for financeiro, diga que vai estudar mais um cadinho, no seu estilo.
"""
    try:
        print(f"[{NOME_CHATBOT}] Enviando o termo '{termo_usuario}' para o Gemini (para {tratamento})...")
        generation_config = genai.types.GenerationConfig(temperature=0.7)
        response = MODELO_GEMINI.generate_content(prompt, generation_config=generation_config)
        text_result = None
        if hasattr(response, 'text') and response.text and isinstance(response.text, str): text_result = response.text
        elif hasattr(response, 'parts') and response.parts: text_result = "".join(part.text for part in response.parts if hasattr(part, 'text') and isinstance(part.text, str))
        elif hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts: text_result = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and isinstance(part.text, str))
        
        if text_result and text_result.strip():
            final_explanation = text_result.strip()
            print(f"[{NOME_CHATBOT}] Explicação do Gemini para '{termo_usuario}': {final_explanation}")
            return final_explanation
        else:
            block_reason_msg = ""
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason: block_reason_msg = f"Motivo do bloqueio: {response.prompt_feedback.block_reason}."
            print(f"[{NOME_CHATBOT}] Resposta do Gemini para '{termo_usuario}' veio vazia. {block_reason_msg}")
            return f"Eita gota, {tratamento}! O {NOME_CHATBOT} tentou desenrolar sobre '{termo_usuario}' mas a resposta veio esquisita. {block_reason_msg}"
    except Exception as e:
        print(f"[{NOME_CHATBOT}] Erro ao falar com Gemini sobre '{termo_usuario}': {e}\n{traceback.format_exc()}")
        return f"Rapaz, deu piripaque na conexão pra explicar '{termo_usuario}', {tratamento}."

def modulo_pix_maquininha(mensagem_usuario_original):
    tratamento = obter_tratamento_usuario()
    print(f"[{NOME_CHATBOT}] Entrou no módulo Pix ou Maquininha para {tratamento}.")
    resposta_base = f"""
Opa, {tratamento}! Chegou na dúvida cruel: Pix ou Maquininha? Relaxe que o {NOME_CHATBOT} te dá o papo reto pra você não entrar em nenhuma roubada! 💸

**PIX: O Ligeirinho Querido** 🚀
O Pix é aquele parceiro que chegou pra facilitar a vida, visse?
* **Grana na Hora:** Vendeu, {tratamento}, recebeu! O dinheiro cai na sua conta rapidinho, sem choro nem vela.
* **Custo Baixo (ou Zero!):** Pra gente que é MEI ou pequeno negócio, muitas vezes não tem taxa nenhuma pra receber via Pix. É economia na certa!
* **Facinho de Usar:** Com Chave Pix (CPF/CNPJ, celular, e-mail) ou QR Code, seu cliente te paga num instante. Você pode ter um QR Code impresso no balcão (estático) ou gerar um na hora pra cada venda (dinâmico).

**MAQUININHA: A Boa e Velha Companheira** 💳
A maquininha ainda tem seu valor, e não é pouco, {tratamento}!
* **Mais Opções pro Cliente:** Aceita cartão de débito, crédito e até parcelado. Tem cliente que não abre mão dessa comodidade.
* **Vendas Parceladas:** Quer vender aquele produto mais caro? Com a maquininha, o cliente pode parcelar e você pode até receber tudo de uma vez (pagando uma taxinha de antecipação, claro).
* **Controle:** Muitas maquininhas já vêm com app pra ajudar no controle das vendas.

**E AS TAXAS DA MAQUININHA, {NOME_CHATBOT}?** 😥
Aí é que mora o perigo se a gente não ficar de olho, {tratamento}! A maquininha tem:
* **Custo da Máquina:** Algumas você compra, outras aluga.
* **Taxa por Venda (MDR):** Um percentual sobre cada venda no débito, crédito à vista e crédito parcelado. Essa taxa varia MUITO de uma maquininha pra outra!
* **Prazo pra Receber:** O dinheiro do crédito pode demorar uns dias (ou até um mês) pra cair. Se quiser antes, paga mais taxa de antecipação.

**{NOME_CHATBOT} AJUDA A DECIDIR: E AGORA, {tratamento.split()[0]}?** 🤔 (Usando só o primeiro nome se tiver mais de um)
1.  **Quem é sua Clientela?** Seus clientes são da turma do Pix ou preferem um cartãozinho? Pergunte pra eles!
2.  **Seu Volume de Vendas:** Se vende muito e com valor mais alto, as taxas da maquininha podem pesar.
3.  **Bote na Ponta do Lápis:** Pesquise as taxas de umas 3 maquininhas diferentes e compare com o custo do Pix (que pode ser zero!).
4.  **Use os Dois, {tratamento}!** Muitas vezes, o melhor dos mundos é ter o Pix como opção principal (mais barata) e uma maquininha pra não perder venda de quem só quer usar cartão.

Ficou mais claro, {tratamento}? Se tiver alguma dúvida mais específica sobre taxas de alguma maquininha, como gerar QR Code no seu banco, ou outra coisa desse assunto, pode mandar a pergunta que o {NOME_CHATBOT} tenta desenrolar com o sistema avançado (Gemini)!
"""
    return resposta_base

def modulo_caixa_forte(mensagem_usuario_original):
    tratamento = obter_tratamento_usuario()
    print(f"[{NOME_CHATBOT}] Entrou no módulo Caixa Forte para {tratamento}. Mensagem: '{mensagem_usuario_original}'")
    mensagem_lower = mensagem_usuario_original.lower().strip()
    gatilhos_base = ["caixa forte", "controle financeiro", "organizar finanças", "gestão financeira", "saúde financeira", "dicas de caixa"]
    eh_pedido_base = any(gatilho == mensagem_lower for gatilho in gatilhos_base)
    
    if not eh_pedido_base and any(gatilho in mensagem_lower for gatilho in gatilhos_base) and len(mensagem_lower.split()) > 3:
        print(f"[{NOME_CHATBOT}] 'Caixa Forte': Pergunta específica para {tratamento}: '{mensagem_usuario_original}'. Usando Gemini.")
        if not GOOGLE_API_KEY or not MODELO_GEMINI: return f"Oxe, {tratamento}, meu sistema avançado tá cochilando agora..."
        prompt_gemini = f"Você é o {NOME_CHATBOT}, consultor financeiro de Alagoas. O usuário '{tratamento}' fez uma pergunta específica sobre controle financeiro: '{mensagem_usuario_original}'. Responda de forma simples, prática, curta (4-5 frases), com sotaque e expressões regionais, positivo e direto."
        try:
            response = MODELO_GEMINI.generate_content(prompt_gemini)
            text_result = None
            if hasattr(response, 'text') and response.text: text_result = response.text
            if text_result and text_result.strip(): return text_result.strip()
            return f"Eita, {tratamento}! Tentei buscar uma luz sobre '{mensagem_usuario_original}', mas o sistema avançado hoje tá meio nublado."
        except Exception as e: return f"Rapaz, deu um piripaque aqui tentando responder sobre '{mensagem_usuario_original}', {tratamento}."

    print(f"[{NOME_CHATBOT}] 'Caixa Forte': Respondendo com informações base para {tratamento}.")
    resposta_base = f"""
E aí, {tratamento}! Quer deixar o caixa da sua empresa forte como um touro e o negócio rendendo que é uma beleza? Então você tá falando com o {NOME_CHATBOT} certo! Bora organizar as finanças pra não ter mais aperreio e o dimdim sobrar no fim do mês! 💰💪

**1. {NOME_CHATBOT} Pergunta: Cadê o Dinheiro da Empresa e Cadê o Seu?**
Primeira lição, e a mais importante de todas, visse {tratamento}? **SEPARE as contas!** O dinheiro que entra das suas vendas é da EMPRESA. O seu salário (o famoso pró-labore) você tira da empresa e bota na sua conta PESSOAL. Misturar tudo é receita pra dor de cabeça e pra não saber se o negócio tá dando lucro de verdade! Uma conta PJ ajuda demais nisso. Se precisar de dica sobre Conta PJ, é só falar!

**2. Anota Tudo, {tratamento}, Freguesia por Freguesia, Despesa por Despesa!**
Pode parecer chato, mas tem que anotar TUDO que entra e TUDO que sai. Desde o cafezinho pago com dinheiro do caixa até aquela venda grande. Isso é o famoso **Fluxo de Caixa**. Sem isso, você fica no escuro!
* **Entradas (Receitas):** Dinheiro das vendas, serviços prestados, e qualquer outra graninha que pingar na conta da empresa.
* **Saídas (Despesas/Custos):** Aluguel, água, luz, internet, telefone, fornecedor, material, imposto, seu pró-labore, e até aquela balinha que você comprou pro troco. Tem as **despesas fixas** (aquelas que vêm todo mês, faça chuva ou faça sol, tipo o aluguel) e as **variáveis** (que mudam conforme você vende mais ou menos, tipo a matéria-prima pro seu produto).

**3. Ferramentas pra te Ajudar nessa Missão, {tratamento}:**
Não precisa ser nenhum expert em computador, não!
* **App do seu Banco:** Muitos bancos já mostram o extrato direitinho e alguns até ajudam a categorizar os gastos. Fuce lá nas opções do seu app!
* **Planilha Financeira:** Uma planilha simples no Excel ou Google Sheets faz milagres! Colunas básicas: Data, Descrição (o que foi a entrada/saída), Entrada (R$), Saída (R$), Saldo (R$). O {NOME_CHATBOT} pode te dar umas dicas de como montar uma depois, se quiser!
* **Aplicativos de Controle Financeiro:** Existem vários apps (alguns até de graça, {tratamento}!) feitos pra ajudar o microempreendedor a organizar as contas. Vale a pena dar uma pesquisada em alguns como 'Organizze', 'Mobills' ou outros focados em MEI.

**4. Pra que Serve esse Tal de Caixa Forte, {NOME_CHATBOT} me Explica?**
Com as contas organizadas, {tratamento}, você consegue:
* Saber pra onde o dinheiro tá indo e se tem algum ralo vazando grana que você nem percebia.
* Ver se o preço do seu produto ou serviço tá cobrindo os custos e dando lucro de verdade.
* Planejar melhor seus investimentos, suas compras de material e não entrar em dívida à toa.
* Ter base pra negociar com fornecedor, pedir um empréstimo consciente se precisar.
* E o principal, {tratamento}: dormir mais tranquilo sabendo como tá a saúde financeira do seu negócio!

E aí, {tratamento}, deu pra clarear as ideias? Se tiver alguma pergunta mais específica sobre como fazer uma planilha, exemplos de custos, ou outras dicas de controle financeiro, pode mandar a bronca que o {NOME_CHATBOT} se vira nos trinta pra te ajudar!
"""
    return resposta_base

def modulo_alerta_antigolpe(mensagem_usuario_original):
    tratamento = obter_tratamento_usuario()
    print(f"[{NOME_CHATBOT}] Entrou no módulo Alerta AntiGolpe para {tratamento}.")
    mensagem_lower = mensagem_usuario_original.lower().strip()
    resposta_base = f"""
Opa, {tratamento}! Fique esperto que nem suricato no deserto, porque no mundo digital tem muito malandro querendo passar a perna na gente boa! Mas relaxa, que o {NOME_CHATBOT} vai te dar o bizu pra você não cair em cilada e manter seu suado dinheirinho seguro. Bora aprender a farejar golpe de longe? 🕵️‍♂️🚫

**Principais Golpes que Rondam o Empreendedor:**
* **Boleto Adulterado:** Sempre confira o nome do beneficiário, o CNPJ, o valor e o banco antes de pagar, {tratamento}. Se o código de barras estiver esquisito ou falhado, desconfie!
* **Mensagem Falsa (Phishing):** SMS, e-mail ou zap com link suspeito pedindo seus dados, senha, ou dizendo que você ganhou um prêmio incrível? CORRA QUE É CILADA, {tratamento.split()[0]}! Banco e empresa séria não pedem senha assim.
* **Zap Clonado ou Perfil Falso:** "Amigo" ou "parente" pedindo dinheiro com urgência? Ligue pra pessoa (chamada de voz, não zap!) pra confirmar antes de fazer qualquer Pix.
* **Crédito Fácil que Pede Depósito Adiantado:** Promessa de empréstimo rápido sem consulta, mas tem que pagar uma "taxinha" antes? Golpe na certa, {tratamento}! Instituição séria não cobra pra liberar empréstimo.
* **Golpe do PIX Agendado ou Comprovante Falso:** Vendeu algo? Só entregue o produto depois que o dinheiro CAIR MESMO na sua conta. Comprovante pode ser forjado!

**Dicas de Ouro do {NOME_CHATBOT} pra se Proteger, {tratamento}:**
1.  **Desconfie Sempre:** Se a oferta é boa demais pra ser verdade, provavelmente é mentira.
2.  **Não Clique em Tudo:** Link estranho no e-mail, SMS ou zap? Melhor não clicar. Vá direto no site oficial da empresa ou do banco.
3.  **Senha é Segredo:** Sua senha é que nem escova de dente, não se empresta pra ninguém! Use senhas fortes e diferentes para cada serviço.
4.  **Autenticação de Dois Fatores (2FA):** Ative isso em tudo que der (banco, redes sociais, e-mail). É uma camada extra de segurança arretada!
5.  **Na Dúvida, NÃO FAÇA!** Se sentir que tem algo esquisito, pare, respire e peça ajuda ou verifique com a empresa/banco por um canal que VOCÊ conhece e confia.

Quer que o {NOME_CHATBOT} te conte um 'causo' de golpe pra você ver como os malandros agem, {tratamento.split()[0]}? Ou tem alguma dúvida específica sobre algum tipo de trambique? Manda aí que a gente tenta te deixar mais safo!
"""
    gatilhos_cenario_golpe = ["me conte um causo", "exemplo de golpe", "simulação de golpe", "como agem os golpistas"]
    if any(gatilho in mensagem_lower for gatilho in gatilhos_cenario_golpe):
        if not GOOGLE_API_KEY or not MODELO_GEMINI: return f"{resposta_base}\n\nOxe, {tratamento}, meu sistema de 'causos' tá na rede hoje."
        prompt_gemini_cenario = f"Você é o {NOME_CHATBOT} de Alagoas. O usuário '{tratamento}' pediu um exemplo de golpe comum. Descreva um cenário curto (3-5 frases) de golpe digital (boleto falso, phishing, etc), com sua persona alagoana, explicando o 'pulo do gato' do golpista e o 'alerta vermelho'."
        try:
            response = MODELO_GEMINI.generate_content(prompt_gemini_cenario)
            text_result = None
            if hasattr(response, 'text') and response.text: text_result = response.text
            if text_result and text_result.strip(): return f"{resposta_base}\n\n**O {NOME_CHATBOT} te conta um causo pra ficar ligado:**\n{text_result.strip()}\n\nLembre-se, {tratamento}: informação e desconfiança são suas melhores armas!"
            return f"{resposta_base}\n\nOxe, {tratamento}! Ia te contar um causo, mas meu repertório deu um branco."
        except Exception as e: return f"{resposta_base}\n\nRapaz, minha memória pra causo de golpe falhou agora, {tratamento}."
    return resposta_base

# NOVA FUNÇÃO PARA O PLANEJADOR DE SONHOS

# Dentro do seu chatbot_guia.py, na função modulo_planejador_sonhos:

def modulo_planejador_sonhos(mensagem_usuario_original):
    tratamento = obter_tratamento_usuario()
    # session.get('planejador_estado') já deve estar definido pela processar_mensagem_usuario ao entrar aqui pela primeira vez.
    # Se não estiver (improvável com a nova lógica), assume PEDINDO_SONHO.
    estado_atual = session.get('planejador_estado', 'PEDINDO_SONHO') 
    
    print(f"[{NOME_CHATBOT}] Planejador de Sonhos para {tratamento}. Estado: {estado_atual}. Mensagem: '{mensagem_usuario_original}'")

    resposta = ""

    if estado_atual == 'PEDINDO_SONHO':
        # A mensagem_usuario_original aqui pode ser o gatilho inicial (ex: "planejador")
        # ou já a resposta do usuário ao pedido explícito do sonho.
        # Precisamos de uma forma de diferenciar.
        # A lógica de 'contem_gatilho_inicial' ajuda, mas pode não ser perfeita.
        
        # Se a sessão 'sonho_atual' NÃO existe, então estamos realmente pedindo o sonho pela primeira vez neste fluxo.
        if 'sonho_atual' not in session:
            gatilhos_iniciais_planejador = ["planejador", "planejamento financeiro", "sonho", "meta", "objetivo", "simulador de planejamento"]
            mensagem_lower_sem_gatilho = mensagem_usuario_original.lower()
            
            # Verifica se a mensagem é um dos gatilhos E NADA MAIS, ou se é curta
            # Se for mais longa, ou não for um gatilho, assume que é a descrição do sonho
            eh_apenas_gatilho_curto = False
            for gatilho in gatilhos_iniciais_planejador:
                if mensagem_lower_sem_gatilho == gatilho:
                    eh_apenas_gatilho_curto = True
                    break
            if len(mensagem_lower_sem_gatilho.split()) <=2 and any(gatilho in mensagem_lower_sem_gatilho for gatilho in gatilhos_iniciais_planejador):
                 eh_apenas_gatilho_curto = True


            if not eh_apenas_gatilho_curto and mensagem_lower_sem_gatilho: # Se não for só um gatilho e não for vazia
                sonho_do_usuario = mensagem_usuario_original.strip()
                session['sonho_atual'] = sonho_do_usuario 
                session['planejador_estado'] = 'PEDINDO_CUSTO_SONHO'
                print(f"[{NOME_CHATBOT}] Sonho do usuário '{sonho_do_usuario}' salvo. Novo estado: PEDINDO_CUSTO_SONHO.")
                resposta = f"""Entendi, {tratamento}! Seu sonho é: **"{sonho_do_usuario}"**. Que massa! Adorei a ideia! 🚀
Agora, pra gente continuar nosso plano: você já tem uma ideia de **quanto mais ou menos custa para realizar esse sonho?**
(Pode ser um valor aproximado, {tratamento.split()[0]}!)"""
            else: # É o primeiro chamado com um gatilho, ou mensagem vazia (improvável aqui)
                resposta = f"""Que massa, {tratamento}! Fico arretado em te ajudar a tirar esses sonhos do papel e botar pra jogo! 🚀
O {NOME_CHATBOT} aqui adora um bom planejamento!
Para começarmos essa jornada rumo à sua conquista, me conta aí com suas palavras:
**Qual é o seu grande sonho ou objetivo para o seu negócio neste momento?**
(Por exemplo: "quero comprar um freezer novo", "preciso fazer um curso de confeitaria", "quero reformar minha loja", "juntar dinheiro para investir em marketing")"""
                # Garante que estamos neste estado para a próxima interação
                session['planejador_estado'] = 'PEDINDO_SONHO' 
        else: # 'sonho_atual' já existe na sessão, mas o estado ainda é PEDINDO_SONHO (não deveria acontecer com a lógica acima)
              # Isso pode significar que o usuário está tentando mudar o sonho. Por agora, vamos pedir o custo do sonho já registrado.
            session['planejador_estado'] = 'PEDINDO_CUSTO_SONHO'
            sonho_ja_registrado = session.get('sonho_atual', 'seu sonho')
            resposta = f"""Opa, {tratamento}, parece que já tínhamos anotado seu sonho como **"{sonho_ja_registrado}"**.
Você já tem uma ideia de **quanto mais ou menos custa para realizar esse sonho?**
(Pode ser um valor aproximado!)"""


    elif estado_atual == 'PEDINDO_CUSTO_SONHO':
        # ... (resto da função como antes) ...
        custo_sonho_str = mensagem_usuario_original.strip()
        session['custo_sonho_atual'] = custo_sonho_str 
        session['planejador_estado'] = 'PEDINDO_ECONOMIA'
        sonho_atual = session.get('sonho_atual', 'seu sonho')
        print(f"[{NOME_CHATBOT}] Custo '{custo_sonho_str}' para '{sonho_atual}' salvo. Novo estado: PEDINDO_ECONOMIA.")
        resposta = f"""Beleza, {tratamento}! Então o custo para "{sonho_atual}" é por volta de **{custo_sonho_str}**, certo?
Agora, pensando em juntar essa grana: **quanto você acha que consegue guardar por mês (ou por semana, se preferir) para esse objetivo**, sem se apertar demais no orçamento?
(Qualquer valor que você conseguir separar já é um passo importante, {tratamento.split()[0]}!)"""
    
    # Dentro do seu chatbot_guia.py, na função modulo_planejador_sonhos:

# ... (estados PEDINDO_SONHO e PEDINDO_CUSTO_SONHO como antes) ...

    elif estado_atual == 'PEDINDO_ECONOMIA':
        economia_str = mensagem_usuario_original.strip()
        session['economia_str_atual'] = economia_str # Guarda a string original da economia
        
        sonho_atual = session.get('sonho_atual', 'seu sonho')
        custo_str_atual = session.get('custo_sonho_atual', '0')

        print(f"[{NOME_CHATBOT}] Economia '{economia_str}' para '{sonho_atual}' (custo '{custo_str_atual}') informada.")

        # **PASSO 1: Processar os dados (extrair números e periodicidade)**
        # Esta é uma parte que pode ficar bem complexa para cobrir todos os formatos.
        # Vamos fazer uma extração simples por enquanto. Idealmente, usaríamos Gemini aqui também ou regex mais robustas.
        
        custo_numerico = 0.0
        try:
            # Tenta limpar a string de custo: remove "R$", pontos de milhar, substitui vírgula por ponto
            custo_limpo = custo_str_atual.lower().replace("r$", "").replace(".", "").replace(",", ".").strip()
            custo_numerico = float(custo_limpo)
        except ValueError:
            print(f"[{NOME_CHATBOT}] Não foi possível converter o custo '{custo_str_atual}' para número.")
            session['planejador_estado'] = 'PEDINDO_CUSTO_SONHO' # Volta para pedir o custo novamente
            return f"Oxe, {tratamento}, não entendi direito esse valor de custo ('{custo_str_atual}'). Pode me dizer o valor só com números, por favor? Exemplo: 10000 ou 150.50"

        economia_numerico = 0.0
        periodicidade_economia = "por mês" # Padrão
        try:
            economia_lower = economia_str.lower()
            # Tenta encontrar palavras-chave de periodicidade
            if "semana" in economia_lower:
                periodicidade_economia = "por semana"
            elif "dia" in economia_lower: # Menos comum para planejamento de sonho, mas possível
                periodicidade_economia = "por dia"
            
            # Remove palavras e R$ para extrair o número
            economia_limpa = economia_lower.replace("r$", "").replace("por semana", "").replace("semanal", "").replace("por mês", "").replace("mensal", "").replace("por dia", "").replace("diário", "").replace(".", "").replace(",", ".").strip()
            
            # Pega apenas a primeira sequência de números/ponto encontrada
            import re
            match = re.search(r'[\d\.]+', economia_limpa)
            if match:
                economia_numerico = float(match.group(0))
            else:
                raise ValueError("Número da economia não encontrado")

        except ValueError:
            print(f"[{NOME_CHATBOT}] Não foi possível converter a economia '{economia_str}' para número.")
            session['planejador_estado'] = 'PEDINDO_ECONOMIA' # Volta para pedir a economia novamente
            return f"Hummm, {tratamento}, não consegui entender esse valor de economia ('{economia_str}'). Pode me dizer o valor e se é por semana ou por mês? Exemplo: 500 por mês ou 100 por semana."

        if custo_numerico <= 0 or economia_numerico <= 0:
            session['planejador_estado'] = 'PEDINDO_ECONOMIA' # Ou PEDINDO_CUSTO_SONHO dependendo do erro
            return f"Opa, {tratamento}, parece que o valor do custo (R${custo_numerico:.2f}) ou da economia (R${economia_numerico:.2f}) não tá batendo. Precisamos de valores positivos pra calcular direitinho!"

        # **PASSO 2: Calcular o Prazo Estimado**
        prazo_calculado_str = ""
        if periodicidade_economia == "por mês":
            prazo_em_periodos = custo_numerico / economia_numerico
            unidade_periodo = "meses"
        elif periodicidade_economia == "por semana":
            prazo_em_periodos = custo_numerico / economia_numerico
            unidade_periodo = "semanas"
            # Opcional: converter para meses: prazo_em_periodos_meses = prazo_em_periodos / 4.345 
        else: # por dia
            prazo_em_periodos = custo_numerico / economia_numerico
            unidade_periodo = "dias"

        import math
        prazo_arredondado = math.ceil(prazo_em_periodos) # Arredonda para cima

        if unidade_periodo == "dias" and prazo_arredondado > 60: # Se for muitos dias, converte para meses
            prazo_arredondado = math.ceil(prazo_arredondado / 30.44)
            unidade_periodo = "meses"
        elif unidade_periodo == "semanas" and prazo_arredondado > 8: # Se for muitas semanas, converte para meses
            prazo_arredondado = math.ceil(prazo_arredondado / 4.345)
            unidade_periodo = "meses"

        prazo_calculado_str = f"{prazo_arredondado} {unidade_periodo}"
        if prazo_arredondado == 1: # Singular
            prazo_calculado_str = f"{prazo_arredondado} {unidade_periodo.replace('s', '')}"


        # **PASSO 3: Montar o Prompt para o Gemini e Gerar a Resposta Final**
        if not GOOGLE_API_KEY or not MODELO_GEMINI:
            # Fallback se Gemini não estiver disponível
            resposta = f"""Show de bola, {tratamento}! Com uma economia de R${economia_numerico:.2f} {periodicidade_economia} para o seu sonho de "{sonho_atual}" (que custa R${custo_numerico:.2f}), você levaria aproximadamente {prazo_calculado_str} para alcançar!
Parabéns pela iniciativa! Continue firme nesse propósito!
(O {NOME_CHATBOT} ainda está aprendendo a dar mais dicas personalizadas sobre isso.)"""
            session['planejador_estado'] = 'PLANEJAMENTO_CONCLUIDO'
            return resposta

        prompt_final_planejamento = f"""
Você é o {NOME_CHATBOT}, consultor financeiro gente boa de Alagoas.
O usuário '{tratamento}', tem o sonho de '{sonho_atual}', que custa aproximadamente R$ {custo_numerico:.2f}.
Ele(a) consegue economizar R$ {economia_numerico:.2f} {periodicidade_economia}.
Com base nisso, o prazo estimado para alcançar o sonho é de aproximadamente {prazo_calculado_str}.

Agora, Zé, monte uma mensagem gente boa e encorajadora para o {tratamento}:
1. Confirme de forma clara e amigável o sonho, o custo, a economia e o prazo calculado.
2. Dê parabéns pelo planejamento e pela disciplina de economizar.
3. Sugira 1 ou 2 dicas PRÁTICAS e CRIATIVAS que o {tratamento} poderia fazer para TENTAR ACELERAR esse prazo (ex: uma pequena renda extra relacionada ao negócio dele, revisar alguma despesa específica, procurar por versões mais baratas do item do sonho, etc.). Seja específico se possível, mas sem inventar informações sobre o negócio dele se não as tiver.
4. Ofereça-se para conectar com o módulo de "Crédito Amigo" (diga algo como: "Se quiser explorar um empurrãozinho financeiro, me pergunte sobre 'Crédito Amigo'!") se ele quiser explorar opções de adiantar o sonho, mas sempre lembrando de ser consciente.
5. Finalize com uma mensagem de incentivo bem alagoana, usando suas expressões típicas.
Use sua persona e linguagem regional. Mantenha a resposta útil, detalhada na medida certa e motivadora.
Evite frases como "Com base nisso..." no início da resposta, comece de forma mais natural.
"""
        try:
            print(f"[{NOME_CHATBOT}] Enviando dados do planejamento para Gemini...")
            generation_config_planejamento = genai.types.GenerationConfig(temperature=0.75) # Um pouco mais criativo
            response = MODELO_GEMINI.generate_content(prompt_final_planejamento, generation_config=generation_config_planejamento)
            
            text_result = None
            # (Reutilizar a mesma lógica de extração de texto da resposta do Gemini)
            if hasattr(response, 'text') and response.text and isinstance(response.text, str): text_result = response.text
            elif hasattr(response, 'parts') and response.parts: text_result = "".join(part.text for part in response.parts if hasattr(part, 'text') and isinstance(part.text, str))
            # ... (adicionar o caso dos candidates se necessário) ...
            
            if text_result and text_result.strip():
                resposta = text_result.strip()
            else:
                # Fallback se Gemini não der boa resposta
                resposta = f"""Arretado, {tratamento}! Para seu sonho de "{sonho_atual}" (R${custo_numerico:.2f}), economizando R${economia_numerico:.2f} {periodicidade_economia}, o prazo estimado é de {prazo_calculado_str}.
Continue focado que você chega lá! Se precisar de mais dicas, é só chamar!"""
            
            session['planejador_estado'] = 'PLANEJAMENTO_CONCLUIDO' # Novo estado final
            return resposta
        except Exception as e:
            print(f"[{NOME_CHATBOT}] Erro ao chamar Gemini para finalizar planejamento: {e}\n{traceback.format_exc()}")
            # Fallback em caso de erro com Gemini
            return f"Oxe, {tratamento}, deu um probleminha aqui pra montar seu plano final, mas seus dados estão salvos! Para seu sonho de R${custo_numerico:.2f}, economizando R${economia_numerico:.2f} {periodicidade_economia}, o prazo é de uns {prazo_calculado_str}. Continue firme!"
    
    elif estado_atual == 'PLANEJAMENTO_CONCLUIDO':
        # Se o usuário enviar outra mensagem depois do planejamento, a intenção será reavaliada.
        # Se ele chamar o planejador de novo, a processar_mensagem_usuario vai limpar os dados da sessão.
        sonho_concluido = session.get('sonho_atual', 'seu último sonho')
        resposta = f"""Opa, {tratamento}! Já fizemos um planejamento bem bacana para '{sonho_concluido}'. 
Se quiser começar um NOVO planejamento, é só me chamar de novo para o 'Planejador de Sonhos'. 
Ou posso te ajudar com outro assunto?"""
        # Limpar o estado para que a próxima mensagem seja reavaliada pela intenção geral
        if 'planejador_estado' in session: del session['planejador_estado']
        # Considerar limpar 'sonho_atual', 'custo_sonho_atual', 'economia_str_atual' também,
        # ou deixar para a processar_mensagem_usuario limpar quando a intenção PLANEJADOR_SONHOS for chamada de novo.
        return resposta

    else: # Estado desconhecido 
        if 'planejador_estado' in session: del session['planejador_estado']
        # ... (limpar outros dados da sessão do planejador)
        print(f"[{NOME_CHATBOT}] Estado do planejador limpo ou desconhecido ('{estado_atual}').")
        resposta = f"Opa, {tratamento}! Parece que a gente se perdeu um pouco no nosso planejamento. Se quiser começar um novo, é só me chamar para o 'Planejador de Sonhos'!"

    return resposta

def listar_termos_conhecidos():
    tratamento = obter_tratamento_usuario()
    mensagem = f"Opa, {tratamento}! O {NOME_CHATBOT} aqui já tem na ponta da língua os seguintes termos do nosso glossário local:\n"
    if not glossario_local_do_ze_TEMPLATE: mensagem = f"Oxe, {tratamento}, ainda tô montando meu caderninho de termos!"
    else:
        for termo in glossario_local_do_ze_TEMPLATE.keys(): mensagem += f"- {termo.capitalize()}\n"
    mensagem += f"\nE pode perguntar sobre 'Pix ou Maquininha', dicas de 'Caixa Forte', 'Alertas AntiGolpe' e sobre o nosso 'Planejador de Sonhos'! Se jogar um termo que não conheço de cabeça, dou meus pulos com o Gemini pra te ajudar, {tratamento}!"
    return mensagem

def pesquisar_termo_glossario(mensagem_usuario):
    mensagem_normalizada = mensagem_usuario.lower().strip()
    print(f"[{NOME_CHATBOT}] Pesquisando termo para (glossário): '{mensagem_normalizada}'")
    
    termo_encontrado_localmente_template = None
    termo_candidato_local = ""

    for termo_chave in glossario_local_do_ze_TEMPLATE.keys():
        if f" {termo_chave} " in f" {mensagem_normalizada} " or mensagem_normalizada == termo_chave:
            termo_encontrado_localmente_template = glossario_local_do_ze_TEMPLATE[termo_chave]
            termo_candidato_local = termo_chave; break 
    
    if termo_encontrado_localmente_template:
        tratamento = obter_tratamento_usuario()
        resposta_formatada = termo_encontrado_localmente_template.format(tratamento=tratamento)
        print(f"[{NOME_CHATBOT}] Termo '{termo_candidato_local}' encontrado no glossário local e formatado para {tratamento}.")
        return resposta_formatada
    
    saudacoes_iniciais_comuns = ["legal, ", "legal ", "show, ", "show ", "então, ", "então ", "ok, ", "ok ", "certo, ", "certo ", "massa, ", "massa ", "tipo assim, ", "tipo assim ", "tipo, ", "tipo ", "zé, ", "ze, ", "zé ", "ze "]
    mensagem_para_extracao = mensagem_normalizada
    for saudacao_inicio in saudacoes_iniciais_comuns:
        if mensagem_para_extracao.startswith(saudacao_inicio):
            mensagem_para_extracao = mensagem_para_extracao[len(saudacao_inicio):].strip(); print(f"[{NOME_CHATBOT}] Limpeza de saudação: '{mensagem_para_extracao}'"); break
    
    palavras_chave_extracao = ["o que é", "o que significa", "explique sobre", "explique", "definição de", "significado de", "fale sobre", "me fala sobre", "saber sobre", "sobre"]
    termo_para_gemini = ""
    for palavra_chave in palavras_chave_extracao:
        if palavra_chave in mensagem_para_extracao:
            try:
                idx_inicio_termo = mensagem_para_extracao.index(palavra_chave) + len(palavra_chave)
                termo_extraido = mensagem_para_extracao[idx_inicio_termo:].strip()
                preposicoes_artigos_inicio = ["o ", "a ", "os ", "as ", "um ", "uma ", "uns ", "umas ", "de ", "do ", "da ", "dos ", "das ", "em ", "no ", "na ", "nos ", "nas "]
                for prep_art in preposicoes_artigos_inicio:
                    if termo_extraido.startswith(prep_art): termo_extraido = termo_extraido[len(prep_art):].strip(); break
                for pontuacao in ["?", ".", "!"]:
                    if termo_extraido.endswith(pontuacao): termo_extraido = termo_extraido[:-1].strip()
                if termo_extraido and termo_extraido not in palavras_chave_extracao and len(termo_extraido.split()) <= 4: # Limite de palavras para um termo
                    termo_para_gemini = termo_extraido; print(f"[{NOME_CHATBOT}] Termo extraído (após palavra-chave '{palavra_chave}' e limpeza): '{termo_para_gemini}'"); break
            except ValueError: continue
        if termo_para_gemini: break
    
    if not termo_para_gemini and len(mensagem_para_extracao.split()) <= 3:
        palavras_curtas_ignoraveis = ["oi", "ok", "sim", "não", "valeu", "obrigado", "blz", "tchau", "teste", "pix", "qr code", "maquininha", "caixa", "legal", "show", "lista", "termos", "ajuda", "comandos"]
        if mensagem_para_extracao and mensagem_para_extracao not in palavras_curtas_ignoraveis and not any(saud in mensagem_para_extracao for saud in ["bom dia", "boa tarde", "boa noite"]):
             termo_para_gemini = mensagem_para_extracao; print(f"[{NOME_CHATBOT}] Mensagem curta (após limpeza) '{termo_para_gemini}' assumida como termo (glossário).")
    
    if termo_para_gemini:
        if len(termo_para_gemini.split()) > 7: return f"NENHUMA_ESPECIFICA_TERMO_LONGO: {termo_para_gemini}"
        return explicar_termo_com_gemini(termo_para_gemini)
    else:
        return f"NENHUMA_ESPECIFICA_EXTRACAO_FALHOU: {mensagem_usuario}"

# Dentro do seu chatbot_guia.py, modifique a função processar_mensagem_usuario:

def processar_mensagem_usuario(mensagem_usuario):
    mensagem_lower = mensagem_usuario.lower().strip()
    if not mensagem_lower:
        return f"Manda a prosa, {obter_tratamento_usuario()}! {NOME_CHATBOT} tá aqui todo ouvidos!"

    print(f"[{NOME_CHATBOT}] MENSAGEM RECEBIDA (roteador principal): '{mensagem_usuario}' (normalizada: '{mensagem_lower}')")
    tratamento = obter_tratamento_usuario()

    # --- NOVO: VERIFICAR SE ESTAMOS EM UM FLUXO DE PLANEJAMENTO ATIVO ---
    if session.get('planejador_estado') and session.get('planejador_estado') != 'INICIO': 
        # Se existe um estado no planejador (e não é o estado inicial que pode ser acionado por uma nova intenção)
        # então a mensagem é uma resposta para o planejador.
        print(f"[{NOME_CHATBOT}] Roteador: Detectado estado ativo do Planejador de Sonhos ('{session.get('planejador_estado')}'). Encaminhando diretamente.")
        return modulo_planejador_sonhos(mensagem_usuario)
    # --- FIM DA NOVA VERIFICAÇÃO ---

    # Se não estamos em um fluxo ativo do planejador, classificamos a intenção
    intencao = obter_intencao_com_gemini(mensagem_lower)
    print(f"[{NOME_CHATBOT}] Intenção Principal Identificada: {intencao}")

    if intencao == "SAUDACAO": return saudacao_inicial()
    elif intencao == "PIX_MAQUININHA": return modulo_pix_maquininha(mensagem_usuario)
    elif intencao == "CAIXA_FORTE": return modulo_caixa_forte(mensagem_usuario)
    elif intencao == "ALERTA_ANTIGOLPE": return modulo_alerta_antigolpe(mensagem_usuario)
    elif intencao == "PLANEJADOR_SONHOS":
        # Ao iniciar o planejador, garantimos que o estado é setado para o começo
        session['planejador_estado'] = 'PEDINDO_SONHO' 
        # Limpar dados de sonhos anteriores, caso existam, para um novo planejamento
        if 'sonho_atual' in session: del session['sonho_atual']
        if 'custo_sonho_atual' in session: del session['custo_sonho_atual']
        if 'economia_atual' in session: del session['economia_atual']
        print(f"[{NOME_CHATBOT}] Roteador: Iniciando Planejador de Sonhos. Estado definido para PEDINDO_SONHO.")
        return modulo_planejador_sonhos(mensagem_usuario) # Passa a mensagem original, que pode conter o gatilho
    elif intencao == "GLOSSARIO_TERMO":
        resposta_glossario = pesquisar_termo_glossario(mensagem_usuario)
        if resposta_glossario.startswith("NENHUMA_ESPECIFICA_"):
             return f"Oxe, {tratamento}, o {NOME_CHATBOT} ficou aqui matutando sobre '{mensagem_usuario}' mas não achei um termo claro pra te explicar... Pode tentar perguntar 'o que é [termo]' ou peça a 'lista de termos'?"
        return resposta_glossario
    elif intencao == "LISTAR_FUNCIONALIDADES":
        # ... (código da lista de funcionalidades como antes) ...
        resposta_funcionalidades = listar_termos_conhecidos()
        resposta_funcionalidades += f"\n\nAlém disso, {tratamento}, o {NOME_CHATBOT} pode te ajudar com temas como:"
        resposta_funcionalidades += "\n- Dicas sobre Pix ou Maquininha."
        resposta_funcionalidades += "\n- Conselhos para um Caixa Forte e controle financeiro."
        resposta_funcionalidades += "\n- Alertas para você não cair em golpes."
        resposta_funcionalidades += "\n- E nosso novo Planejador de Sonhos para o seu negócio!"
        resposta_funcionalidades += f"\nÉ só perguntar que o {NOME_CHATBOT} se vira nos trinta pra te ajudar!"
        return resposta_funcionalidades
    elif intencao == "DESPEDIDA":
        # Ao se despedir, podemos limpar o estado do planejador também, se ele estiver ativo.
        if 'planejador_estado' in session: del session['planejador_estado']
        if 'sonho_atual' in session: del session['sonho_atual']
        # ... (limpar outros dados da sessão do planejador)
        return f"Até mais, {tratamento}! Precisando, é só chamar o {NOME_CHATBOT}! Sucesso aí no seu corre!"
    elif intencao == "NENHUMA_ESPECIFICA":
        return f"Oxe, {tratamento}, o {NOME_CHATBOT} ficou aqui matutando sobre '{mensagem_usuario}'... Não peguei bem o que você quis dizer. Pode tentar perguntar de um jeito diferente ou sobre um dos meus temas principais?"
    else: 
        print(f"[{NOME_CHATBOT}] ERRO: Intenção desconhecida recebida: {intencao}")
        return f"Eita, {tratamento}! {NOME_CHATBOT} se embananou todo aqui. Pode repetir, por favor?"

# --- Endpoints Flask ---
@app.route('/') 
def home():
    print(f"[{NOME_CHATBOT}] Servindo a página principal do chat (index.html). Usuário na sessão: {session.get('user_name')}")
    return render_template('index.html')

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    resposta_bot = f"Oxe! Alguma coisa deu muito errado aqui no {NOME_CHATBOT} e ele não soube o que dizer."
    mensagem_recebida_para_log = ""
    nome_enviado_pelo_frontend = None
    try:
        if request.method == 'POST':
            dados_recebidos = request.json
            mensagem_usuario = dados_recebidos.get('mensagem', '').strip()
            nome_enviado_pelo_frontend = dados_recebidos.get('nome_usuario')
            mensagem_recebida_para_log = mensagem_usuario
        elif request.method == 'GET':
            mensagem_usuario = request.args.get('mensagem', '').strip()
            nome_enviado_pelo_frontend = request.args.get('nome_usuario')
            mensagem_recebida_para_log = mensagem_usuario
        else: return jsonify({'resposta_bot': 'Método não suportado.'}), 405

        if nome_enviado_pelo_frontend:
            nome_enviado_limpo = nome_enviado_pelo_frontend.strip()
            if nome_enviado_limpo and session.get('user_name') != nome_enviado_limpo :
                session['user_name'] = nome_enviado_limpo
                print(f"[{NOME_CHATBOT}] Nome do usuário '{session['user_name']}' salvo/atualizado na sessão.")
                if mensagem_usuario in ["REGISTRO_DE_NOME_USUARIO", "REINICIO_SESSAO_COM_NOME"]:
                    return jsonify({'resposta_bot': f"Beleza, {obter_tratamento_usuario()}! Nome registrado. Manda a pergunta!"})
        if not mensagem_usuario:
            resposta_bot = f'Manda a prosa, {obter_tratamento_usuario()}! {NOME_CHATBOT} tá aqui todo ouvidos!'
        else:
            resposta_bot = processar_mensagem_usuario(mensagem_usuario)
        return jsonify({'resposta_bot': resposta_bot})
    except Exception as e:
        print(f"[{NOME_CHATBOT}] ERRO GRAVE no endpoint para mensagem '{mensagem_recebida_para_log}': {e}\n{traceback.format_exc()}")
        return jsonify({'resposta_bot': f"Eita gota, {obter_tratamento_usuario()}! {NOME_CHATBOT} teve um piripaque feio."}), 500

# --- Para rodar o aplicativo Flask localmente ---
if __name__ == '__main__':
    print(f"[{NOME_CHATBOT}] Iniciando o servidor Flask...")
    if not GOOGLE_API_KEY or not MODELO_GEMINI:
        print(f"[{NOME_CHATBOT}] ALERTA: {NOME_CHATBOT} vai operar em MODO LIMITADO...")
    app.run(debug=True, host='0.0.0.0', port=5000)