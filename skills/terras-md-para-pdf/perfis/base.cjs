// Base comum dos perfis do md-to-pdf. Extensão .cjs porque o repositório é
// "type": "module" e o md-to-pdf carrega a config com require().
const fs = require("fs");
const path = require("path");

// Usa um Chrome/Chromium já instalado quando houver, para o npx não baixar
// outro navegador. PUPPETEER_EXECUTABLE_PATH, se definido, tem prioridade.
const CANDIDATOS = [
  process.env.PUPPETEER_EXECUTABLE_PATH,
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "/usr/bin/chromium",
  "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
].filter(Boolean);
const navegador = CANDIDATOS.find((p) => fs.existsSync(p));

module.exports = function perfil(css, margem) {
  return {
    stylesheet: [path.join(__dirname, css)],
    pdf_options: {
      format: "A4",
      margin: margem,
      printBackground: true,
      outline: true, // marcadores na barra lateral do PDF, a partir dos títulos
      tagged: true, // PDF com estrutura, melhor para leitor de tela e ATS
    },
    ...(navegador ? { launch_options: { executablePath: navegador } } : {}),
  };
};
