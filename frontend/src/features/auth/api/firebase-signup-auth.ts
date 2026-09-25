import { env } from '@/config/env';
import { authApi } from './auth-api';
import type { ConfirmationResult } from '@react-native-firebase/auth';
import type { RegisterPayload, SignupPayload } from '../types/auth-types';

const MOCK_OTP = '123456';
const EXPIRY_SEC = 60;
const RESEND_SEC = 30;

let confirmation: ConfirmationResult | undefined;
let pendingPayload: SignupPayload | undefined;

async function getFirebaseAuth() {
  return import('@react-native-firebase/auth');
}

export type SignupOtpSession = {
  requestId: 'firebase';
  expiresInSec: number;
  resendInSec: number;
};

export async function startSignupOtp(payload: SignupPayload): Promise<SignupOtpSession> {
  pendingPayload = payload;
  if (!env.useMockApi) {
    const { getAuth, signInWithPhoneNumber } = await getFirebaseAuth();
    confirmation = await signInWithPhoneNumber(getAuth(), payload.phone);
  }
  return { requestId: 'firebase', expiresInSec: EXPIRY_SEC, resendInSec: RESEND_SEC };
}

export async function resendSignupOtp(): Promise<SignupOtpSession> {
  if (!pendingPayload) throw new Error('Signup session expired. Please start again.');
  if (!env.useMockApi) {
    const { getAuth, signInWithPhoneNumber } = await getFirebaseAuth();
    confirmation = await signInWithPhoneNumber(getAuth(), pendingPayload.phone);
  }
  return { requestId: 'firebase', expiresInSec: EXPIRY_SEC, resendInSec: RESEND_SEC };
}

export async function confirmSignupOtp(otp: string) {
  if (!pendingPayload) throw new Error('Signup session expired. Please start again.');

  let firebaseIdToken = 'mock-firebase-id-token';
  if (env.useMockApi) {
    if (otp !== MOCK_OTP) throw new Error('Incorrect code. Please try again.');
  } else {
    if (!confirmation) throw new Error('Signup session expired. Please request a new code.');
    const credential = await confirmation.confirm(otp);
    firebaseIdToken = await credential.user.getIdToken();
  }

  const payload: RegisterPayload = { ...pendingPayload, firebase_id_token: firebaseIdToken };
  const response = await authApi.register(payload);
  pendingPayload = undefined;
  confirmation = undefined;
  return response;
}
