import { ApiError } from '@/services/http/api-error';
import type { AuthApi, RegisterPayload } from '../types/auth-types';

const wait = (ms = 700) => new Promise((r) => setTimeout(r, ms));
const MOCK_OTP = '123456';
const MAX_ATTEMPTS = 5;
const EXPIRY_SEC = 60;
const RESEND_SEC = 30;

const sessions = new Map<string, { payload: RegisterPayload; expiresAt: number; attempts: number }>();
const session = (requestId: string) => ({ requestId, expiresInSec: EXPIRY_SEC, resendInSec: RESEND_SEC });
const DEMO_PHONE = '+919876543210';

export const mockAuthApi: AuthApi = {
  async register(payload) {
    await wait();
    if (payload.email === 'taken@example.com') {
      throw new ApiError(409, 'EMAIL_TAKEN', 'This email is already registered.', {
        fieldErrors: { email: 'This email is already registered' },
      });
    }
    const requestId = `mock-${Date.now()}`;
    sessions.set(requestId, { payload, expiresAt: Date.now() + EXPIRY_SEC * 1000, attempts: 0 });
    return session(requestId);
  },

  async login(payload) {
    await wait();
    if (payload.phone !== DEMO_PHONE) throw new ApiError(404, 'ACCOUNT_NOT_FOUND', 'We could not find an account with this phone number.');
    const requestId = `mock-login-${Date.now()}`;
    sessions.set(requestId, {
      payload: { firstName: 'Demo', lastName: 'User', email: 'demo@example.com', phone: payload.phone },
      expiresAt: Date.now() + EXPIRY_SEC * 1000,
      attempts: 0,
    });
    return session(requestId);
  },

  async verifyOtp({ requestId, otp }) {
    await wait();
    const s = sessions.get(requestId);
    if (!s) throw new ApiError(404, 'SESSION_NOT_FOUND', 'Session expired. Please sign up again.');
    if (s.attempts >= MAX_ATTEMPTS) throw new ApiError(429, 'OTP_LOCKED', 'Too many attempts. Please request a new code.');
    if (Date.now() > s.expiresAt) throw new ApiError(410, 'OTP_EXPIRED', 'This code has expired. Please request a new one.');
    if (otp !== MOCK_OTP) {
      s.attempts += 1;
      throw new ApiError(400, 'OTP_INVALID', 'Incorrect code.', { details: { attemptsLeft: MAX_ATTEMPTS - s.attempts } });
    }
    return { accessToken: 'mock-access-token', refreshToken: 'mock-refresh-token', user: { id: 'mock-user', ...s.payload } };
  },

  async resendOtp(requestId) {
    await wait();
    const s = sessions.get(requestId);
    if (!s) throw new ApiError(404, 'SESSION_NOT_FOUND', 'Session expired. Please sign up again.');
    s.expiresAt = Date.now() + EXPIRY_SEC * 1000;
    s.attempts = 0;
    return session(requestId);
  },
};
