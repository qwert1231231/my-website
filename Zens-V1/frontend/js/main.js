import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";
import { sendMessageToChat } from "./api.js";

// Supabase client
const SUPABASE_URL = "https://YOUR_PROJECT.supabase.co";
const SUPABASE_KEY = "YOUR_PUBLIC_ANON_KEY";
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Dark/light mode toggle
const themeToggle = document.getElementById("themeToggle");
if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light");
  });

  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
  }
}

// Elements for chat
const tryZennoBtn = document.getElementById("tryZennoBtn");
const chatBox = document.getElementById("chatBox");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

// Show chat when button clicked
if (tryZennoBtn) {
  tryZennoBtn.addEventListener("click", (e) => {
    // Redirect to chat.html when button is clicked
    window.location.href = "chat.html";
  });
}

// Send chat message
if (sendBtn) {
  sendBtn.addEventListener("click", async () => {
    if (!chatInput || !chatMessages) return;
    const msg = chatInput.value.trim();
    if (!msg) return;

    addMessage("user", msg);
    chatInput.value = "";

    const response = await sendMessageToChat(msg);
    if (response.success) {
      addMessage("ai", response.reply);
    } else {
      addMessage("ai", "⚠️ Error: " + response.error);
    }
  });
}

// Add messages to UI
function addMessage(sender, text) {
  if (!chatMessages) return;
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("message", sender);
  msgDiv.textContent = text;
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Logout button
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    await supabase.auth.signOut();
    localStorage.clear();
    window.location.href = "login.html";
  });
}
