import { StyleSheet, type ImageSourcePropType } from 'react-native';
import Svg, { ClipPath, Defs, LinearGradient, Path, Rect, Stop, Image as SvgImage } from 'react-native-svg';

import { colors } from '@/theme';
import { toSvgHref } from '@/utils/image';

type Props = {
  id: string;
  source: ImageSourcePropType;
  width: number;
  height: number;
  buildPath: (w: number, h: number) => string;
  align?: string;
  /** Fades the right side into the page background. */
  wash?: boolean;
};

export function WaveImage({ id, source, width, height, buildPath, align = 'xMidYMid slice', wash }: Props) {
  const clip = `url(#${id}-clip)`;
  return (
    <Svg width={width} height={height} style={StyleSheet.absoluteFill}>
      <Defs>
        <ClipPath id={`${id}-clip`}>
          <Path d={buildPath(width, height)} />
        </ClipPath>
        <LinearGradient id={`${id}-wash`} x1="0.35" y1="0" x2="1" y2="0">
          <Stop offset="0" stopColor={colors.background} stopOpacity="0" />
          <Stop offset="1" stopColor={colors.background} stopOpacity="0.75" />
        </LinearGradient>
      </Defs>
      <SvgImage href={toSvgHref(source)} x={0} y={0} width={width} height={height} preserveAspectRatio={align} clipPath={clip} />
      {wash ? <Rect x={0} y={0} width={width} height={height} fill={`url(#${id}-wash)`} clipPath={clip} /> : null}
    </Svg>
  );
}
