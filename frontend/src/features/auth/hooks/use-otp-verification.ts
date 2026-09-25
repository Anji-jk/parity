import { useRouter } from 'expo-router';
import { useRef, useState } from 'react';

import { routes } from '@/constants/routes';
import { useCountdown } from '@/hooks/use-countdown';
import { toApiError } from '@/services/http/api-error';
import { tokenStorage } from '@/services/storage/token-storage';
import { authApi } from '../api/auth-api';
import { confirmSignupOtp, resendSignupOtp } from '../api/firebase-signup-auth';
import { OTP_LENGTH } from '../constants/auth-config';

type Params = { requestId: string; expiresInSec: number; resendInSec: number };

export function useOtpVerification({ requestId, expiresInSec, resendInSec }: Params) {
  const router = useRouter();
  const [otp, setOtpState] = useState('');
  const [error, setError] = useState<string>();
  const [verifying, setVerifying] = useState(false);
  const [resending, setResending] = useState(false);
  const [locked, setLocked] = useState(false);
  const inFlight = useRef(false);

  const expiry = useCountdown(expiresInSec);
  const cooldown = useCountdown(resendInSec);

  const canVerify = otp.length === OTP_LENGTH && !expiry.isDone && !locked && !verifying;
  const canResend = cooldown.isDone && !resending && !verifying;

  const setOtp = (value: string) => {
    setOtpState(value);
    if (error) setError(undefined);
  };

  const verify = async () => {
    if (!canVerify || inFlight.current) return;
    inFlight.current = true;
    setVerifying(true);
    setError(undefined);
    try {
      const res = requestId === 'firebase'
        ? await confirmSignupOtp(otp)
        : await authApi.verifyOtp({ requestId, otp });
      if (res.accessToken && res.refreshToken) {
        await tokenStorage.save({ accessToken: res.accessToken, refreshToken: res.refreshToken });
      }
      router.replace(routes.roleSelection);
    } catch (e) {
      const err = toApiError(e);
      switch (err.code) {
        case 'OTP_INVALID': {
          const left = err.details?.attemptsLeft;
          setError(
            typeof left === 'number'
              ? `Incorrect code. ${left} ${left === 1 ? 'attempt' : 'attempts'} left.`
              : 'Incorrect code. Please try again.',
          );
          setOtpState('');
          break;
        }
        case 'OTP_EXPIRED':
          expiry.restart(0);
          setError('This code has expired. Please request a new one.');
          break;
        case 'OTP_LOCKED':
          setLocked(true);
          setError(err.message);
          break;
        default:
          setError(err.message);
      }
    } finally {
      inFlight.current = false;
      setVerifying(false);
    }
  };

  const resend = async () => {
    if (!canResend) return;
    setResending(true);
    setError(undefined);
    try {
      const res = requestId === 'firebase'
        ? await resendSignupOtp()
        : await authApi.resendOtp(requestId);
      setOtpState('');
      setLocked(false);
      expiry.restart(res.expiresInSec);
      cooldown.restart(res.resendInSec);
    } catch (e) {
      setError(toApiError(e).message);
    } finally {
      setResending(false);
    }
  };

  return {
    otp,
    setOtp,
    error,
    verify,
    resend,
    canVerify,
    canResend,
    verifying,
    resending,
    isExpired: expiry.isDone,
    expiresIn: expiry.secondsLeft,
    resendIn: cooldown.secondsLeft,
  };
}
