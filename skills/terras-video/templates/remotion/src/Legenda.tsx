// Frase que aparece palavra por palavra, espalhada pela duracao do bloco.
// Sem marcacao de tempo da fala, o ritmo e uniforme: cada palavra ganha a mesma
// fatia de tempo, o que acompanha bem uma narracao de ritmo constante.
import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {ComTerras, Palco, useFonte, useTerras} from './terras';

export type LegendaProps = ComTerras & {
  texto: string;
  destaques?: string[];
};

const limpa = (p: string) => p.toLowerCase().replace(/[^\p{L}\p{N}%]/gu, '');

export const Legenda: React.FC<LegendaProps> = (props) => {
  const t = useTerras(props);
  const familia = useFonte(t);
  const frame = useCurrentFrame();
  const u = Math.min(t.width, t.height) / 100;
  const palavras = props.texto.split(/\s+/).filter(Boolean);
  const destaques = new Set((props.destaques ?? []).map(limpa));
  // As palavras entram nos primeiros 85% do bloco; o resto e leitura parada.
  const fatia = (t.duracao * t.fps * 0.85) / Math.max(palavras.length, 1);

  return (
    <AbsoluteFill style={{backgroundColor: t.cores.base, fontFamily: familia, color: t.cores.texto}}>
      <Palco t={t}>
        <div style={{fontSize: 9 * u, fontWeight: 800, lineHeight: 1.18, letterSpacing: -0.15 * u}}>
          {palavras.map((p, i) => {
            const inicio = i * fatia;
            const a = interpolate(frame, [inicio, inicio + 8], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            return (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  marginRight: 2.2 * u,
                  opacity: 0.12 + 0.88 * a,
                  transform: `translateY(${(1 - a) * 1.5 * u}px)`,
                  color: destaques.has(limpa(p)) ? t.cores.acento : undefined,
                }}
              >
                {p}
              </span>
            );
          })}
        </div>
      </Palco>
    </AbsoluteFill>
  );
};
