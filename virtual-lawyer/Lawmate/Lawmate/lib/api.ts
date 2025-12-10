const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  console.log(`🌐 API Request: ${options.method || "GET"} ${url}`);
  console.log(`   BASE_URL: ${BASE_URL}`);
  
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    console.log(`📥 API Response: ${res.status} ${res.statusText} for ${url}`);

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      console.error(`❌ API Error: ${res.status} ${res.statusText} - ${errText}`);
      throw new Error(
        `Request failed: ${res.status} ${res.statusText} ${errText}`.trim()
      );
    }

    const data = await res.json() as T;
    console.log(`✅ API Success: Data received for ${url}`, data);
    return data;
  } catch (error) {
    console.error(`❌ API Request Failed for ${url}:`, error);
    throw error;
  }
}

async function requestMultipart<T>(
  path: string,
  formData: FormData,
  method: HttpMethod = "POST"
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    method,
    body: formData,
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    throw new Error(
      `Request failed: ${res.status} ${res.statusText} ${errText}`.trim()
    );
  }

  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  postMultipart: <T>(path: string, formData: FormData) =>
    requestMultipart<T>(path, formData, "POST"),
};

export { BASE_URL };

