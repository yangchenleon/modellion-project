const API_BASE = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function http<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`.replace(/\/$/, ""), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...authHeaders(),
    },
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const data = await res.json();
      msg = (data && (data.detail || data.message)) || msg;
    } catch {}
    throw new Error(msg);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return (await res.json()) as T;
  // @ts-expect-error any
  return (await res.text()) as T;
}

export const api = {
  // auth
  async login(username: string, password: string) {
    return http<{ access_token: string; token_type: string; expires_in: number }>(
      "/api/auth/login",
      { method: "POST", body: JSON.stringify({ username, password }) }
    );
  },
  async me() {
    return http<{ id: number; username: string; role: string; created_at: string }>(
      "/api/auth/me"
    );
  },

  // products
  async getProducts(params: Record<string, any>) {
    const usp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v === undefined || v === null || v === "") return;
      usp.set(k, String(v));
    });
    return http<{ items: any[]; meta: { page: number; page_size: number; total: number } }>(
      `/api/products/?${usp.toString()}`
    );
  },
  async getProduct(id: number) {
    return http(`/api/products/${id}`);
  },
  async createProduct(payload: any) {
    return http(`/api/products/`, { method: "POST", body: JSON.stringify(payload) });
  },
  async updateProduct(id: number, payload: any) {
    return http(`/api/products/${id}`, { method: "PUT", body: JSON.stringify(payload) });
  },
  async deleteProduct(id: number) {
    return http(`/api/products/${id}`, { method: "DELETE" });
  },

  // images
  async listImages(productId: number) {
    return http(`/api/images/product/${productId}`);
  },
  async uploadImage(productId: number, file: File) {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_BASE}/api/images/upload/${productId}`.replace(/\/$/, ""), {
      method: "POST",
      body: form,
      headers: { ...authHeaders() },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async presign(imageId: number) {
    return http<{ url: string }>(`/api/images/presign/${imageId}`);
  },
  async deleteImage(imageId: number, deleteObject: boolean) {
    const usp = new URLSearchParams({ delete_object: String(!!deleteObject) });
    return http(`/api/images/${imageId}?${usp.toString()}`, { method: "DELETE" });
  },

  // import
  async importFromJson() {
    return http<{ total: number; created: number; updated: number; errors: string[] }>(
      "/api/import/json",
      { method: "POST" }
    );
  },

  // stats
  async statsOverview(top = 10) {
    return http(
      `/api/stats/overview?${new URLSearchParams({ top: String(top) }).toString()}`
    );
  },
};
