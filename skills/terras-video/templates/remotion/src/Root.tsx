// Composicoes disponiveis para o bloco `remotion` do roteiro. Para criar uma nova:
// componente que recebe ComTerras + props proprias, registrado aqui com
// `calculateMetadata={metadados}`. O id e o que o roteiro pede em `composicao`.
import React from 'react';
import {Composition} from 'remotion';
import {metadados} from './terras';
import {Numero, NumeroProps} from './Numero';
import {Barras, BarrasProps} from './Barras';
import {Legenda, LegendaProps} from './Legenda';

const base = {durationInFrames: 360, fps: 60, width: 1080, height: 1920, calculateMetadata: metadados};

export const Root: React.FC = () => (
  <>
    <Composition<any, NumeroProps>
      id="Numero"
      component={Numero}
      {...base}
      defaultProps={{valor: 1250, sufixo: '%', rotulo: 'de crescimento no trimestre', apoio: 'Comparado ao mesmo periodo do ano passado.'}}
    />
    <Composition<any, BarrasProps>
      id="Barras"
      component={Barras}
      {...base}
      defaultProps={{
        titulo: 'Tempo de resposta',
        sufixo: ' ms',
        itens: [
          {rotulo: 'Antes', valor: 820},
          {rotulo: 'Com cache', valor: 310},
          {rotulo: 'Com fila', valor: 140, destaque: true},
        ],
      }}
    />
    <Composition<any, LegendaProps>
      id="Legenda"
      component={Legenda}
      {...base}
      defaultProps={{texto: 'O video que se monta sozinho, com uma aprovacao no meio.', destaques: ['sozinho', 'aprovacao']}}
    />
  </>
);
