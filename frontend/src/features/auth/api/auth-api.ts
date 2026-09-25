import { env } from '@/config/env';
import { request } from '@/services/http/http-client';
import type { AuthApi, OtpSessionResponse, VerifyOtpResponse } from '../types/auth-types';
import { mockAuthApi } from './auth-api.mock';

type BackendLoginResponse = {
  access_token: string;
  refresh_token: string;
  role: string;
  user_id: string;
};

type BackendSignupResponse = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
};

const realAuthApi: AuthApi = {
  register: async (payload) => {
    const response = await request<BackendSignupResponse>('/api/v1/auth/signup', { method: 'POST', body: payload });
    return { user: response };
  },
  login: async (payload) => {
    const response = await request<BackendLoginResponse>('/v1/auth/login', { method: 'POST', body: payload });
    return { accessToken: response.access_token, refreshToken: response.refresh_token };
  },
  verifyOtp: (payload) => request<VerifyOtpResponse>('/v1/auth/otp/verify', { method: 'POST', body: payload }),
  resendOtp: (requestId) => request<OtpSessionResponse>('/v1/auth/otp/resend', { method: 'POST', body: { requestId } }),
};

export const authApi: AuthApi = env.useMockApi ? mockAuthApi : realAuthApi;
