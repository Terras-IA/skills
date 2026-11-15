// Semaforo de niveis: as luzes acendem em sequencia, acompanhando a fala que
// nomeia cada nivel. `momentos` diz em que fracao do bloco cada luz acende; sem
// ele, as luzes se espalham por igual entre 15% e 75% da duracao.
import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {ComTerras, Palco, useFonte, useTerras} from './terras';

export type SemaforoProps = ComTerras & {
  titulo?: string;
  niveis: {nome: string; cor: string; rotulo: string}[];
  momentos?: number[];
};

export const Semaforo: React.FC<SemaforoProps> = (props) => {
  const t = useTerras(props);
  const familia = useFonte(t);
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const u = Math.min(t.width, t.height) / 100;
  const deitado = t.width > t.height;
  const n = props.niveis.length;
  const momentos =
    props.momentos ?? props.niveis.map((_, i) => 0.15 + (n > 1 ? (0.6 * i) / (n - 1) : 0));
  const titulo = spring({frame, fps, config: {damping: 200}});

  return (
    <AbsoluteFill style={{backgroundColor: t.cores.base, fontFamily: familia, color: t.cores.texto}}>
      <Palco t={t}>
        {props.titulo ? (
          <div style={{fontSize: 7 * u, fontWeight: 800, lineHeight: 1.1, marginBottom: 7 * u, opacity: titulo}}>
            {props.titulo}
          </div>
        ) : null}
        <div style={{display: 'flex', flexDirection: deitado ? 'row' : 'column', gap: 5 * u}}>
          {props.niveis.map((nv, i) => {
            const inicio = momentos[i] * durationInFrames;
            const acende = spring({frame: frame - inicio, fps, config: {damping: 14, mass: 0.6}});
            // a luz da vez brilha mais; as anteriores ficam acesas, mas em repouso
            const proxima = i + 1 < n ? momentos[i + 1] * durationInFrames : Infinity;
            const vez = frame >= inicio && frame < proxima ? 1 : 0.55;
            const brilho = interpolate(acende, [0, 1], [0.12, vez], {extrapolateRight: 'clamp'});
            return (
              <div
                key={nv.nome}
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: deitado ? 'column' : 'row',
                  alignItems: deitado ? 'flex-start' : 'center',
                  gap: 4 * u,
                  padding: 4 * u,
                  borderRadius: 3 * u,
                  border: `${0.3 * u}px solid ${t.cores.linha ?? '#1e293b'}`,
                  background: `rgba(255,255,255,${0.02 + 0.03 * acende})`,
                }}
              >
                <div
                  style={{
                    width: 14 * u,
                    height: 14 * u,
                    flexShrink: 0,
                    borderRadius: '50%',
                    background: nv.cor,
                    opacity: brilho,
                    boxShadow: `0 0 ${8 * u * brilho}px ${2 * u * brilho}px ${nv.cor}`,
                    transform: `scale(${0.85 + 0.15 * acende})`,
                  }}
                />
                <div>
                  <div style={{fontSize: 6 * u, fontWeight: 800, letterSpacing: 0.3 * u, color: nv.cor, opacity: 0.25 + 0.75 * acende}}>
                    {nv.nome}
                  </div>
                  <div style={{fontSize: 3.8 * u, lineHeight: 1.3, marginTop: 1.2 * u, color: t.cores.texto_apoio, opacity: 0.2 + 0.8 * acende}}>
                    {nv.rotulo}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Palco>
    </AbsoluteFill>
  );
};
