(function () {
  "use strict";

  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const chatContainer = document.getElementById("chatContainer");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const errorBanner = document.getElementById("errorBanner");
  const moodButtons = document.querySelectorAll(".mood-btn");

  let selectedMood = null;
  let isLoading = false;

  moodButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      moodButtons.forEach(function (b) {
        b.classList.remove("active");
      });
      if (selectedMood === btn.dataset.mood) {
        selectedMood = null;
      } else {
        btn.classList.add("active");
        selectedMood = btn.dataset.mood === "other" ? null : btn.dataset.mood;
      }
    });
  });

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.classList.remove("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
    errorBanner.textContent = "";
  }

  function setLoading(loading) {
    isLoading = loading;
    sendBtn.disabled = loading;
    messageInput.disabled = loading;
    loadingIndicator.classList.toggle("hidden", !loading);
  }

  function appendMessage(text, role, options) {
    options = options || {};
    const wrapper = document.createElement("div");
    wrapper.className = "message " + (role === "user" ? "user-message" : "bot-message");

    if (options.isCrisis) {
      wrapper.classList.add("crisis-message");
    }

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    if (options.mood && options.mood !== "neutral" && options.mood !== "crisis") {
      const tag = document.createElement("span");
      tag.className = "mood-tag";
      tag.textContent = "Detected mood: " + options.mood;
      bubble.appendChild(document.createElement("br"));
      bubble.appendChild(tag);
    }

    wrapper.appendChild(bubble);
    chatContainer.appendChild(wrapper);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  async function sendMessage(message) {
    hideError();
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          mood: selectedMood,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        showError(data.error || "Something went wrong. Please try again.");
        return;
      }

      appendMessage(data.reply, "bot", {
        mood: data.mood,
        isCrisis: data.is_crisis,
      });
    } catch (_err) {
      showError("Unable to reach the server. Please check your connection and try again.");
    } finally {
      setLoading(false);
      messageInput.focus();
    }
  }

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    if (isLoading) return;

    const message = messageInput.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    messageInput.value = "";
    sendMessage(message);
  });

  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.requestSubmit();
    }
  });
})();
