# Zé do Financeiro - Seu Guia de Bolso para o Microempreendedor Digitalizado! 💰💡

## Sobre o Projeto

O **Zé do Financeiro** é um chatbot gente boa, com sotaque arretado do Nordeste, criado para ser o melhor amigo do microempreendedor e do trabalhador autônomo na hora de desenrolar as finanças no mundo digital. Ele dá dicas sobre contas PJ digitais, compara taxas de maquininhas e Pix, ajuda com noções de fluxo de caixa usando apps bancários, orienta sobre microcrédito consciente e ainda te deixa esperto para não cair em golpes online!

Este projeto foi desenvolvido como parte da **Imersão IA da Alura com Gemini**, e é um exemplo prático de como a Inteligência Artificial pode ser usada para criar soluções úteis e com um toque regional e humano.

---

🚀 **Uma Jornada de Última Hora com um Guerreiro Celeron!** 🚀

Este projeto tem uma história especial de superação! Desenvolvido com muita paixão e café, grande parte do "Zé do Financeiro" ganhou vida no *último dia de entrega da Imersão IA Alura*. Tudo isso foi codificado em um valente computador Intel Celeron de 2 núcleos e 2 threads, que bravamente enfrentou os desafios de rodar o ambiente de desenvolvimento e, às vezes, até mesmo um navegador de internet! Se o Zé te ajudar, agradeça também a esse Celeron guerreiro que não desistiu! 😄

---

## Funcionalidades Implementadas

O Zé do Financeiro já está esperto e pode te ajudar com:

* **🗣️ Conversa Personalizada:** Ele pergunta seu nome e te trata de forma única durante o papo!
* **📖 Glossário Financeiro:** Não entendeu um termo? Pergunta pro Zé! Se ele não souber de cabeça, ele consulta o Gemini para te explicar com aquele jeitinho alagoano.
* **💳 Pix ou Maquininha?:** Ajuda a entender as vantagens e desvantagens de cada um para o seu negócio.
* **📊 Caixa Forte, Negócio Forte:** Dicas essenciais sobre controle financeiro, fluxo de caixa e a importância de separar as contas pessoais das da empresa. O Zé também pode responder perguntas específicas sobre esse tema com a ajuda do Gemini.
* **🛡️ Alerta Vermelho AntiGolpe:** Informações sobre os principais golpes online e como se proteger. O Zé pode até te contar uns "causos" de golpes para te deixar mais safo, com cenários gerados pelo Gemini.
* **🎯 Planejador de Sonhos:**
    * O Zé inicia a conversa para te ajudar a planejar seus objetivos de negócio!
    * Ele pergunta qual seu sonho, o custo estimado e quanto você pode economizar.
    * Com essas informações, ele calcula um prazo e usa o Gemini para te dar uma resposta encorajadora com dicas práticas para alcançar sua meta.
* **💬 Interface Web Simples:** Você pode conversar com o Zé através de uma interface web amigável no seu navegador.
* **💾 Histórico de Chat:** A conversa fica salva no seu navegador (`localStorage`) para você poder continuar ou rever depois.

## Tecnologias Utilizadas

* **Python:** A linguagem principal do backend do Zé.
* **Flask:** O microframework web que faz o Zé funcionar na internet.
* **Google Gemini API:** A inteligência artificial poderosa que ajuda o Zé a entender suas perguntas, classificar intenções, explicar termos e gerar conteúdo criativo e personalizado.
* **HTML, CSS, JavaScript:** Para construir a interface web onde você conversa com o Zé.
* **Git & GitHub:** Para controlar as versões e hospedar esse projeto arretado!
* **Força de Vontade e um Intel Celeron de 2 núcleos!** 💪

## Como Rodar o Projeto Localmente

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/AgsonPereira/ze-do-financeiro-chatbot.git](https://github.com/AgsonPereira/ze-do-financeiro-chatbot.git)
    cd ze-do-financeiro-chatbot
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate    # No Windows
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install Flask google-generativeai python-dotenv
    ```

4.  **Configure suas Chaves de API:**
    * Crie um arquivo chamado `.env` na raiz do projeto (na pasta `ze-do-financeiro-chatbot`).
    * Adicione suas chaves dentro dele. Você pode usar o arquivo `.env.example` (se você o criou e adicionou ao repositório) como modelo:
      ```env
      # Conteúdo para seu arquivo .env
      GOOGLE_API_KEY="SUA_CHAVE_GEMINI_AQUI"
      FLASK_SECRET_KEY="GERAR_UMA_CHAVE_FLASK_FORTE_E_ALEATORIA_AQUI"
      ```

5.  **Execute o Aplicativo Flask:**
    ```bash
    python chatbot_guia.py
    ```

6.  **Acesse no Navegador:**
    * Abra seu navegador e vá para `http://127.0.0.1:5000/`

## Próximos Passos (Ideias para o Futuro)

* Completar os módulos "Descomplica PJ Digital" e "Crédito Amigo".
* Aprofundar a interatividade do "Planejador de Sonhos" com mais cálculos e sugestões do Gemini.
* Melhorar ainda mais a capacidade do Zé de entender linguagem natural e extrair informações das frases dos usuários.
* Explorar a integração com plataformas de mensagens como WhatsApp ou Telegram.
* Adicionar um sistema de feedback para os usuários avaliarem as respostas do Zé.
* Comprar um computador novo para programar! 😉 (Brincadeira!)

## Contribuição

Este projeto foi uma jornada incrível de aprendizado. Se você tiver ideias ou sugestões, sinta-se à vontade para abrir uma *issue* ou um *pull request* no repositório!

---

Feito com muito esforço e carinho por **Agson Pereira** diretamente de **Rio Largo, Alagoas, Brasil!** ☀️🌴

---
Vídeo de Apresentação:

https://github.com/user-attachments/assets/ed4a0606-de41-4f5e-9987-c1293a59176b


