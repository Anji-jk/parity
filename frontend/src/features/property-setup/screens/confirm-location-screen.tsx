import { Ionicons } from '@expo/vector-icons';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScrollView, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { AppButton, AppText } from '@/components/ui';
import { routes } from '@/constants/routes';
import { colors, spacing } from '@/theme';
import { MapPreview } from '../components/map-preview';
import { SetupHeader } from '../components/setup-header';

type Params = { propertyName?: string; address?: string; city?: string; state?: string; pincode?: string };

export function ConfirmLocationScreen() {
  const params = useLocalSearchParams<Params>();
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const address = `${params.address || '123 Park Street'}, ${params.city || 'Kolkata'}`;
  const region = `${params.state || 'West Bengal'} ${params.pincode || '700016'}`;

  return (
    <ScrollView contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm }]} showsVerticalScrollIndicator={false}>
      <SetupHeader onBack={() => router.replace(routes.addProperty)} />
      <AppText variant="featureTitle" color={colors.primary} style={styles.heading}>Confirm Location</AppText>
      <MapPreview />
      <View style={styles.address}>
        <Ionicons name="location-outline" size={24} color={colors.primary} />
        <AppText variant="caption" color={colors.textDark} style={styles.addressText}>{address}{`\n`}{region}</AppText>
      </View>
      <AppButton title="Confirm Location" onPress={() => router.replace({ pathname: routes.propertyAdded, params: { propertyName: params.propertyName || 'The Haven Hotel' } })} trailingIcon={<Ionicons name="arrow-forward" size={22} color={colors.white} />} style={styles.button} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { flexGrow: 1, paddingHorizontal: spacing.xl, paddingBottom: spacing.xl, backgroundColor: colors.background },
  heading: { marginBottom: 12 },
  address: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, marginTop: 16, paddingHorizontal: 4 },
  addressText: { flex: 1, lineHeight: 19 },
  button: { marginTop: 20 },
});
