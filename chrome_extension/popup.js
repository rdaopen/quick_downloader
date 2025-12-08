document.getElementById("downloadBtn").addEventListener("click", async () => {
  const statusDiv = document.getElementById("status");
  statusDiv.textContent = "Sending...";
  statusDiv.className = "status";

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url) {
    statusDiv.textContent = "No active tab found.";
    statusDiv.className = "status error";
    return;
  }

  try {
    const response = await fetch("http://localhost:6006/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: tab.url }),
    });

    const result = await response.json();

    if (result.status === "ok") {
      statusDiv.textContent = "Sent!";
      statusDiv.className = "status success";
      setTimeout(() => window.close(), 1000);
    } else {
      statusDiv.textContent = "Error: " + result.message;
      statusDiv.className = "status error";
    }
  } catch (err) {
    statusDiv.textContent = "Failed to connect. Is the app open?";
    statusDiv.className = "status error";
  }
});
