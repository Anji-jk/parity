const at = (w: number, h: number) => ({
  x: (v: number) => (v * w).toFixed(1),
  y: (v: number) => (v * h).toFixed(1),
});

export function signupFooterPath(w: number, h: number): string {
  const { x, y } = at(w, h);
  return [
    `M ${x(0)} ${y(0.02)}`,
    `C ${x(0.18)} ${y(0.17)} ${x(0.4)} ${y(0.19)} ${x(0.62)} ${y(0.14)}`,
    `C ${x(0.8)} ${y(0.1)} ${x(0.92)} ${y(0.09)} ${x(1)} ${y(0.11)}`,
    `L ${x(1)} ${y(1)} L ${x(0)} ${y(1)} Z`,
  ].join(' ');
}

export function verifyFooterPath(w: number, h: number): string {
  const { x, y } = at(w, h);
  return [
    `M ${x(0)} ${y(0.6)}`,
    `C ${x(0.2)} ${y(0.5)} ${x(0.3)} ${y(0.36)} ${x(0.45)} ${y(0.3)}`,
    `C ${x(0.65)} ${y(0.2)} ${x(0.85)} ${y(0.14)} ${x(1)} ${y(0.12)}`,
    `L ${x(1)} ${y(1)} L ${x(0)} ${y(1)} Z`,
  ].join(' ');
}
