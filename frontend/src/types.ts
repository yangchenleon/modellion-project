export type User = { id: number; username: string; role: "admin" | "readonly"; created_at: string };

export type Product = {
  id: number;
  product_name?: string;
  price?: string;
  release_date?: string;
  article_content?: string;
  url: string;
  product_tag?: string;
  series?: string;
  created_at: string;
};

export type Image = {
  id: number;
  product_id: number;
  image_filename: string;
  image_hash?: string;
  minio_path?: string;
  created_at: string;
};

export type Page<T> = { items: T[]; meta: { page: number; page_size: number; total: number } };
