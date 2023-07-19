TOPIC_SENTENCE_SYSTEM_PROMPT="""Ask yourself the question: Does the topic sentence in the passage clarify to the reader why the paragraph provides a concrete reason to do what the writer wants?

If yes: just respond with "no changes"

If no: Rewrite the following passages, focusing on the topic sentence, to ensure it clearly describes its content while maintaining the author's original intent and whether or not the paragraph gives a concrete reason to justify the author's point of view
"""

QUOTATION_SYSTEM_PROMPT = """Identify if the passage has quotations introduced with fluffy lean-ins and replace them with substantive ones"""