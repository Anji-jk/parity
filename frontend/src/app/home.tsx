import { View } from 'react-native';

import { AppText } from '@/components/ui';
import { colors } from '@/theme';

export default function Home() {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.background }}>
      <AppText variant="title">Home</AppText>
    </View>
  );
}
