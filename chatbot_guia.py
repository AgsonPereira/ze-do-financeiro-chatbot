# chatbot_guia.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import traceback # Para imprimir o traceback completo do erro, se necessário
from flask import Flask, request, jsonify

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
        # Tenta carregar o modelo aqui
        MODELO_GEMINI = genai.GenerativeModel('gemini-1.5-flash') # Ou 'gemini-pro' se preferir/precisar
        print(f"[{NOME_CHATBOT}] Modelo Gemini '{MODELO_GEMINI.model_name}' carregado e pronto pra desenrolar!")
    except Exception as e:
        print(f"[{NOME_CHATBOT}] Oxe! Deu um erro ao configurar o Gemini ou carregar o modelo: {e}")
        print(f"[{NOME_CHATBOT}] Detalhes do erro: {traceback.format_exc()}")
        print(f"[{NOME_CHATBOT}] Verifique sua API Key, conexão com a internet e se o modelo 'gemini-1.5-flash' está disponível para sua conta.")
        GOOGLE_API_KEY = None # Define como None para indicar que Gemini não está funcional
        MODELO_GEMINI = None


def saudacao_inicial():
    return f"Chegue mais, meu patrão/minha patroa! Sou o {NOME_CHATBOT}, seu parceiro aqui de Alagoas pra gente desenrolar as finanças do seu negócio. Pode perguntar o significado de termos financeiros ou pedir a 'lista de termos' que eu já aprendi!"

glossario_local_do_ze = {
    "mei": f"Aí sim, patrão/patroa! MEI é o Microempreendedor Individual. É tipo um atalho pra você que trampa por conta própria ter seu CNPJ, emitir nota, essas paradas todas...", # Mantenha suas definições locais
    "cnpj": f"CNPJ, meu consagrado(a), é o Cadastro Nacional da Pessoa Jurídica. É tipo o CPF, só que pra sua empresa...",
    "conta pj": f"Conta PJ é uma conta no banco feita especialmente pra sua empresa, separada da sua conta pessoal...",
    "pix": f"O Pix é aquele jeito ligeiro e quase sempre de graça pra gente pequena mandar e receber dinheiro...",
    "qr code": f"QR Code é tipo um código de barras moderninho, um quadradinho cheio de quadradinhos menores...",
    "fluxo de caixa": f"Fluxo de caixa, meu camarada, é o controle de toda grana que entra e sai do seu negócio...",
    "capital de giro": f"Capital de giro é aquela reserva esperta que você precisa ter pra manter o negócio funcionando no dia a dia...",
    "microcrédito": f"Microcrédito é um tipo de empréstimo com valor mais baixo, pensado pra ajudar o pequeno empreendedor..."
    # Adicione mais termos locais se quiser
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
        # print(f"[{NOME_CHATBOT}] DEBUG - Prompt enviado ao Gemini:\n---\n{prompt}\n---") # Descomente para ver o prompt exato

        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            # max_output_tokens=150 # Descomente se quiser limitar o tamanho da resposta
        )
        
        response = MODELO_GEMINI.generate_content(prompt, generation_config=generation_config)
        
        print(f"[{NOME_CHATBOT}] Resposta recebida do Gemini para '{termo_usuario}'.")
        # print(f"[{NOME_CHATBOT}] DEBUG - Resposta bruta do Gemini: {vars(response) if hasattr(response, '__dict__') else response}") # Descomente para depuração profunda

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
                safety_info = ""
                if hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'safety_ratings'):
                    safety_info = f" (Safety Ratings: {response.candidates[0].safety_ratings})"
                block_reason_msg += safety_info
                return f"Oxe, meu patrão/minha patroa! O sistema avançado não quis falar sobre '{termo_usuario}'. {block_reason_msg} Vamos tentar outro?"
            
            print(f"[{NOME_CHATBOT}] Resposta do Gemini para '{termo_usuario}' veio vazia ou em formato não reconhecido. {block_reason_msg} Resposta completa: {vars(response) if hasattr(response, '__dict__') else response}")
            return f"Eita gota! O {NOME_CHATBOT} tentou desenrolar sobre '{termo_usuario}' com o sistema avançado, mas a resposta veio meio... em branco ou esquisita. {block_reason_msg} Parece que nem ele pegou a ideia dessa vez. Que tal outro termo?"

    except Exception as e:
        print(f"[{NOME_CHATBOT}] Deu um erro arretado ao tentar falar com o Gemini sobre '{termo_usuario}': {e}\n{traceback.format_exc()}")
        return f"Rapaz, deu um piripaque daqueles na minha conexão com o sistema avançado pra explicar '{termo_usuario}'. A antena deve ter caído! Tenta de novo daqui a pouquinho. (Detalhe do erro: {type(e).__name__})"

def listar_termos_conhecidos():
    if not glossario_local_do_ze:
        return f"Oxe, ainda tô aprendendo os termos, {NOME_CHATBOT} aqui tá começando! Volte mais tarde."
    
    mensagem = f"Opa! O {NOME_CHATBOT} aqui já tem na ponta da língua um bocado de coisa, visse? Se liga nos termos que eu posso te explicar do meu caderninho:\n"
    for termo in glossario_local_do_ze.keys():
        mensagem += f"- {termo.capitalize()}\n"
    mensagem += f"\nMas se você jogar um termo diferente, eu dou meus pulos com meu sistema avançado pra tentar te ajudar! É só perguntar, tipo: 'O que é {list(glossario_local_do_ze.keys())[0]}?' ou 'Me explique {list(glossario_local_do_ze.keys())[0]}'."
    return mensagem

def pesquisar_termo_glossario(mensagem_usuario):
    mensagem_normalizada = mensagem_usuario.lower().strip()
    print(f"[{NOME_CHATBOT}] Pesquisando termo para: '{mensagem_normalizada}'")
    
    termo_encontrado_localmente = None
    termo_candidato_local = ""

    for termo_chave in glossario_local_do_ze.keys():
        if termo_chave.lower() in mensagem_normalizada:
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
        # Verifica se a mensagem começa com a palavra-chave seguida de um espaço
        if mensagem_normalizada.startswith(palavra_chave + " "):
            termo_extraido = mensagem_normalizada.split(palavra_chave + " ", 1)[1].strip()
            # Remove pontuações comuns do final do termo
            for pontuacao in ["?", ".", "!"]:
                if termo_extraido.endswith(pontuacao):
                    termo_extraido = termo_extraido[:-1].strip()
            
            if termo_extraido:
                termo_para_gemini = termo_extraido
                print(f"[{NOME_CHATBOT}] Termo extraído para Gemini (após palavra-chave '{palavra_chave}'): '{termo_para_gemini}'")
                break 
    
    if not termo_para_gemini and len(mensagem_normalizada.split()) <= 3:
        palavras_curtas_ignoraveis = ["oi", "ok", "sim", "não", "valeu", "obrigado", "blz", "tchau", "teste"] # Adicione mais se necessário
        if mensagem_normalizada not in palavras_curtas_ignoraveis and not any(saud in mensagem_normalizada for saud in ["bom dia", "boa tarde", "boa noite"]):
             termo_para_gemini = mensagem_normalizada
             print(f"[{NOME_CHATBOT}] Mensagem curta '{termo_para_gemini}' assumida como termo para Gemini.")

    if termo_para_gemini:
        # Verifica se o termo para o Gemini não é excessivamente longo ou parece uma frase completa
        if len(termo_para_gemini.split()) > 7: # Limite arbitrário de 7 palavras para um "termo"
            print(f"[{NOME_CHATBOT}] Termo extraído '{termo_para_gemini}' é muito longo, não vou enviar ao Gemini. Respondendo com mensagem padrão.")
            return f"Oxe, {NOME_CHATBOT} acha que '{termo_para_gemini}' é mais uma frase do que um termo pra explicar. Tenta algo mais direto ou um termo do nosso glossário!"
        
        print(f"[{NOME_CHATBOT}] Termo '{termo_para_gemini}' não encontrado localmente. Tentando com Gemini...")
        return explicar_termo_com_gemini(termo_para_gemini)
    else:
        print(f"[{NOME_CHATBOT}] Não foi possível extrair um termo claro da mensagem: '{mensagem_usuario}'. Respondendo com mensagem padrão.")
        return f"Oxe, {NOME_CHATBOT} não entendeu bem o que você quis dizer com '{mensagem_usuario}'. Tente perguntar 'o que é [termo]?' ou peça a 'lista de termos'."

# --- Lógica Principal do Chatbot (Roteamento) ---
def processar_mensagem_usuario(mensagem_usuario):
    mensagem_lower = mensagem_usuario.lower().strip()
    print(f"[{NOME_CHATBOT}] MENSAGEM RECEBIDA DO USUÁRIO (processar_mensagem_usuario): '{mensagem_usuario}' (normalizada: '{mensagem_lower}')")

    if not mensagem_lower:
        return f"Manda a prosa, meu patrão/minha patroa! {NOME_CHATBOT} tá aqui todo ouvidos!"

    saudacoes = ["oi", "olá", "e aí", "iai", "opa", "salve", "bom dia", "boa tarde", "boa noite"]
    if mensagem_lower in saudacoes or any(mensagem_lower.startswith(s) and len(mensagem_lower.split()) <=3 for s in saudacoes) :
        print(f"[{NOME_CHATBOT}] Mensagem reconhecida como saudação.")
        return saudacao_inicial()

    print(f"[{NOME_CHATBOT}] Mensagem não é saudação, encaminhando para pesquisa de termo...")
    return pesquisar_termo_glossario(mensagem_usuario) # Passa a mensagem original para manter capitalização se necessário para extração

# --- Endpoint para receber mensagens (simulando o WhatsApp) ---
@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    resposta_bot = f"Oxe! Alguma coisa deu muito errado aqui no {NOME_CHATBOT} e ele não soube o que dizer." # Resposta padrão de erro
    
    if request.method == 'POST':
        try:
            dados_recebidos = request.json
            mensagem_usuario = dados_recebidos.get('mensagem', '').strip()
            print(f"[{NOME_CHATBOT}] Requisição POST recebida. Mensagem: '{mensagem_usuario}'")
            
            if not mensagem_usuario:
                resposta_bot = f'Manda a mensagem aí, meu patrão/patroa! {NOME_CHATBOT} tá no aguardo.'
            else:
                resposta_bot = processar_mensagem_usuario(mensagem_usuario)
        except Exception as e:
            print(f"[{NOME_CHATBOT}] ERRO GRAVE no endpoint POST: {e}\n{traceback.format_exc()}")
            resposta_bot = f"Eita gota! {NOME_CHATBOT} teve um piripaque feio processando sua mensagem. Tente de novo ou avise o técnico!"
        
        return jsonify({'resposta_bot': resposta_bot})
    
    elif request.method == 'GET':
        try:
            mensagem_teste = request.args.get('mensagem', '').strip() # Pega o parâmetro 'mensagem' da URL
            print(f"[{NOME_CHATBOT}] Requisição GET recebida. Mensagem: '{mensagem_teste}'")

            if not mensagem_teste: # Se nenhuma mensagem for passada via GET, manda a saudação.
                print(f"[{NOME_CHATBOT}] Mensagem GET vazia, respondendo com saudação.")
                resposta_bot = saudacao_inicial()
            else:
                resposta_bot = processar_mensagem_usuario(mensagem_teste)
        except Exception as e:
            print(f"[{NOME_CHATBOT}] ERRO GRAVE no endpoint GET: {e}\n{traceback.format_exc()}")
            resposta_bot = f"Eita gota! {NOME_CHATBOT} teve um piripaque feio processando seu teste. Tente de novo ou avise o técnico!"

        return jsonify({'resposta_bot': resposta_bot})

# --- Para rodar o aplicativo Flask localmente ---
if __name__ == '__main__':
    print(f"[{NOME_CHATBOT}] Iniciando o servidor Flask...")
    if not GOOGLE_API_KEY or not MODELO_GEMINI:
        print(f"[{NOME_CHATBOT}] ALERTA: {NOME_CHATBOT} vai operar em MODO LIMITADO pois a API do Gemini não está completamente configurada (verifique GOOGLE_API_KEY e o carregamento do MODELO_GEMINI).")
    
    # host='0.0.0.0' permite acesso de outros dispositivos na mesma rede
    # debug=True é ótimo para desenvolvimento, mas DESATIVE para produção
    app.run(debug=True, host='0.0.0.0', port=5000)