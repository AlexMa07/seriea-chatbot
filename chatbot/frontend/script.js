const API_URL = "/api/chat";

const chatArea   = document.getElementById("chatArea");
const inputField = document.getElementById("userInput");
const sendBtn    = document.getElementById("sendBtn");
const suggestions = document.getElementById("suggestions");

// ── Message rendering ───────────────────────────────────────────────────────

function appendMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "🧑" : "🏆";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "bot") {
    // Wrap monospaced blocks (lines starting with spaces or box-drawing chars)
    bubble.innerHTML = formatBotText(text);
  } else {
    bubble.textContent = text;
  }

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatArea.appendChild(wrap);
  scrollBottom();
  return wrap;
}

function formatBotText(text) {
  // Escape HTML, then restore line breaks and make table-like blocks monospaced
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // If the text contains table-like lines (leading spaces / box chars) wrap in <pre>
  const hasTable = /^\s{2,}/m.test(escaped) || /─/.test(escaped);
  if (hasTable) {
    return `<pre>${escaped}</pre>`;
  }
  // Otherwise just convert newlines to <br>
  return escaped.replace(/\n/g, "<br>");
}

function showTyping() {
  const wrap = document.createElement("div");
  wrap.className = "message bot";
  wrap.id = "typing";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "🏆";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML =
    '<span class="typing-dot"></span>' +
    '<span class="typing-dot"></span>' +
    '<span class="typing-dot"></span>';

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chatArea.appendChild(wrap);
  scrollBottom();
}

function removeTyping() {
  const el = document.getElementById("typing");
  if (el) el.remove();
}

function scrollBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

// ── Send logic ──────────────────────────────────────────────────────────────

async function sendMessage() {
  const text = inputField.value.trim();
  if (!text) return;

  // Hide suggestions after first interaction
  suggestions.style.display = "none";

  appendMessage("user", text);
  inputField.value = "";
  sendBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    removeTyping();
    appendMessage("bot", data.response);
  } catch (err) {
    removeTyping();
    appendMessage("bot", "Errore di comunicazione con il server. Riprova.");
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    inputField.focus();
  }
}

function sendSuggestion(btn) {
  inputField.value = btn.textContent.replace(/^[^\w]+/, "").trim();
  sendMessage();
}

// ── Key binding ─────────────────────────────────────────────────────────────

inputField.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
