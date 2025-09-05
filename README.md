# Earley Parser in Python

This project implements the **Earley parsing algorithm** for natural language processing.  
It can parse sentences according to a given **context-free grammar (CFG)**, detect whether a parse exists, and display the resulting **parse tree**.

---

## 📖 What is the Earley Parser?

The **Earley Parser** is a type of chart parser for context-free grammars.  
It is efficient and works with:
- Left-recursive grammars  
- Ambiguous grammars  
- Any context-free grammar  

The parser uses three main operations:
1. **Predictor** – expands non-terminals based on grammar rules.  
2. **Scanner** – matches terminals against input words.  
3. **Completer** – completes states and links back to previous rules.  

---

## 🛠️ Features

- Parses sentences using a CFG grammar file.  
- Handles ambiguous and recursive grammars.  
- Displays parse results using **NLTK's `Tree`**.  
- Option to **pretty-print** or **draw** the parse tree.  

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/earley-parser.git
cd earley-parser
