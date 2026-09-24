import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import { colors } from '@/theme';

export function MapPreview() {
  return (
    <View style={styles.map}>
      <View style={[styles.road, styles.roadA]} />
      <View style={[styles.road, styles.roadB]} />
      <View style={[styles.road, styles.roadC]} />
      <View style={styles.water} />
      <View style={styles.marker}><Ionicons name="location" size={34} color={colors.primary} /></View>
      <View style={styles.dot} />
      <View style={styles.locationButton}><Ionicons name="locate-outline" size={22} color={colors.primary} /></View>
    </View>
  );
}

const styles = StyleSheet.create({
  map: { height: 224, overflow: 'hidden', borderRadius: 14, backgroundColor: '#E8E6DF' },
  road: { position: 'absolute', backgroundColor: '#F8F6EF', borderWidth: 1, borderColor: '#D4D7D0', transform: [{ rotate: '35deg' }] },
  roadA: { width: 360, height: 32, left: -70, top: 54 },
  roadB: { width: 390, height: 25, left: -70, top: 145, transform: [{ rotate: '-28deg' }] },
  roadC: { width: 300, height: 19, left: 35, top: 95, transform: [{ rotate: '78deg' }] },
  water: { position: 'absolute', width: 140, height: 300, right: -58, top: -26, backgroundColor: '#DDE8E4', transform: [{ rotate: '24deg' }] },
  marker: { position: 'absolute', left: '50%', top: '42%', marginLeft: -17, marginTop: -25 },
  dot: { position: 'absolute', left: '50%', top: '53%', width: 13, height: 13, marginLeft: -6, borderRadius: 7, backgroundColor: '#2D8BE8', borderWidth: 3, borderColor: '#D9E7F6' },
  locationButton: { position: 'absolute', right: 12, bottom: 12, width: 42, height: 42, borderRadius: 21, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.background },
});
