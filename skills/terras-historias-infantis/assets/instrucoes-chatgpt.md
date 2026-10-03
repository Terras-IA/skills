# Usar o ChatGPT como ilustrador (modo assistido)

A skill roda no ZCode; o ChatGPT entra como **gerador das artes** no estilo 3D.
Fluxo completo:

1. **ZCode:** peça o livro em modo assistido → a skill gera `roteiro.md` (com a ficha de
   personagens) e `prompts-imagem.md` (um prompt pronto por página).
2. **ChatGPT:** abra UMA conversa nova e cole os prompts na ordem, um por vez, sempre na
   **mesma conversa** — o ChatGPT reutiliza o personagem da imagem anterior, e é isso que
   mantém a consistência. Se o personagem vier diferente, responda:
   "mantenha exatamente o mesmo personagem da imagem anterior" e gere de novo.
   Tamanho: retrato / 1024×1536 (2:3).
3. **Salvar:** baixe cada imagem na pasta do livro, em `imagens/`, com o nome exato
   indicado no `prompts-imagem.md` (ex.: `imagens/capa.png`, `imagens/pagina-01.png`).
4. **ZCode:** peça "monte o livro com as imagens" → as páginas HTML passam a usar cada
   PNG como fundo, com narração, balões e versículo sobrepostos, e o `livro.pdf` é gerado.

## Bloco de instruções para colar no ChatGPT (início da conversa)

```
Você é o ilustrador dos meus livros ilustrados cristãos infantis. Regras fixas:
- Estilo: ilustração 3D de filme de animação, cores quentes e suaves, luz aconchegante,
  expressões infantis claras e carinhosas.
- Formato: vertical 1024×1536 (2:3).
- NUNCA escreva texto, letras ou balões na imagem (o texto é adicionado depois), exceto
  quando eu disser explicitamente "capa com título".
- Mantenha EXATAMENTE o mesmo personagem entre as imagens: mesmo rosto, mesmo penteado,
  mesma cor de cabelo, mesma roupa e acessórios.
- Temas bíblicos com reverência e delicadeza; nada assustador.
Eu vou enviar a cena de cada página, sempre repetindo a ficha do personagem. Confirme e gere.
```

## Por que o texto não vai nas imagens do ChatGPT

Balões e narração são sobrepostos aqui, em HTML — garante português perfeito, fonte do
livro e ajuste de layout. Imagem do ChatGPT = só a arte.
