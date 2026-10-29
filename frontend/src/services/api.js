import axios from "axios";
import { collectPages, mediaUrl } from "./data";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "/api"
).replace(/\/+$/, "");
export const MEDIA_BASE_URL = (
  import.meta.env.VITE_MEDIA_BASE_URL ||
  (API_BASE_URL.startsWith("http") ? new URL(API_BASE_URL).origin : "")
).replace(/\/+$/, "");
const api = axios.create({ timeout: 15000 });

api.interceptors.response.use(
  (response) => {
    if (
      /\/(cart|orders)\//.test(response.config.url) &&
      response.config.method !== "get"
    ) {
      window.dispatchEvent(new Event("cart-updated"));
    }
    return response;
  },
  (error) => {
    if (
      error.response?.status === 401 &&
      !error.config.url.includes("/users/login/")
    ) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.dispatchEvent(new Event("auth-changed"));
    }
    return Promise.reject(error);
  },
);

export function getImageUrl(image) {
  return mediaUrl(image, MEDIA_BASE_URL);
}

// Follow DRF pages with the original filters, always using the configured API origin.
export function getAllPages(path, config = {}) {
  return collectPages(api, path, config, window.location.origin);
}
export default api;
