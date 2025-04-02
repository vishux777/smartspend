// DOM Elements
const categorizeBtn = document.getElementById('categorize-btn');
const queryBtn = document.getElementById('query-btn');
const expenseInput = document.getElementById('expense-input');
const queryInput = document.getElementById('query-input');
const chatContainer = document.getElementById('chat-container');
const queryChatContainer = document.getElementById('query-chat-container');
const historyContainer = document.getElementById('history-container');
const resetBtn = document.getElementById('reset-btn');
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const apiStatusIndicator = document.getElementById('api-status-indicator');
const apiStatusText = document.getElementById('api-status-text');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Chat history
let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

// Setup event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadThemePreference();
    updateChatHistorySidebar();
    checkApiStatus();
});

function setupEventListeners() {
    // Categorize button click
    if (categorizeBtn) {
        categorizeBtn.addEventListener('click', () => {
            categorizeExpense();
        });
    }
    
    // Query button click
    if (queryBtn) {
        queryBtn.addEventListener('click', () => {
            sendQuery();
        });
    }
    
    // Enter key pressed in expense input
    if (expenseInput) {
        expenseInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                categorizeExpense();
            }
        });
    }
    
    // Enter key pressed in query input
    if (queryInput) {
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendQuery();
            }
        });
    }
    
    // Reset button click
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            resetChat();
        });
    }
    
    // Theme toggle button click
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            toggleTheme();
        });
    }
    
    // Tab buttons click
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show selected tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

function toggleTheme() {
    const body = document.body;
    const isDarkTheme = body.classList.toggle('dark-theme');
    
    localStorage.setItem('darkTheme', isDarkTheme);
    showToast(`${isDarkTheme ? 'Dark' : 'Light'} theme activated`);
}

function loadThemePreference() {
    const darkThemePreferred = localStorage.getItem('darkTheme') === 'true';
    
    if (darkThemePreferred) {
        document.body.classList.add('dark-theme');
    }
}

function resetChat() {
    chatHistory = [];
    localStorage.removeItem('chatHistory');
    updateChatHistorySidebar();
    
    // Clear chat containers
    if (chatContainer) chatContainer.innerHTML = '';
    if (queryChatContainer) queryChatContainer.innerHTML = '';
    
    showToast('Chat history cleared');
}

// Function to check API status
async function checkApiStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'online') {
            apiStatusIndicator.classList.add('status-online');
            apiStatusText.textContent = data.api_available 
                ? 'AI API connected' 
                : 'Online (offline mode)';
                
            if (!data.api_available) {
                apiStatusIndicator.classList.add('status-offline');
            }
        } else {
            apiStatusIndicator.classList.add('status-offline');
            apiStatusText.textContent = 'API offline';
        }
    } catch (error) {
        console.error('Error checking API status:', error);
        apiStatusIndicator.classList.add('status-offline');
        apiStatusText.textContent = 'API connection error';
    }
}

// Function to categorize expense
async function categorizeExpense() {
    const description = expenseInput.value.trim();
    
    if (!description) {
        showToast('Please enter an expense description');
        return;
    }
    
    // Add user message to chat
    addMessage(description, 'user', chatContainer);
    
    // Show loading indicator
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'chat-message bot-message';
    loadingMessage.innerHTML = `
        <div class="message-avatar bot-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text">Thinking...</div>
        </div>
    `;
    chatContainer.appendChild(loadingMessage);
    
    try {
        const response = await fetch('/api/categorize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description })
        });
        
        const data = await response.json();
        
        // Remove loading message
        chatContainer.removeChild(loadingMessage);
        
        if (data.category) {
            // Add bot response
            const messageElement = addMessage(`I've categorized this as: <span class="category-tag tag-${data.category}">${data.category}</span>`, 'bot', chatContainer, true);
            
            // Save to history
            saveChatItem(description, data.category, 'category');
            
            // Clear input
            expenseInput.value = '';
        } else {
            addMessage('Sorry, I couldn\'t categorize that expense. Please try again.', 'bot', chatContainer);
        }
    } catch (error) {
        // Remove loading message
        chatContainer.removeChild(loadingMessage);
        
        console.error('Error categorizing expense:', error);
        addMessage('There was an error processing your request. Please try again.', 'bot', chatContainer);
        
        // Try local categorization as fallback
        const category = getDefaultCategory(description);
        addMessage(`Fallback categorization: <span class="category-tag tag-${category}">${category}</span>`, 'bot', chatContainer, true);
        
        // Save to history
        saveChatItem(description, category, 'category');
    }
}

// Default category function (fallback when API is unavailable)
function getDefaultCategory(description) {
    const desc = description.toLowerCase();
    
    if (desc.includes('restaurant') || desc.includes('food') || desc.includes('dinner') || 
        desc.includes('lunch') || desc.includes('breakfast') || desc.includes('coffee')) {
        return 'food';
    } else if (desc.includes('uber') || desc.includes('taxi') || desc.includes('bus') || 
        desc.includes('train') || desc.includes('gas') || desc.includes('car')) {
        return 'transportation';
    } else if (desc.includes('rent') || desc.includes('mortgage') || desc.includes('home')) {
        return 'housing';
    } else if (desc.includes('electricity') || desc.includes('water') || desc.includes('bill') || 
        desc.includes('internet') || desc.includes('phone')) {
        return 'utilities';
    } else if (desc.includes('movie') || desc.includes('netflix') || desc.includes('spotify') || 
        desc.includes('concert') || desc.includes('game')) {
        return 'entertainment';
    } else if (desc.includes('amazon') || desc.includes('mall') || desc.includes('store') || 
        desc.includes('buy') || desc.includes('purchase')) {
        return 'shopping';
    } else if (desc.includes('doctor') || desc.includes('medicine') || 
        desc.includes('hospital') || desc.includes('health')) {
        return 'health';
    } else if (desc.includes('course') || desc.includes('book') || 
        desc.includes('tuition') || desc.includes('class') || desc.includes('school')) {
        return 'education';
    } else if (desc.includes('hotel') || desc.includes('flight') || 
        desc.includes('vacation') || desc.includes('trip') || desc.includes('travel')) {
        return 'travel';
    } else {
        return 'other';
    }
}

// Function to send finance query
async function sendQuery() {
    const query = queryInput.value.trim();
    
    if (!query) {
        showToast('Please enter a question');
        return;
    }
    
    // Add user message to chat
    addMessage(query, 'user', queryChatContainer);
    
    // Show loading indicator
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'chat-message bot-message';
    loadingMessage.innerHTML = `
        <div class="message-avatar bot-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text">Thinking...</div>
        </div>
    `;
    queryChatContainer.appendChild(loadingMessage);
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        // Remove loading message
        queryChatContainer.removeChild(loadingMessage);
        
        if (data.response) {
            // Add bot response
            addMessage(data.response, 'bot', queryChatContainer);
            
            // Save to history
            saveChatItem(query, data.response, 'query');
            
            // Clear input
            queryInput.value = '';
        } else {
            addMessage('Sorry, I couldn\'t answer that question. Please try again.', 'bot', queryChatContainer);
        }
    } catch (error) {
        // Remove loading message
        queryChatContainer.removeChild(loadingMessage);
        
        console.error('Error processing query:', error);
        addMessage('There was an error processing your request. Please try again.', 'bot', queryChatContainer);
    }
}

// Function to add message to chat
function addMessage(text, sender, container, isHTML = false) {
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}-message`;
    
    const avatarContent = sender === 'user' ? '👤' : '🤖';
    
    messageElement.innerHTML = `
        <div class="message-avatar ${sender}-avatar">${avatarContent}</div>
        <div class="message-content">
            <div class="message-text">${isHTML ? text : escapeHTML(text)}</div>
        </div>
    `;
    
    container.appendChild(messageElement);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    return messageElement;
}

// Helper function to escape HTML
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Function to show toast message
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Function to save chat item to history
function saveChatItem(question, answer, type) {
    const chatItem = {
        id: Date.now(),
        question,
        answer,
        type,
        timestamp: new Date().toISOString()
    };
    
    chatHistory.push(chatItem);
    
    // Limit history to 20 items
    if (chatHistory.length > 20) {
        chatHistory.shift();
    }
    
    // Save to localStorage
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    
    // Update sidebar
    updateChatHistorySidebar();
}

// Function to update chat history sidebar
function updateChatHistorySidebar() {
    if (!historyContainer) return;
    
    if (chatHistory.length === 0) {
        historyContainer.innerHTML = '<div class="empty-history">No chat history yet</div>';
        return;
    }
    
    historyContainer.innerHTML = '';
    
    // Sort by most recent first
    const sortedHistory = [...chatHistory].reverse().slice(0, 10);
    
    sortedHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const icon = item.type === 'category' 
            ? '<i class="fas fa-tag"></i>' 
            : '<i class="fas fa-question-circle"></i>';
        
        const displayText = item.question.length > 25 
            ? item.question.slice(0, 25) + '...' 
            : item.question;
        
        historyItem.innerHTML = `
            ${icon}
            <div class="history-text">${escapeHTML(displayText)}</div>
        `;
        
        historyItem.addEventListener('click', () => {
            loadChatFromHistory(item.id);
        });
        
        historyContainer.appendChild(historyItem);
    });
}

// Function to load chat from history
function loadChatFromHistory(id) {
    const item = chatHistory.find(chat => chat.id === id);
    
    if (!item) return;
    
    if (item.type === 'category') {
        // Load into categorize tab
        tabBtns.forEach(btn => {
            if (btn.getAttribute('data-tab') === 'categorize') {
                btn.click();
            }
        });
        
        expenseInput.value = item.question;
        categorizeExpense();
    } else {
        // Load into query tab
        tabBtns.forEach(btn => {
            if (btn.getAttribute('data-tab') === 'query') {
                btn.click();
            }
        });
        
        queryInput.value = item.question;
        sendQuery();
    }
}

// Function to use example
function useExample(text) {
    const activeTab = document.querySelector('.tab-content.active').id;
    
    if (activeTab === 'categorize-tab') {
        expenseInput.value = text;
        expenseInput.focus();
    } else if (activeTab === 'query-tab') {
        queryInput.value = text;
        queryInput.focus();
    }
}