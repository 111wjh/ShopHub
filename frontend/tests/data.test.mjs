import test from "node:test";
import assert from "node:assert/strict";
import { collectPages, mediaUrl } from "../src/services/data.js";

test("media paths support absent, absolute and relative Django images", () => {
  assert.equal(mediaUrl(null), "");
  assert.equal(
    mediaUrl("https://cdn.example.com/a.webp", "https://api.example.com"),
    "https://cdn.example.com/a.webp",
  );
  assert.equal(mediaUrl("/media/products/a.webp"), "/media/products/a.webp");
  assert.equal(
    mediaUrl("products/a.webp", "https://api.example.com/"),
    "https://api.example.com/media/products/a.webp",
  );
});

test("plain list responses require only one request", async () => {
  let calls = 0;
  const result = await collectPages(
    {
      get: async () => {
        calls++;
        return { data: [{ id: 1 }] };
      },
    },
    "/api/orders/",
    {},
    "http://localhost:5173",
  );
  assert.deepEqual(result, [{ id: 1 }]);
  assert.equal(calls, 1);
});

test("DRF pagination returns products after page one and keeps auth, filters and cancellation", async () => {
  const calls = [];
  const signal = new AbortController().signal;
  const headers = { Authorization: "Bearer test-only" };
  const client = {
    get: async (url, config) => {
      calls.push({ url, config });
      return {
        data:
          calls.length === 1
            ? {
                results: [{ id: 1 }],
                next: "http://backend:8000/api/products/?category=3&page=2",
              }
            : { results: [{ id: 11 }], next: null },
      };
    },
  };
  assert.deepEqual(
    await collectPages(
      client,
      "/api/products/",
      { params: { category: 3 }, headers, signal },
      "http://localhost:5173",
    ),
    [{ id: 1 }, { id: 11 }],
  );
  assert.equal(
    calls[1].url,
    "http://localhost:5173/api/products/?category=3&page=2",
  );
  assert.equal(calls[1].config.params, undefined);
  assert.equal(calls[1].config.headers, headers);
  assert.equal(calls[1].config.signal, signal);
});

test("configured external API base is preserved on later pages", async () => {
  const urls = [];
  await collectPages(
    {
      get: async (url) => {
        urls.push(url);
        return {
          data: {
            results: [],
            next: urls.length === 1 ? "/api/products/?page=2" : null,
          },
        };
      },
    },
    "https://api.example.com/api/products/",
    {},
    "https://shop.example.com",
  );
  assert.equal(urls[1], "https://api.example.com/api/products/?page=2");
});

test("empty page produces an empty collection", async () => {
  assert.deepEqual(
    await collectPages(
      { get: async () => ({ data: { results: [], next: null } }) },
      "/api/products/",
      {},
      "http://localhost",
    ),
    [],
  );
});

test("repeated pagination is rejected instead of looping indefinitely", async () => {
  let calls = 0;
  await assert.rejects(
    () =>
      collectPages(
        {
          get: async () => {
            calls++;
            return { data: { results: [], next: "?page=2" } };
          },
        },
        "/api/products/",
        {},
        "http://localhost",
      ),
    /分页链接重复/,
  );
  assert.equal(calls, 2);
});

test("failed later pages reject rather than silently returning incomplete products", async () => {
  let calls = 0;
  await assert.rejects(
    () =>
      collectPages(
        {
          get: async () => {
            calls++;
            if (calls === 2) throw new Error("service unavailable");
            return { data: { results: [{ id: 1 }], next: "?page=2" } };
          },
        },
        "/api/products/",
        {},
        "http://localhost",
      ),
    /service unavailable/,
  );
});
