const API_BASE = "http://localhost:8000/api";

// Elements
const promptInput = document.getElementById("promptInput");
const paintButton = document.getElementById("paintButton");
const imagePlaceholder = document.getElementById("imagePlaceholder");
const generatedImage = document.getElementById("generatedImage");
const imageLoading = document.getElementById("imageLoading");

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatLoading = document.getElementById("chatLoading");
const chatOutputBox = document.getElementById("chatOutputBox");
const voiceButton = document.getElementById("voiceButton");

// State
let conversationHistory = "";
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

// Image Generation
paintButton.addEventListener("click", async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    // UI state
    paintButton.disabled = true;
    imagePlaceholder.style.display = "none";
    imageLoading.style.display = "flex";

    try {
        const formData = new FormData();
        formData.append("prompt", prompt);

        const response = await fetch(`${API_BASE}/generate-image`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Image generation failed");

        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);

        generatedImage.src = imageUrl;
        generatedImage.style.display = "block";
    } catch (error) {
        console.error("Error generating image:", error);
        alert("Failed to generate image. Ensure backend is running.");
        imagePlaceholder.style.display = "flex";
        generatedImage.style.display = "none";
    } finally {
        imageLoading.style.display = "none";
        paintButton.disabled = false;
    }
});

// Chat Output Helper
function addMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender === 'YOU' ? 'msg-user' : 'msg-bot'}`;
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatMessages.appendChild(msgDiv);

    // Auto scroll to bottom
    chatOutputBox.scrollTop = chatOutputBox.scrollHeight;
}

// Chat Send
sendButton.addEventListener("click", async () => {
    const message = chatInput.value.trim();
    if (!message) return;

    // UI state
    chatInput.value = "";
    sendButton.disabled = true;
    addMessage("YOU", message);
    chatLoading.style.display = "block";

    try {
        const formData = new FormData();
        formData.append("history", conversationHistory);
        formData.append("message", message);

        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Chat failed");

        const data = await response.json();
        const reply = data.reply || "I'm speechless!";

        addMessage("MUNCH", reply);

        // Update history
        conversationHistory += `\nYOU: ${message}\nMUNCH: ${reply}`;
    } catch (error) {
        console.error("Error sending message:", error);
        addMessage("SYSTEM", "Error connecting to backend.");
    } finally {
        chatLoading.style.display = "none";
        sendButton.disabled = false;
    }
});

chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendButton.click();
    }
});

// Voice Input
voiceButton.addEventListener("click", async () => {
    if (isRecording) {
        // Stop recording
        mediaRecorder.stop();
        isRecording = false;
        voiceButton.classList.remove("recording");
        voiceButton.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    } else {
        // Start recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                await processAudio(audioBlob);

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            });

            mediaRecorder.start();
            isRecording = true;
            voiceButton.classList.add("recording");
            voiceButton.innerHTML = '<i class="fa-solid fa-stop"></i>';
        } catch (error) {
            console.error("Microphone access denied:", error);
            alert("Could not access microphone.");
        }
    }
});

async function processAudio(audioBlob) {
    // Show some indication that audio is being processed
    chatInput.placeholder = "Transcribing audio...";
    chatInput.disabled = true;

    try {
        const formData = new FormData();
        // The file needs a filename
        formData.append("audio", audioBlob, "voice.wav");

        const response = await fetch(`${API_BASE}/speech-to-text`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Speech-to-text failed");

        const data = await response.json();

        // Populate chat input
        if (data.text) {
            chatInput.value = data.text.trim();
        }
    } catch (error) {
        console.error("Error processing audio:", error);
        alert("Failed to transcribe audio.");
    } finally {
        chatInput.placeholder = "Type your message here.";
        chatInput.disabled = false;
        chatInput.focus();
    }
}

// Initial Greeting
addMessage("MUNCH", "Hello! I am Robo Munch. What shall we create today?");
