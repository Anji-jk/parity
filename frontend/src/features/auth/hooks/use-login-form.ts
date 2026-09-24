import { useRouter } from 'expo-router';
import { useMemo, useRef, useState } from 'react';

import { routes } from '@/constants/routes';
import { toApiError } from '@/services/http/api-error';
import { authApi } from '../api/auth-api';
import { DEFAULT_COUNTRY, getCountry } from '../constants/countries';
import type { LoginValues } from '../types/auth-types';
import { digitsOnly, sanitizePhone, toE164 } from '../utils/phone';

const INITIAL: LoginValues = { countryIso: DEFAULT_COUNTRY.iso, phone: '' };

export function useLoginForm() {
  const router = useRouter();
  const [values, setValues] = useState<LoginValues>(INITIAL);
  const [touched, setTouched] = useState(false);
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const inFlight = useRef(false);
  const country = getCountry(values.countryIso);

  const error = useMemo(() => {
    if (!touched) return undefined;
    if (!digitsOnly(values.phone)) return 'Phone number is required';
    if (!country.pattern.test(digitsOnly(values.phone))) return `Enter a valid ${country.maxDigits}-digit mobile number`;
    return undefined;
  }, [country, touched, values.phone]);

  const setPhone = (phone: string) => {
    setValues((previous) => ({ ...previous, phone: sanitizePhone(phone, country) }));
    setFormError(undefined);
  };

  const setCountry = (countryIso: string) => {
    setValues((previous) => ({
      ...previous,
      countryIso,
      phone: sanitizePhone(previous.phone, getCountry(countryIso)),
    }));
    setFormError(undefined);
  };

  const submit = async () => {
    if (inFlight.current) return;
    setTouched(true);
    if (error) return;

    inFlight.current = true;
    setSubmitting(true);
    setFormError(undefined);
    try {
      const response = await authApi.login({ phone: toE164(country, values.phone) });
      router.push({
        pathname: routes.verifyOtp,
        params: {
          requestId: response.requestId,
          phone: toE164(country, values.phone),
          expiresInSec: String(response.expiresInSec),
          resendInSec: String(response.resendInSec),
        },
      });
    } catch (caught) {
      const apiError = toApiError(caught);
      if (apiError.code === 'ACCOUNT_NOT_FOUND') {
        router.push({ pathname: routes.noAccount, params: { phone: toE164(country, values.phone) } });
      } else {
        setFormError(apiError.message);
      }
    } finally {
      inFlight.current = false;
      setSubmitting(false);
    }
  };

  return { values, error, formError, submitting, setPhone, setCountry, submit };
}
