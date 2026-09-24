import { Image, View } from 'react-native';

import { AppText } from '@/components/ui';
import { images } from '@/constants/assets';
import { useResponsive } from '@/hooks/use-responsive';
import { colors } from '@/theme';
import { getAspectRatio } from '@/utils/image';
import { verifyFooterPath } from '../utils/footer-paths';
import { WaveImage } from './wave-image';

export function VerifyFooter() {
  const { width } = useResponsive();
  const height = Math.round(width * 0.62);

  return (
    <View style={{ width, height }} pointerEvents="none">
      <WaveImage id="verify" source={images.auth.roomSoft} width={width} height={height} buildPath={verifyFooterPath} />
      <Image
        source={images.auth.plantBottom}
        resizeMode="contain"
        style={{ position: 'absolute', left: 0, bottom: 0, width: width * 0.38, aspectRatio: getAspectRatio(images.auth.plantBottom, 0.57) }}
      />
      <View style={{ position: 'absolute', right: width * 0.13, top: height * 0.39, transform: [{ rotate: '-6deg' }] }}>
        <AppText variant="script" color={colors.primary} style={{ textAlign: 'right' }}>
          {'Small steps.\nCleaner tomorrow.'}
        </AppText>
        <View style={{ width: 34, height: 2, marginTop: 4, marginLeft: 40, backgroundColor: colors.secondary }} />
      </View>
    </View>
  );
}
