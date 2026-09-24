import { useLocalSearchParams, useRouter } from 'expo-router';

import { routes } from '@/constants/routes';
import { CompletionScreen } from '../components/completion-screen';

export function PropertyAddedScreen() {
  const router = useRouter();
  const { propertyName = 'Your property' } = useLocalSearchParams<{ propertyName?: string }>();
  return <CompletionScreen title="Property Added!" body={`${propertyName} has been successfully added. You can now start managing your spaces.`} buttonTitle="Go to Dashboard" icon="business-outline" onBack={() => router.replace(routes.confirmLocation)} onContinue={() => router.replace(routes.home)} />;
}
