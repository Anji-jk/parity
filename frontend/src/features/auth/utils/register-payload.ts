import { getCountry } from '../constants/countries';
import type { SignupPayload, SignupValues } from '../types/auth-types';
import { normalizeName } from '../validation/signup-validation';
import { toE164 } from './phone';

export function buildRegisterPayload(v: SignupValues): SignupPayload {
  return {
    first_name: normalizeName(v.firstName),
    last_name: normalizeName(v.lastName),
    email: v.email.trim().toLowerCase(),
    phone: toE164(getCountry(v.countryIso), v.phone),
    password: v.password,
  };
}
