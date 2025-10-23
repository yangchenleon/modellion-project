export function setToken(token: string) {
  localStorage.setItem("token", token);
}
export function getToken(): string | null {
  return localStorage.getItem("token");
}
export function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
}
export function setRole(role: string) {
  localStorage.setItem("role", role);
}
export function getRole(): string | null {
  return localStorage.getItem("role");
}


