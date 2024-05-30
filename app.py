import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import openai

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
                st.write(f"Erro ao buscar transcript: {e}")
                continue
        if not transcript:
            st.write("Não foi possível encontrar um transcript para este vídeo.")
            return None
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except NoTranscriptFound:
        st.write("Não foi possível encontrar um transcript para este vídeo.")
        return None
    except TranscriptsDisabled:
        st.write("Transcripts estão desativados para este vídeo.")
        return None
    except Exception as e:
        st.write(f"Erro ao obter o transcript: {e}")
        return None

# Função para resumir e traduzir o transcript usando o ChatGPT


def summarize_transcript(transcript):
    try:
        openai.api_key = st.secrets["openai"]["openai_key"]
        response = openai.Completion.create(
            model="gpt-4",
            prompt=f"Você é um assistente que faz resumos detalhados e separa em tópicos. Por favor, traduza e resuma os principais pontos do seguinte transcript: {transcript}",
            temperature=0.7,
            max_tokens=500
        )
        if response and response.choices:
            summary = response.choices[0].text.strip()
            return summary
        else:
            return "Não foi possível gerar um resumo."
    except Exception as e:
        st.write(f"Erro ao chamar a API do OpenAI: {e}")
        return None

# Interface do Streamlit


def main():
    st.title("Assistente de Resumo de Vídeos do YouTube")

    # Entrada do link do YouTube
    youtube_url = st.text_input("Cole o link do YouTube aqui:")

    if st.button("Extrair e Resumir"):
        if youtube_url:
            # Extrair o ID do vídeo do URL
            video_id = youtube_url.split("v=")[-1]

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
            st.error("Por favor, insira um link válido do YouTube.")


if __name__ == "__main__":
    main()
