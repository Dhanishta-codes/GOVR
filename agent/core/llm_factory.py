from langchain_core.messages import AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
import google.generativeai as genai
import agent.infra.config as config


def get_llm():

    # ---------- ANTHROPIC ----------
    if config.AI_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=config.MODELS["anthropic"],
            api_key=config.ANTHROPIC_API_KEY,
            temperature=config.TEMPERATURE
        )

    # ---------- GOOGLE ----------
    elif config.AI_PROVIDER == "google":

        genai.configure(api_key=config.GOOGLE_API_KEY)
        model_name = config.MODELS.get("google", "gemini-2.5-flash")

        class GeminiWrapper(BaseChatModel):

            @property
            def _llm_type(self):
                return "google-gemini-direct"

            def _generate(self, messages, **kwargs):
                prompt = "\n".join(m.content for m in messages)

                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt, request_options = {"timeout": 60})

                return ChatResult(
                    generations=[
                        ChatGeneration(
                            message=AIMessage(content=response.text)
                        )
                    ]
                )

        return GeminiWrapper()

    # ---------- GROQ ----------
    elif config.AI_PROVIDER == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=config.MODELS["groq"],
            groq_api_key=config.GROQ_API_KEY,
            temperature=config.TEMPERATURE
        )

    else:
        raise ValueError("Invalid AI_PROVIDER")
