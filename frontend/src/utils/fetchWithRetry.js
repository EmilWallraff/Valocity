export async function fetchWithRetry(url, options = {}, retries = 3, delay = 1000) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`Status: ${response.status}`);
    return await response.json();
  } catch (err) {
    if (retries <= 0) throw err;
    await new Promise((res) => setTimeout(res, delay));
    return fetchWithRetry(url, options, retries - 1, delay * 2);
  }
}