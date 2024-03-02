PARTS_OF_SPEECH = sorted(
    ["VB", "NNS", "JJ", "V.*?", "VBG", "VBN", "VBD", "VBZ", "VBP", "NN", "NN:U", "NN:UN", "NNP", "PRP.*", "PRP", "PRP$", "N.*?", "JJ.*?", "IN", "CC", "DT", "EX", "LS", "MD", "POS", "RB", "RBR", "RBS", "UH", "WP", "WP$", "WRB"],
    key=len,
    reverse=True
)