import { useState } from 'react';

import { routes } from '@/constants/routes';
import { useRouter } from 'expo-router';

export type PropertyValues = { name: string; address: string; city: string; state: string; pincode: string };

const INITIAL: PropertyValues = { name: '', address: '', city: '', state: '', pincode: '' };

export function usePropertyForm() {
  const router = useRouter();
  const [values, setValues] = useState<PropertyValues>(INITIAL);
  const [touched, setTouched] = useState(false);
  const error = touched && !values.name.trim() ? 'Property name is required' : undefined;

  const setField = (field: keyof PropertyValues, value: string) => setValues((previous) => ({ ...previous, [field]: value }));
  const detectLocation = () => setValues((previous) => ({ ...previous, address: '123 Park Street', city: 'Kolkata', state: 'West Bengal', pincode: '700016' }));
  const submit = () => {
    setTouched(true);
    if (!values.name.trim()) return;
    router.push({ pathname: routes.confirmLocation, params: values });
  };

  return { values, error, setField, detectLocation, submit };
}
