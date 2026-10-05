#!/usr/bin/env node
// Publica texto e/ou imagem no canal (newsletter) do WhatsApp, pela sessão
// Baileys já pareada do sidecar do projeto.
//
// Só envia com --yes; sem ele, apenas confere (--checar) e mostra a prévia.
// A sessão (.auth) é CREDENCIAL: este script só a lê; nunca copie nem versione.
//
// Uso:
//   node publicar.mjs --checar
//   node publicar.mjs --texto post.md --imagem card.png --checar
//   node publicar.mjs --texto post.md --imagem card.png --yes
//
// Config: ~/.config/terras-canal-whatsapp/config.json
//   { "canal": "<id>@newsletter", "sidecar": "<pasta do sidecar>" }
// Overrides: TERRAS_CANAL_WHATSAPP_CONFIG, TERRAS_WHATSAPP_CANAL,
//            TERRAS_WHATSAPP_SIDECAR. Saída: linhas próprias em stdout; ruído
//            conhecido do libsignal é filtrado (o resto é inofensivo).
// Códigos de saída: 0 ok · 1 falha · 2 uso/config · 3 sem permissão no canal.

import { existsSync, readFileSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const LIMITE_LEGENDA = 1024;
const LIMITE_IMAGEM = 16 * 1024 * 1024;
const TIMEOUT_PADRAO = 90000;

// ---- argumentos ------------------------------------------------------------
const args = process.argv.slice(2);
const temFlag = (f) => args.includes(f);
const valor = (f, fallback) => {
  const i = args.indexOf(f);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const checar = temFlag("--checar");
const publicar = temFlag("--yes");
const arquivoTexto = valor("--texto");
const arquivoImagem = valor("--imagem");
const timeoutMs = Number(valor("--timeout", TIMEOUT_PADRAO));

if (checar && publicar) {
  console.error("escolha um: --checar (conferir, não envia) ou --yes (publicar).");
  process.exit(2);
}
if (!checar && !publicar) {
  console.error("nada foi enviado: use --checar para conferir ou --yes para publicar.");
  process.exit(2);
}
if (publicar && !arquivoTexto && !arquivoImagem) {
  console.error("--yes precisa de --texto e/ou --imagem.");
  process.exit(2);
}

// ---- config ----------------------------------------------------------------
const caminhoConfig = valor(
  "--config",
  process.env.TERRAS_CANAL_WHATSAPP_CONFIG ??
    join(homedir(), ".config", "terras-canal-whatsapp", "config.json")
);
if (!existsSync(caminhoConfig)) {
  console.error(`sem config em ${caminhoConfig}: copie scripts/config.example.json e preencha.`);
  process.exit(2);
}
let config;
try {
  config = JSON.parse(readFileSync(caminhoConfig, "utf8"));
} catch (e) {
  console.error(`config inválida: ${e.message}`);
  process.exit(2);
}
const canal = process.env.TERRAS_WHATSAPP_CANAL ?? config.canal;
const sidecar = process.env.TERRAS_WHATSAPP_SIDECAR ?? config.sidecar;
if (typeof canal !== "string" || !canal.endsWith("@newsletter")) {
  console.error("config sem 'canal': esperado um JID terminado em @newsletter.");
  process.exit(2);
}
if (typeof sidecar !== "string" || !existsSync(join(sidecar, "node_modules"))) {
  console.error(`sidecar inválido ("${sidecar}"): rode npm install na pasta do sidecar do projeto.`);
  process.exit(2);
}
const authDir = join(sidecar, ".auth");
if (!existsSync(join(authDir, "creds.json"))) {
  console.error(`sem sessão em ${authDir}: pareie o sidecar primeiro (veja references/pareamento-e-problemas.md).`);
  process.exit(2);
}

// ---- conteúdo --------------------------------------------------------------
let texto = "";
if (arquivoTexto) {
  if (!existsSync(arquivoTexto)) {
    console.error(`texto não existe: ${arquivoTexto}`);
    process.exit(2);
  }
  texto = readFileSync(arquivoTexto, "utf8").replace(/\r\n/g, "\n").trimEnd();
}
if (arquivoImagem) {
  if (!existsSync(arquivoImagem)) {
    console.error(`imagem não existe: ${arquivoImagem}`);
    process.exit(2);
  }
  if (!/\.(png|jpe?g|webp)$/i.test(arquivoImagem)) {
    console.error("imagem: use png, jpg/jpeg ou webp.");
    process.exit(2);
  }
  if (statSync(arquivoImagem).size > LIMITE_IMAGEM) {
    console.error("imagem acima de 16 MB: reduza antes de publicar.");
    process.exit(2);
  }
  if (texto.length > LIMITE_LEGENDA) {
    console.error(`legenda com ${texto.length} caracteres (limite ${LIMITE_LEGENDA} com imagem). Encurte ou publique sem imagem.`);
    process.exit(2);
  }
}

// ---- Baileys (de dentro do sidecar) ----------------------------------------
const req = createRequire(join(sidecar, "package.json"));
let caminhoBaileys;
try {
  caminhoBaileys = req.resolve("@whiskeysockets/baileys");
} catch {
  console.error("Baileys não encontrado no sidecar: rode npm install na pasta dele.");
  process.exit(2);
}
// Filtra o ruído conhecido do libsignal (dumps de sessão) nas saídas de console.
// O patch vem ANTES do import: a lib loga por console.info/log em tempo de uso,
// e o dump de sessão (session_record.js) sai por console.info.
const RUÍDO =
  /Bad MAC|Failed to decrypt|Closing (open )?session|SessionEntry|_chains|chainKey|chainType|currentRatchet|registrationId|ephemeralKeyPair|messageKeys|pubKey|privKey|indexInfo|baseKey|lastRemoteEphemeralKey|previousCounter|remoteIdentityKey|rootKey|sessionVersion|pendingPreKey|^\s*[{}[\]]+,?\s*$/;
for (const m of ["log", "error", "warn", "info", "debug"]) {
  const original = console[m].bind(console);
  console[m] = (...a) => {
    if (!RUÍDO.test(String(a[0] ?? ""))) original(...a);
  };
}

const baileys = await import(pathToFileURL(caminhoBaileys).href);
const { default: makeWASocket, useMultiFileAuthState } = baileys;

const loggerSilencioso = () => {
  const n = () => {};
  return { level: "silent", child: () => loggerSilencioso(), trace: n, debug: n, info: n, warn: n, error: n, fatal: n };
};

const { state, saveCreds } = await useMultiFileAuthState(authDir);
const sock = makeWASocket({ auth: state, logger: loggerSilencioso(), markOnlineOnConnect: false, printQRInTerminal: false });
sock.ev.on("creds.update", saveCreds);

let encerrado = false;
const encerrar = (codigo) => {
  if (encerrado) return;
  encerrado = true;
  setTimeout(() => process.exit(codigo), 300);
};
const relogio = setTimeout(() => {
  console.error(`tempo esgotado (${timeoutMs}ms) sem concluir: a sessão pode ter caído (repareie) ou a conexão travou.`);
  encerrar(1);
}, timeoutMs);

sock.ev.on("connection.update", async (u) => {
  const { connection, lastDisconnect, qr } = u;
  if (qr) {
    console.error("(o servidor pediu QR: a sessão não está mais valendo, repareie o sidecar)");
  }
  if (connection === "open") {
    clearTimeout(relogio);
    try {
      const meta = await sock.newsletterMetadata("jid", canal);
      const papel = meta?.viewer_metadata?.role;
      const nome = meta?.thread_metadata?.name?.text ?? "(sem nome)";
      if (papel !== "OWNER" && papel !== "ADMIN") {
        console.error(`papel "${papel ?? "desconhecido"}" no canal "${nome}": sem permissão para postar.`);
        encerrar(3);
        return;
      }
      console.log(`canal: ${nome} (${canal}) · papel: ${papel}`);
      if (!texto && !arquivoImagem) {
        console.log("--checar: canal pronto para postar (nenhum conteúdo informado).");
        encerrar(0);
        return;
      }
      console.log(
        `conteúdo: ${arquivoTexto ? `texto com ${texto.length} chars` : "sem texto"}` +
          `${arquivoImagem ? ` · imagem ${arquivoImagem} (${statSync(arquivoImagem).size} bytes)` : ""}`
      );
      if (checar) {
        if (texto) {
          const previa = texto.length > 600 ? `${texto.slice(0, 600)}\n[...]` : texto;
          console.log(`--- prévia ---\n${previa}`);
        }
        console.log("--checar: nada foi enviado.");
        encerrar(0);
        return;
      }
      const conteudo = arquivoImagem
        ? { image: readFileSync(arquivoImagem), caption: texto || undefined }
        : { text: texto };
      const enviada = await sock.sendMessage(canal, conteudo);
      console.log(`publicado — id ${enviada?.key?.id ?? "(sem id)"}`);
      encerrar(0);
    } catch (e) {
      console.error(`falha: ${e?.message ?? e}`);
      encerrar(1);
    }
  }
  if (connection === "close") {
    if (encerrado) return;
    const status = lastDisconnect?.error?.output?.statusCode;
    console.error(
      status === 401
        ? "sessão caiu (aparelho deslogado): repareie o sidecar."
        : `conexão fechou antes de concluir (status ${status ?? "?"}).`
    );
    encerrar(1);
  }
});
