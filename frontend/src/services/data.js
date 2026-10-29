// Keep URL handling independent of Vue so pagination and media contracts are testable.
export function mediaUrl(image, base = "") {
  if (!image) return "";
  if (/^https?:\/\//i.test(image)) return image;
  return `${base.replace(/\/+$/, "")}${image.startsWith("/media/") ? image : `/media/${image.replace(/^\/+/, "")}`}`;
}

export async function collectPages(client, path, config = {}, origin) {
  const items = [];
  const seen = new Set();
  const current = new URL(path, origin);
  let url = path;
  let requestConfig = config;
  while (url) {
    if (seen.has(url)) throw new Error("分页链接重复，请稍后重试");
    seen.add(url);
    const { data } = await client.get(url, requestConfig);
    items.push(...(Array.isArray(data) ? data : data.results || []));
    if (Array.isArray(data) || !data.next) break;
    const next = new URL(data.next, origin);
    // DRF may build next links using an internal host; never forward credentials there.
    url = `${current.origin}${current.pathname}${next.search}`;
    requestConfig = { ...config, params: undefined };
  }
  return items;
}
