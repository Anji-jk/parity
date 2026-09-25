import { StyleSheet, View } from 'react-native';

import { AppIcon, AppText } from '@/components/ui';
import { colors, fontFamily } from '@/theme';
import type { DashboardSummary } from '../types/dashboard-types';

type Props = { item: DashboardSummary };

export function SummaryCard({ item }: Props) {
  const tone = item.tone === 'green' ? colors.primary : item.tone === 'amber' ? colors.secondary : colors.textSecondary;

  return (
    <View style={[styles.card, item.tone === 'green' && styles.selected]}>
      <AppIcon icon={item.icon} size={31} color={tone} />
      <View style={styles.copy}>
        <AppText style={styles.value} color={colors.textDark}>{item.value}</AppText>
        <AppText style={styles.label} color={tone}>{item.label}</AppText>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { flex: 1, minHeight: 94, paddingHorizontal: 11, paddingVertical: 14, borderRadius: 15, borderWidth: 1, borderColor: '#E3E7E3', backgroundColor: 'rgba(255,255,255,0.64)', justifyContent: 'center', gap: 7 },
  selected: { borderColor: '#B5CCB8', backgroundColor: '#F1F7F0' },
  copy: { gap: 1 },
  value: { fontFamily: fontFamily.semiBold, fontSize: 22, lineHeight: 26 },
  label: { fontFamily: fontFamily.regular, fontSize: 12, lineHeight: 17 },
});
