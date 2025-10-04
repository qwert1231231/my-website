// Handles API calls to backend

// Send a message to the /chat endpoint and get the AI reply
export async function sendMessageToChat(message) {
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
  return await res.json();
}

// Example: fetch data from any backend endpoint
export async function fetchData(endpoint) {
  const res = await fetch(endpoint);
  if (!res.ok) throw new Error("API error");
  return await res.json();
}
