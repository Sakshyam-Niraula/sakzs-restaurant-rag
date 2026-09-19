/* =========================================================
   SAKZ'S RESTAURANT AI
   Frontend Application
   ========================================================= */


// =========================================================
// DOM ELEMENTS
// =========================================================

const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");

const newChatBtn = document.getElementById("newChatBtn");

const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

const characterCount = document.getElementById("characterCount");

const mobileMenuBtn = document.getElementById("mobileMenuBtn");
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");

const conversationList =
    document.getElementById("conversationList");


// =========================================================
// STATE
// =========================================================

let isLoading = false;

let conversations = [];


// =========================================================
// THEME
// =========================================================

function loadTheme() {

    const savedTheme = localStorage.getItem("sakz-theme");

    if (savedTheme === "dark") {

        document.body.classList.add("dark");

        themeIcon.textContent = "☀";
    }

    else {

        themeIcon.textContent = "☾";
    }
}


function toggleTheme() {

    document.body.classList.toggle("dark");

    const isDark =
        document.body.classList.contains("dark");

    localStorage.setItem(
        "sakz-theme",
        isDark ? "dark" : "light"
    );

    themeIcon.textContent =
        isDark ? "☀" : "☾";
}


themeToggle.addEventListener(
    "click",
    toggleTheme
);


// =========================================================
// TEXTAREA
// =========================================================

function autoResize() {

    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            130
        ) + "px";
}


messageInput.addEventListener(
    "input",
    () => {

        autoResize();

        const length =
            messageInput.value.length;

        characterCount.textContent =
            `${length} / 500`;
    }
);


// =========================================================
// ENTER TO SEND
// =========================================================

messageInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


// =========================================================
// SEND BUTTON
// =========================================================

sendBtn.addEventListener(
    "click",
    sendMessage
);


// =========================================================
// SUGGESTION BUTTONS
// =========================================================

document
    .querySelectorAll(".suggestion-card")
    .forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                const question =
                    button.dataset.question;

                sendMessage(question);
            }
        );
    });


// =========================================================
// SEND MESSAGE
// =========================================================

async function sendMessage(question = null) {

    if (isLoading) {
        return;
    }


    const text =
        question !== null
            ? question
            : messageInput.value.trim();


    if (!text) {
        return;
    }


    // Hide welcome screen
    welcomeScreen.style.display = "none";


    // Add user message
    addMessage(
        "user",
        text
    );


    // Clear input
    messageInput.value = "";

    messageInput.style.height = "auto";

    characterCount.textContent = "0 / 500";


    // Add conversation
    addConversation(text);


    // Loading state
    setLoading(true);


    const typingElement =
        addTypingIndicator();


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: text
                    })
                }
            );


        const data =
            await response.json();


        typingElement.remove();


        if (!response.ok || !data.success) {

            addMessage(
                "assistant",
                data.error ||
                "Something went wrong. Please try again."
            );

            return;
        }


        addMessage(
            "assistant",
            data.answer
        );

    }

    catch (error) {

        typingElement.remove();

        console.error(error);

        addMessage(
            "assistant",
            "I couldn't connect to the restaurant AI. "
            + "Please make sure the server is running and try again."
        );
    }

    finally {

        setLoading(false);
    }
}


// =========================================================
// ADD MESSAGE
// =========================================================

function addMessage(
    type,
    text
) {

    const message =
        document.createElement("div");

    message.className =
        `message ${type}`;


    if (type === "assistant") {

        const avatar =
            document.createElement("div");

        avatar.className =
            "assistant-avatar";

        avatar.textContent = "S";


        const content =
            document.createElement("div");


        const bubble =
            document.createElement("div");

        bubble.className =
            "message-bubble";

        bubble.textContent =
            text;


        const actions =
            document.createElement("div");

        actions.className =
            "message-actions";


        const copyButton =
            document.createElement("button");

        copyButton.className =
            "copy-btn";

        copyButton.textContent =
            "Copy answer";


        copyButton.addEventListener(
            "click",
            async () => {

                try {

                    await navigator.clipboard.writeText(
                        text
                    );

                    copyButton.textContent =
                        "Copied ✓";


                    setTimeout(
                        () => {

                            copyButton.textContent =
                                "Copy answer";

                        },
                        1500
                    );

                }

                catch (error) {

                    console.error(error);
                }
            }
        );


        actions.appendChild(copyButton);

        content.appendChild(bubble);
        content.appendChild(actions);

        message.appendChild(avatar);
        message.appendChild(content);

    }

    else {

        const bubble =
            document.createElement("div");

        bubble.className =
            "message-bubble";

        bubble.textContent =
            text;

        message.appendChild(bubble);
    }


    messages.appendChild(message);

    scrollToBottom();

    return message;
}


// =========================================================
// TYPING INDICATOR
// =========================================================

function addTypingIndicator() {

    const message =
        document.createElement("div");

    message.className =
        "message assistant";


    const avatar =
        document.createElement("div");

    avatar.className =
        "assistant-avatar";

    avatar.textContent = "S";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";


    const typing =
        document.createElement("div");

    typing.className =
        "typing";


    for (let i = 0; i < 3; i++) {

        const dot =
            document.createElement("span");

        typing.appendChild(dot);
    }


    bubble.appendChild(typing);

    message.appendChild(avatar);
    message.appendChild(bubble);

    messages.appendChild(message);

    scrollToBottom();

    return message;
}


// =========================================================
// LOADING
// =========================================================

function setLoading(state) {

    isLoading = state;

    sendBtn.disabled = state;

    messageInput.disabled = state;
}


// =========================================================
// SCROLL
// =========================================================

function scrollToBottom() {

    const chatArea =
        document.getElementById("chatArea");

    requestAnimationFrame(
        () => {

            chatArea.scrollTo(
                {
                    top:
                        chatArea.scrollHeight,

                    behavior: "smooth"
                }
            );
        }
    );
}


// =========================================================
// NEW CHAT
// =========================================================

newChatBtn.addEventListener(
    "click",
    () => {

        messages.innerHTML = "";

        welcomeScreen.style.display =
            "block";

        messageInput.value = "";

        messageInput.style.height =
            "auto";

        characterCount.textContent =
            "0 / 500";

        conversations = [];

        renderConversations();

        closeMobileSidebar();
    }
);


// =========================================================
// CONVERSATIONS
// =========================================================

function addConversation(text) {

    conversations.unshift(
        text.length > 34
            ? text.substring(0, 34) + "..."
            : text
    );


    // Keep only the latest 8
    conversations =
        conversations.slice(0, 8);


    renderConversations();
}


function renderConversations() {

    conversationList.innerHTML = "";


    if (conversations.length === 0) {

        const empty =
            document.createElement("div");

        empty.className =
            "empty-conversations";

        empty.textContent =
            "No conversations yet";

        conversationList.appendChild(empty);

        return;
    }


    conversations.forEach(
        (conversation) => {

            const item =
                document.createElement("button");

            item.style.cssText = `
                width: 100%;
                border: none;
                background: transparent;
                color: var(--text-secondary);
                text-align: left;
                padding: 9px 10px;
                border-radius: 9px;
                cursor: pointer;
                font-size: 11px;
            `;

            item.textContent =
                conversation;


            item.addEventListener(
                "mouseenter",
                () => {

                    item.style.background =
                        "var(--surface-hover)";
                }
            );


            item.addEventListener(
                "mouseleave",
                () => {

                    item.style.background =
                        "transparent";
                }
            );


            conversationList.appendChild(item);
        }
    );
}


// =========================================================
// MOBILE SIDEBAR
// =========================================================

mobileMenuBtn.addEventListener(
    "click",
    () => {

        sidebar.classList.add("open");

        sidebarOverlay.classList.add(
            "visible"
        );
    }
);


sidebarOverlay.addEventListener(
    "click",
    closeMobileSidebar
);


function closeMobileSidebar() {

    sidebar.classList.remove("open");

    sidebarOverlay.classList.remove(
        "visible"
    );
}


// =========================================================
// INITIALIZE
// =========================================================

loadTheme();

renderConversations();