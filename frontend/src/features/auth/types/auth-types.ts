export type SignupField = 'firstName' | 'lastName' | 'email' | 'phone';
export type SignupValues = { firstName: string; lastName: string; email: string; countryIso: string; phone: string };
export type SignupErrors = Partial<Record<SignupField, string>>;

export type LoginValues = { countryIso: string; phone: string };
export type LoginPayload = { phone: string };

export type RegisterPayload = { firstName: string; lastName: string; email: string; phone: string /* E.164 */ };
export type OtpSessionResponse = { requestId: string; expiresInSec: number; resendInSec: number };
export type VerifyOtpPayload = { requestId: string; otp: string };
export type VerifyOtpResponse = {
  accessToken: string;
  refreshToken: string;
  user: { id: string; firstName: string; lastName: string; email: string; phone: string };
};

export interface AuthApi {
  register(payload: RegisterPayload): Promise<OtpSessionResponse>;
  login(payload: LoginPayload): Promise<OtpSessionResponse>;
  verifyOtp(payload: VerifyOtpPayload): Promise<VerifyOtpResponse>;
  resendOtp(requestId: string): Promise<OtpSessionResponse>;
}
