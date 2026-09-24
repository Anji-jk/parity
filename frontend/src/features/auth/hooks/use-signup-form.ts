import { useRouter } from 'expo-router';
import { useMemo, useRef, useState } from 'react';

import { routes } from '@/constants/routes';
import { toApiError } from '@/services/http/api-error';
import { authApi } from '../api/auth-api';
import { DEFAULT_COUNTRY, getCountry } from '../constants/countries';
import type { SignupErrors, SignupField, SignupValues } from '../types/auth-types';
import { sanitizePhone, toE164 } from '../utils/phone';
import { buildRegisterPayload } from '../utils/register-payload';
import { FIELD_ORDER, firstInvalidField, validateSignup } from '../validation/signup-validation';

const INITIAL: SignupValues = { firstName: '', lastName: '', email: '', countryIso: DEFAULT_COUNTRY.iso, phone: '' };

export function useSignupForm(options: { onInvalidField?: (field: SignupField) => void } = {}) {
  const router = useRouter();
  const [values, setValues] = useState<SignupValues>(INITIAL);
  const [touched, setTouched] = useState<Partial<Record<SignupField, boolean>>>({});
  const [serverErrors, setServerErrors] = useState<SignupErrors>({});
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);
  const inFlight = useRef(false);

  const clientErrors = useMemo(() => validateSignup(values), [values]);

  const errors = useMemo(() => {
    const out: SignupErrors = {};
    for (const f of FIELD_ORDER) out[f] = (touched[f] ? clientErrors[f] : undefined) ?? serverErrors[f];
    return out;
  }, [clientErrors, touched, serverErrors]);

  const clearServer = (field: SignupField) => {
    setServerErrors((prev) => (prev[field] ? { ...prev, [field]: undefined } : prev));
    setFormError(undefined);
  };

  const setField = (field: SignupField, text: string) => {
    setValues((prev) => ({
      ...prev,
      [field]: field === 'phone' ? sanitizePhone(text, getCountry(prev.countryIso)) : text,
    }));
    clearServer(field);
  };

  const setCountry = (iso: string) => {
    setValues((prev) => ({ ...prev, countryIso: iso, phone: sanitizePhone(prev.phone, getCountry(iso)) }));
    clearServer('phone');
  };

  const markTouched = (field: SignupField) => setTouched((prev) => (prev[field] ? prev : { ...prev, [field]: true }));

  const submit = async () => {
    if (inFlight.current) return;
    setTouched({ firstName: true, lastName: true, email: true, phone: true });

    const invalid = firstInvalidField(clientErrors);
    if (invalid) {
      options.onInvalidField?.(invalid);
      return;
    }

    inFlight.current = true;
    setSubmitting(true);
    setFormError(undefined);
    try {
      const res = await authApi.register(buildRegisterPayload(values));
      router.push({
        pathname: routes.verifyOtp,
        params: {
          requestId: res.requestId,
          phone: toE164(getCountry(values.countryIso), values.phone),
          expiresInSec: String(res.expiresInSec),
          resendInSec: String(res.resendInSec),
        },
      });
    } catch (e) {
      const err = toApiError(e);
      if (err.fieldErrors) {
        const mapped: SignupErrors = {};
        for (const f of FIELD_ORDER) if (err.fieldErrors[f]) mapped[f] = err.fieldErrors[f];
        setServerErrors(mapped);
        const first = FIELD_ORDER.find((f) => mapped[f]);
        if (first) options.onInvalidField?.(first);
        else setFormError(err.message);
      } else {
        setFormError(err.message);
      }
    } finally {
      inFlight.current = false;
      setSubmitting(false);
    }
  };

  return { values, errors, formError, submitting, setField, setCountry, markTouched, submit };
}
