import { getCountry } from '../constants/countries';
import type { RegisterPayload, SignupValues } from '../types/auth-types';
import { normalizeName } from '../validation/signup-validation';
import { toE164 } from './phone';

export function buildRegisterPayload(v: SignupValues): RegisterPayload {
  return {
    firstName: normalizeName(v.firstName),
    lastName: normalizeName(v.lastName),
    email: v.email.trim().toLowerCase(),
    phone: toE164(getCountry(v.countryIso), v.phone),
  };
}
