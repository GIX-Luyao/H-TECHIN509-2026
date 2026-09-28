"""Week 7: example tests for the ChatBot class (runs offline via FakeLLM)."""

from ribot.chatbot import ChatBot, ConversationLogger


def test_history_starts_with_system_message():
    bot = ChatBot(system_prompt="You are a test bot.")
    assert bot.history[0] == {"role": "system", "content": "You are a test bot."}


def test_add_turn_appends_to_history():
    bot = ChatBot()
    before = len(bot.history)
    bot.add_turn("user", "hi")
    assert len(bot.history) == before + 1
    assert bot.history[-1] == {"role": "user", "content": "hi"}


def test_reply_records_user_and_assistant():
    bot = ChatBot()
    answer = bot.reply("hello")
    assert isinstance(answer, str) and answer
    assert bot.history[-2]["role"] == "user"
    assert bot.history[-1]["role"] == "assistant"


def test_reset_keeps_only_system():
    bot = ChatBot()
    bot.reply("hello")
    bot.reset()
    assert len(bot.history) == 1


def test_logger_records_turns():
    logger = ConversationLogger()
    logger.log("user", "hi")
    assert logger.turns == [{"role": "user", "content": "hi"}]


def test_memory_recalls_name_when_history_is_kept():
    # The Week 1/3 memory demo: with history kept, the bot recalls your name.
    bot = ChatBot()
    bot.reply("My name is Sam.")
    answer = bot.reply("What's my name?")
    assert "Sam" in answer


def _tiny_retriever():
    # A two-chunk index, built the same way Week 6's build_index does it.
    from ribot.embeddings import fallback_embed
    from ribot.retriever import Retriever
    from ribot.vectorstore import InMemoryStore

    store = InMemoryStore()
    chunks = [
        "Vacation policy: full-time employees receive 15 vacation days per year.",
        "To reset your password, open the IT portal and choose 'Forgot password'.",
    ]
    store.add(
        ids=["policy.md:0", "it_faq.md:0"],
        documents=chunks,
        embeddings=[fallback_embed(c) for c in chunks],
    )
    return Retriever(store, embed_fn=fallback_embed)


def test_reply_grounded_cites_a_source():
    # Week 7 floor: the grounded reply must carry a [source: ...] citation.
    bot = ChatBot()
    answer = bot.reply_grounded("How many vacation days do employees get?", _tiny_retriever())
    assert "[source:" in answer


def test_reply_grounded_refuses_on_empty_index():
    # No documents indexed -> the honest answer is "I don't know", not an invention.
    from ribot.embeddings import fallback_embed
    from ribot.retriever import Retriever
    from ribot.vectorstore import InMemoryStore

    bot = ChatBot()
    empty = Retriever(InMemoryStore(), embed_fn=fallback_embed)
    answer = bot.reply_grounded("What is the vacation policy?", empty)
    assert "don't know" in answer.lower()


def test_memory_forgets_without_history():
    # The "goldfish" case: if earlier turns are NOT in messages, the bot can't know.
    from ribot.llm import chat

    answer = chat(
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is my name?"},
        ]
    )
    assert "don't know" in answer.lower()
