import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import requests
from openai import OpenAI
import re

# Função para extrair o ID do vídeo do YouTube


def extract_video_id(url):
    # Verifica diferentes formatos de URLs do YouTube
    patterns = [
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([^&?/]+)'
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None

# Função para extrair o transcript de um vídeo do YouTube


def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        for transcript_obj in transcript_list:
            try:
                transcript = transcript_obj.fetch()
                break
            except Exception as e:
                st.error(f"Erro ao buscar transcript: {e}")
                continue
        if not transcript:
            st.warning(
                "Não foi possível encontrar um transcript para este vídeo. Verifique se o vídeo possui legendas habilitadas.")
            return None
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except NoTranscriptFound:
        st.warning(
            "Não foi possível encontrar um transcript para este vídeo. Talvez o vídeo seja muito recente ou não possua legendas.")
        return None
    except TranscriptsDisabled:
        st.error("Transcripts estão desativados para este vídeo.")
        return None
    except Exception as e:
        st.error(f"Erro ao obter o transcript: {e}")
        return None

# Função para resumir e traduzir o transcript usando o ChatGPT


def summarize_transcript(transcript):
    api_key = st.secrets["openai"]["openai_key"]
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[
            {
                "role": "system",
                "content": """
        # Instruções para o Professor AI

        Aja como um professor especialista no assunto e siga estas etapas para explicar o tópico com base no seguinte fluxo estruturado:

        ## Visão Geral
        Forneça uma explicação inicial simples e objetiva para introduzir o conceito principal.

        ## Analogia
        Utilize uma analogia do mundo real para facilitar a compreensão do conceito por parte do usuário.

        ## Explicação Progressiva
        Aprofunde o conceito de maneira gradual, aumentando a complexidade em cada etapa com exemplos e detalhes que reforcem a aprendizagem.

        ## Relações
        Estabeleça conexões entre o conceito e áreas de conhecimento pré-existentes do usuário, se aplicável.

        ## Exemplos Práticos
        Forneça exemplos práticos que demonstrem a aplicação do conceito no dia a dia ou em contextos relevantes.

        ## Detalhes Técnicos
        Explique os aspectos mais técnicos e complexos do conceito, adequando-se ao nível do usuário.

        ---

        ## Fluxo de Pensamento e Reflexão

        Sempre que estiver explicando ou resolvendo um problema, siga estas diretrizes estruturadas:

        ### <thinking>
        1. Analise brevemente a questão e delineie sua abordagem.
        2. Apresente um plano claro de etapas para resolver o problema.
        3. Utilize um processo de raciocínio em "Cadeia de Pensamentos", dividindo seu processo de pensamento em etapas numeradas.
        </thinking>

        ### <reflection>
        1. Reveja seu raciocínio.
        2. Verifique potenciais erros ou falhas.
        3. Confirme ou ajuste sua conclusão, se necessário.
        4. Feche todas as seções de reflexão de maneira apropriada.
        </reflection>

        Após cobrir os pontos acima, peça ao usuário para:

        1. **Resumo**: Incentive o usuário a resumir o que entendeu para solidificar o aprendizado. Ofereça correções e feedback para esclarecer qualquer mal-entendido.

        2. **Perguntas de Acompanhamento**: Sugira perguntas de acompanhamento para aprofundar o entendimento do tópico.

        ## Interatividade
        Encoraje o usuário a fazer conexões com outros conceitos que já conhece e explore questões adicionais que ele possa ter. Use perguntas esclarecedoras e uma linguagem acessível ao longo de todo o processo, garantindo uma abordagem interativa e personalizada.

        Lembre-se de sempre fechar suas seções de <thinking> e <reflection>, e usar essas tags de forma separada.
        """
            },
            {
                "role": "user",
                "content": f"{transcript}"
            }
        ],
        temperature=0.7,
    )

    if response and response.choices:
        return response.choices[0].message.content
    else:
        return "Nenhuma resposta válida foi retornada pela API."

# Interface do Streamlit


def main():
    st.title("Assistente de Resumo de Vídeos do YouTube")

    # Entrada do link do YouTube
    youtube_url = st.text_input("Cole o link do YouTube aqui:")

    if st.button("Extrair e Resumir"):
        if youtube_url:
            # Extrair o ID do vídeo do URL
            video_id = extract_video_id(youtube_url)

            if video_id:
                with st.spinner("Obtendo o transcript do vídeo..."):
                    transcript = get_youtube_transcript(video_id)

                if transcript:
                    with st.spinner("Gerando o resumo..."):
                        summary = summarize_transcript(transcript)

                    if summary:
                        st.subheader("Resumo:")
                        st.write(summary)
                    else:
                        st.error("Não foi possível gerar o resumo.")
                else:
                    st.error("Não foi possível obter o transcript do vídeo.")
            else:
                st.error(
                    "Não foi possível extrair o ID do vídeo. Verifique o link do YouTube.")
        else:
            st.error("Por favor, insira um link válido do YouTube.")


if __name__ == "__main__":
    main()
