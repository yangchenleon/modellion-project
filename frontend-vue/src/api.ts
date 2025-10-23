const API_BASE = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";
const MINIO_PUBLIC_BASE = (import.meta as any).env?.VITE_MINIO_PUBLIC_BASE || "http://localhost:9000";

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
  
  // 处理401未授权错误（token过期）
  if (res.status === 401) {
    console.warn("Token已过期，清除本地token并跳转到登录页");
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    // 跳转到登录页
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    let msg = "登录已过期，请重新登录";
    try {
      const data = await res.json();
      msg = (data && (data.detail || data.message)) || msg;
    } catch {}
    throw new Error(msg);
  }
  
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
    
    // 处理401（FormData上传不走http函数）
    if (res.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
      throw new Error("登录已过期，请重新登录");
    }
    
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async presign(imageId: number) {
    const res = await http<{ url: string }>(`/api/images/presign/${imageId}`);
    // 将容器内主机名替换为浏览器可访问的公共地址
    const url = res.url
      .replace("http://minio:9000", MINIO_PUBLIC_BASE)
      .replace("https://minio:9000", MINIO_PUBLIC_BASE);
    return { url } as { url: string };
  },
  async deleteImage(imageId: number, deleteObject: boolean) {
    const usp = new URLSearchParams({ delete_object: String(!!deleteObject) });
    return http(`/api/images/${imageId}?${usp.toString()}`, { method: "DELETE" });
  },
  async setImageAsCover(imageId: number) {
    return http(`/api/images/${imageId}/set-cover`, { method: "PUT" });
  },

  // import
  async importFromJson() {
    return http<{ total: number; created: number; updated: number; errors: string[] }>(
      "/api/import/json",
      { method: "POST" }
    );
  },
  async importFromZip(file: File) {
    const form = new FormData();
    form.append("file", file);
    
    const headers = { ...authHeaders() };
    
    const res = await fetch(`${API_BASE}/api/import/zip`.replace(/\/$/, ""), {
      method: "POST",
      body: form,
      headers,
    });
    
    // 处理401（FormData上传不走http函数）
    if (res.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
      throw new Error("登录已过期，请重新登录");
    }
    
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text);
    }
    return res.json() as Promise<{ total: number; created: number; updated: number; errors: string[] }>;
  },

  // stats
  async statsOverview(top = 10) {
    return http(
      `/api/stats/overview?${new URLSearchParams({ top: String(top) }).toString()}`
    );
  },
};


