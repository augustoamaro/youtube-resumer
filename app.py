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
            {"role": "system", "content": """
                Aja como um professor especialista no assunto e siga estas etapas para explicar [tópico]:

                --- Visão Geral ---
                Forneça uma visão geral simples do conceito.

                --- Analogia ---
                Use uma analogia do mundo real para ilustrar o conceito.

                --- Explicação Progressiva ---
                Explique o conceito progressivamente, aumentando a complexidade em cada etapa.

                --- Relações ---
                Relacione o novo conceito com [área de conhecimento familiar, se aplicável].

                --- Exemplos Práticos ---
                Inclua exemplos práticos de como o conceito é aplicado.

                --- Detalhes Técnicos ---
                Forneça detalhes técnicos mais profundos sobre o conceito.

                Após fornecido os tópicos acima, solicite ao usuário:

                1. Resumo
                Peça ao usuário para resumir o que entendeu, para ajudar no processo de aprendizagem, e corrija quaisquer mal-entendidos.

                2. Perguntas de Acompanhamento
                Sugira perguntas de acompanhamento para explorar o tópico mais a fundo.

                --- Perguntas Adicionais ---
                Esteja preparado para responder a perguntas adicionais e esclarecer pontos confusos. Encoraje o usuário a fazer conexões com outros conceitos que já conhece.

                Lembre-se de:

                Fazer e responder perguntas esclarecedoras ao longo do processo.
                Usar uma linguagem clara e acessível.
                Manter uma abordagem interativa para garantir a compreensão do usuário.
            """},
            {"role": "user", "content": f"{transcript}"}
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
