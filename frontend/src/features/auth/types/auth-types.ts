export type SignupField = 'firstName' | 'lastName' | 'email' | 'phone' | 'password';
export type SignupValues = { firstName: string; lastName: string; email: string; countryIso: string; phone: string; password: string };
export type SignupErrors = Partial<Record<SignupField, string>>;

export type LoginValues = { login_id: string; password: string };
export type LoginPayload = { login_id: string; password: string };

export type SignupPayload = { first_name: string; last_name: string; email: string; phone: string; password: string };
export type RegisterPayload = SignupPayload & { firebase_id_token: string };
export type AuthResponse = {
  accessToken: string;
  refreshToken: string;
  user?: { id: string; first_name: string; last_name: string; email: string; phone?: string };
};
export type SignupResponse = {
  accessToken?: string;
  refreshToken?: string;
  user?: { id: string; first_name: string; last_name: string; email: string; phone?: string };
};
export type OtpSessionResponse = { requestId: string; expiresInSec: number; resendInSec: number };
export type VerifyOtpResponse = AuthResponse;
export type VerifyOtpPayload = { requestId: string; otp: string };
export interface AuthApi {
  register(payload: RegisterPayload): Promise<SignupResponse>;
  login(payload: LoginPayload): Promise<AuthResponse>;
  verifyOtp(payload: VerifyOtpPayload): Promise<VerifyOtpResponse>;
  resendOtp(requestId: string): Promise<OtpSessionResponse>;
}
