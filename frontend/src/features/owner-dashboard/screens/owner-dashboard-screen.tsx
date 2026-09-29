import { useRouter } from 'expo-router';
import { Image, ScrollView, StyleSheet, View, useWindowDimensions } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { AppText } from '@/components/ui';
import { routes } from '@/constants/routes';
import { colors, fontFamily, spacing } from '@/theme';
import { AddPropertyButton } from '../components/add-property-button';
import { DashboardHeader } from '../components/dashboard-header';
import { DashboardTabs } from '../components/dashboard-tabs';
import { PropertyCard } from '../components/property-card';
import { SummaryCard } from '../components/summary-card';
import { dashboardSummary, dashboardTabs, properties } from '../constants/dashboard-data';

export function OwnerDashboardScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { width } = useWindowDimensions();
  const compact = width < 390;

  return (
    <View style={styles.root}>
      {/* <Image source={require('@/assets/images/decor/leaves_top.png')} style={styles.topLeaves} resizeMode="contain" /> */}
      <Image source={require('@/assets/images/decor/leaves_bottom.png')} style={styles.bottomLeaves} resizeMode="contain" />
      <ScrollView contentContainerStyle={[styles.scroll, { paddingTop: insets.top + 12, paddingBottom: insets.bottom + 100 }]} showsVerticalScrollIndicator={false}>
        <DashboardHeader />
        <View style={styles.headingBlock}>
          <AppText style={styles.eyebrow} color={colors.textMuted}>OWNER DASHBOARD</AppText>
          <View style={styles.headingRow}>
            <View style={styles.headingCopy}>
              <AppText style={styles.heading} color={colors.primary}>Your Properties</AppText>
              <AppText style={styles.subtitle} color={colors.textSecondary}>Manage and monitor all your properties from one place.</AppText>
            </View>
            <AddPropertyButton compact={compact} onPress={() => router.push(routes.addProperty)} />
          </View>
        </View>
        <View style={styles.summaryRow}>
          {dashboardSummary.map((item) => <SummaryCard key={item.label} item={item} />)}
        </View>
        <View style={styles.properties}>
          {properties.map((property) => <PropertyCard key={property.id} property={property} />)}
        </View>
      </ScrollView>
      <View style={styles.tabs}><DashboardTabs tabs={dashboardTabs} activeLabel="Properties" /></View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  scroll: { paddingHorizontal: spacing.xl, gap: 0 },
  topLeaves: { position: 'absolute', top: 90, right: -32, width: 180, height: 210, opacity: 0.56 },
  bottomLeaves: { position: 'absolute', bottom: 54, right: -14, width: 190, height: 160, opacity: 0.6 },
  headingBlock: { marginTop: 47 },
  eyebrow: { fontFamily: fontFamily.medium, fontSize: 15, lineHeight: 20, letterSpacing: 4 },
  headingRow: { flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 14 },
  headingCopy: { flex: 1 },
  heading: { fontFamily: fontFamily.bold, fontSize: 24, lineHeight: 30, letterSpacing: 0 },
  subtitle: { fontFamily: fontFamily.regular, fontSize: 14, marginTop: 5 },
  summaryRow: { flexDirection: 'row', gap: 13, marginTop: 32 },
  properties: { marginTop: 25 },
  tabs: { position: 'absolute', left: 0, right: 0, bottom: 0 },
});
