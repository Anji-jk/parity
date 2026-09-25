import { Ionicons } from '@expo/vector-icons';
import { Image, Pressable, StyleSheet, View } from 'react-native';

import { AppText } from '@/components/ui';
import { images } from '@/constants/assets';
import { colors, fontFamily } from '@/theme';

export function DashboardHeader() {
  return (
    <View style={styles.header}>
      <Image source={images.brand.logoWordmark} style={styles.logo} resizeMode="contain" />
      <View style={styles.actions}>
        <Pressable style={styles.notification} accessibilityRole="button" accessibilityLabel="Notifications">
          <Ionicons name="notifications-outline" size={25} color={colors.primary} />
          <View style={styles.notificationDot} />
        </Pressable>
        <View style={styles.avatar}>
          <TextInitials />
        </View>
      </View>
    </View>
  );
}

function TextInitials() {
  return <AppText style={styles.initials} color={colors.primary}>AK</AppText>;
}

const styles = StyleSheet.create({
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  logo: { width: 184, height: 58, alignSelf: 'flex-start' },
  actions: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  notification: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.inputBorder,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.white,
  },
  notificationDot: { position: 'absolute', top: 8, right: 7, width: 11, height: 11, borderRadius: 6, backgroundColor: '#F21E2B' },
  avatar: { width: 48, height: 48, borderRadius: 24, backgroundColor: '#E9F0E9', alignItems: 'center', justifyContent: 'center' },
  initials: { fontFamily: fontFamily.semiBold, fontSize: 16, color: colors.primary },
});
