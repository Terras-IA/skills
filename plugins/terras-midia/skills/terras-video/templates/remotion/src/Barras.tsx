// Grafico de barras horizontais que crescem uma depois da outra.
import React from 'react';
import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {ComTerras, Palco, useFonte, useTerras} from './terras';

export type BarrasProps = ComTerras & {
  titulo: string;
  itens: {rotulo: string; valor: number; destaque?: boolean}[];
  sufixo?: string;
};

export const Barras: React.FC<BarrasProps> = (props) => {
  const t = useTerras(props);
  const familia = useFonte(t);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const u = Math.min(t.width, t.height) / 100;
  const maximo = Math.max(...props.itens.map((i) => i.valor), 1);
  const titulo = spring({frame, fps, config: {damping: 200}});

  return (
    <AbsoluteFill style={{backgroundColor: t.cores.base, fontFamily: familia, color: t.cores.texto}}>
      <Palco t={t}>
        <div style={{fontSize: 8 * u, fontWeight: 800, lineHeight: 1.1, marginBottom: 6 * u, opacity: titulo}}>
          {props.titulo}
        </div>
        {props.itens.map((item, i) => {
          const p = spring({frame: frame - (0.5 + i * 0.35) * fps, fps, config: {damping: 200}});
          const cor = item.destaque ? t.cores.acento : t.cores.texto_apoio;
          return (
            <div key={item.rotulo} style={{marginBottom: 4.5 * u, opacity: Math.min(1, p * 2)}}>
              <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 4.6 * u, marginBottom: 1.4 * u}}>
                <span style={{fontWeight: item.destaque ? 700 : 500}}>{item.rotulo}</span>
                <span style={{fontWeight: 700, color: cor, fontVariantNumeric: 'tabular-nums'}}>
                  {Math.round(item.valor * p).toLocaleString('pt-BR')}
                  {props.sufixo ?? ''}
                </span>
              </div>
              <div style={{height: 3 * u, background: t.cores.linha ?? '#1e293b', borderRadius: 0.8 * u}}>
                <div
                  style={{
                    height: '100%',
                    width: `${(item.valor / maximo) * 100 * p}%`,
                    background: cor,
                    borderRadius: 0.8 * u,
                  }}
                />
              </div>
            </div>
          );
        })}
      </Palco>
    </AbsoluteFill>
  );
};
