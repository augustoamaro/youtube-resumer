import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
import openai

# Função para extrair o transcript de um vídeo do YouTube em português


def get_youtube_transcript(video_id, lang='en, pt'):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=[lang])
        transcript = " ".join([entry['text'] for entry in transcript_list])
        return transcript
    except NoTranscriptFound:
        st.write(
            "Não foi possível encontrar um transcript em português para este vídeo.")
        return None
    except Exception as e:
        st.write(f"Erro ao obter o transcript: {e}")
        return None

# Função para resumir o transcript usando o ChatGPT


def summarize_transcript(transcript):
    openai.api_key = st.secrets["openai"]["openai_key"]
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é um assistente que faz resumo detalhados e separa em tópicos."},
            {"role": "user", "content": f"Por favor, resuma os principais pontos do seguinte transcript: {transcript}"}
        ],
        temperature=0.7,
    )
    if response.choices:
        summary = response.choices[0].message['content']
        return summary
    else:
        return "Não foi possível gerar um resumo."

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
                transcript = get_youtube_transcript(video_id, lang='pt')

            if transcript:
                st.subheader("Transcript:")
                st.write(transcript)

                with st.spinner("Gerando o resumo..."):
                    summary = summarize_transcript(transcript)

                st.subheader("Resumo:")
                st.write(summary)
            else:
                st.error("Não foi possível obter o transcript do vídeo.")
        else:
            st.error("Por favor, insira um link válido do YouTube.")


if __name__ == "__main__":
    main()
