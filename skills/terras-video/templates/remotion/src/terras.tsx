// Contrato com o build.py da terras-video.
//
// O build.py manda em `props._terras` o canvas, os 60fps, a duracao do bloco
// (fala + respiro, ou a duracao pedida no roteiro), as cores e a fonte do tema e,
// no vertical, a faixa segura do player. A composicao so desenha: narracao, fades
// e montagem continuam no build.py.
import React, {useEffect, useState} from 'react';
import {CalculateMetadataFunction, continueRender, delayRender, staticFile} from 'remotion';

export type Terras = {
  width: number;
  height: number;
  fps: number;
  duracao: number;
  cores: Record<string, string>;
  fonte: {nome: string; arquivos: string[]};
  seguro?: {topo: number; base: number} | null;
};

export type ComTerras = {_terras?: Terras};

// Valores do Studio, quando a composicao abre sem o build.py (tema youtube, Short).
export const TERRAS_PADRAO: Terras = {
  width: 1080,
  height: 1920,
  fps: 60,
  duracao: 6,
  cores: {base: '#020617', texto: '#f8fafc', texto_apoio: '#cad5e2', acento: '#22d3ee', linha: '#1e293b'},
  fonte: {nome: 'Inter', arquivos: []},
  seguro: {topo: 294, base: 1336},
};

// `any` de proposito: a mesma funcao serve a todas as composicoes, cada uma com props
// proprias, e so le `_terras`.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const metadados: CalculateMetadataFunction<any> = ({props}) => {
  const t = {...TERRAS_PADRAO, ...(props as ComTerras)._terras};
  return {
    width: t.width,
    height: t.height,
    fps: t.fps,
    durationInFrames: Math.max(1, Math.round(t.duracao * t.fps)),
  };
};

export const useTerras = (props: ComTerras): Terras => ({...TERRAS_PADRAO, ...props._terras});

// Carrega a fonte do tema (copiada pelo build.py para public/fonts) antes do
// primeiro quadro: sem isso o Chrome desenha o fallback nos quadros iniciais.
export const useFonte = (t: Terras): string => {
  const [handle] = useState(() => (t.fonte.arquivos.length ? delayRender('fonte do tema') : null));
  useEffect(() => {
    if (handle === null) return;
    Promise.all(
      t.fonte.arquivos.map((a) =>
        new FontFace(t.fonte.nome, `url(${staticFile('fonts/' + a)})`, {weight: '100 900'})
          .load()
          .then((f) => document.fonts.add(f)),
      ),
    )
      .catch((e) => console.error('fonte nao carregou', e))
      .finally(() => continueRender(handle));
  }, [handle, t.fonte]);
  const reserva = t.fonte.nome.includes('Mono') ? 'monospace' : 'sans-serif';
  return `'${t.fonte.nome}', ${reserva}`;
};

// Area onde o conteudo pode viver: a faixa segura no vertical, margem simples no resto.
export const Palco: React.FC<{t: Terras; children: React.ReactNode}> = ({t, children}) => {
  const margem = Math.round(Math.min(t.width, t.height) * 0.09);
  const topo = t.seguro ? t.seguro.topo : margem;
  const base = t.seguro ? t.height - t.seguro.base : margem;
  return (
    <div
      style={{
        position: 'absolute',
        left: margem,
        right: margem,
        top: topo,
        bottom: base,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      {children}
    </div>
  );
};
