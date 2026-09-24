import { env } from '@/config/env';
import { request } from '@/services/http/http-client';
import type { AuthApi, OtpSessionResponse, VerifyOtpResponse } from '../types/auth-types';
import { mockAuthApi } from './auth-api.mock';

const realAuthApi: AuthApi = {
  register: (payload) => request<OtpSessionResponse>('/v1/auth/register', { method: 'POST', body: payload }),
  login: (payload) => request<OtpSessionResponse>('/v1/auth/login', { method: 'POST', body: payload }),
  verifyOtp: (payload) => request<VerifyOtpResponse>('/v1/auth/otp/verify', { method: 'POST', body: payload }),
  resendOtp: (requestId) => request<OtpSessionResponse>('/v1/auth/otp/resend', { method: 'POST', body: { requestId } }),
};

export const authApi: AuthApi = env.useMockApi ? mockAuthApi : realAuthApi;
