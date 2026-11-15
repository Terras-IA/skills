// Numero grande que conta de 0 ate o valor, com rotulo e barra de progresso.
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {ComTerras, Palco, useFonte, useTerras} from './terras';

export type NumeroProps = ComTerras & {
  valor: number;
  prefixo?: string;
  sufixo?: string;
  rotulo: string;
  apoio?: string;
  casas?: number;
};

export const Numero: React.FC<NumeroProps> = (props) => {
  const t = useTerras(props);
  const familia = useFonte(t);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const u = Math.min(t.width, t.height) / 100;

  const conta = interpolate(frame, [0.2 * fps, 1.8 * fps], [0, props.valor], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const entrada = spring({frame, fps, config: {damping: 200}});
  const rotulo = spring({frame: frame - 0.9 * fps, fps, config: {damping: 200}});
  const casas = props.casas ?? 0;
  const texto = conta.toLocaleString('pt-BR', {minimumFractionDigits: casas, maximumFractionDigits: casas});

  return (
    <AbsoluteFill style={{backgroundColor: t.cores.base, fontFamily: familia, color: t.cores.texto}}>
      <Palco t={t}>
        <div
          style={{
            fontSize: 26 * u,
            fontWeight: 800,
            lineHeight: 1,
            letterSpacing: -0.5 * u,
            color: t.cores.acento,
            opacity: entrada,
            transform: `translateY(${(1 - entrada) * 4 * u}px)`,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {props.prefixo ?? ''}
          {texto}
          {props.sufixo ?? ''}
        </div>
        <div
          style={{
            height: 1.2 * u,
            marginTop: 4 * u,
            background: t.cores.linha ?? '#1e293b',
            borderRadius: u,
            overflow: 'hidden',
          }}
        >
          <div style={{height: '100%', width: `${(conta / (props.valor || 1)) * 100}%`, background: t.cores.acento}} />
        </div>
        <div
          style={{
            marginTop: 5 * u,
            fontSize: 7 * u,
            fontWeight: 700,
            lineHeight: 1.15,
            opacity: rotulo,
            transform: `translateY(${(1 - rotulo) * 3 * u}px)`,
          }}
        >
          {props.rotulo}
        </div>
        {props.apoio ? (
          <div style={{marginTop: 3 * u, fontSize: 4.4 * u, lineHeight: 1.35, color: t.cores.texto_apoio, opacity: rotulo}}>
            {props.apoio}
          </div>
        ) : null}
      </Palco>
    </AbsoluteFill>
  );
};
