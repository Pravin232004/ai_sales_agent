import { useEffect, useRef, useState } from "react";
import "./App.css";


function App() {

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm the AI Sales Workforce Agent. How can I help you today?"
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("ai");

  const messagesEndRef = useRef(null);


  // =======================================================
  // Auto-scroll
  // =======================================================

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });

  }, [messages]);


  // =======================================================
  // Send Message
  // =======================================================

  const sendMessage = async (customMessage = null) => {

    const userMessage = (
      customMessage !== null
        ? customMessage
        : input
    ).trim();


    if (!userMessage || loading) {
      return;
    }


    // Add user message
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: userMessage
      }
    ]);


    setInput("");
    setLoading(true);


    try {

      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            message: userMessage
          })
        }
      );


      const data = await response.json();


      // Update current mode
      if (data.mode) {
        setMode(data.mode);
      }


      // Add AI response
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data.response ||
            "I couldn't generate a response."
        }
      ]);


    } catch (error) {

      console.error("Frontend error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Unable to connect to the AI backend. " +
            "Please make sure FastAPI is running."
        }
      ]);

    } finally {

      setLoading(false);

    }
  };


  // =======================================================
  // Quick Actions
  // =======================================================

  const quickActions = [
    "What products do you offer?",
    "Tell me about pricing",
    "I want to book a demo",
    "I want to talk to sales"
  ];


  // =======================================================
  // Enter Key
  // =======================================================

  const handleKeyDown = (event) => {

    if (event.key === "Enter" && !event.shiftKey) {

      event.preventDefault();

      sendMessage();
    }
  };


  // =======================================================
  // Render
  // =======================================================

  return (

    <div className="app">

      {/* =================================================
          Header
      ================================================= */}

      <header className="app-header">

        <div className="brand">

          <div className="brand-icon">
            ✦
          </div>

          <div>

            <h1>
              AI Sales Workforce
            </h1>

            <p>
              AI-powered sales automation assistant
            </p>

          </div>

        </div>


        <div className="connection-status">

          <span className="status-dot"></span>

          <span>
            Online
          </span>

        </div>

      </header>


      {/* =================================================
          Main Chat Container
      ================================================= */}

      <main className="chat-container">

        <div className="chat-card">


          {/* =============================================
              Chat Header
          ============================================= */}

          <div className="chat-header">

            <div className="chat-title">

              <div className="chat-icon">
                AI
              </div>

              <div>

                <h2>
                  Sales Workforce Agent
                </h2>

                <p>
                  Powered by AI + RAG
                </p>

              </div>

            </div>


            <div className="live-status">

              <span className="live-dot"></span>

              {mode === "demo_fallback"
                ? "Demo Mode"
                : "Live"
              }

            </div>

          </div>


          {/* =============================================
              Messages
          ============================================= */}

          <div className="messages">

            {messages.map((message, index) => (

              <div
                key={index}
                className={`message-row ${message.role}`}
              >

                {message.role === "assistant" && (

                  <div className="message-avatar">
                    AI
                  </div>

                )}


                <div
                  className={`message-bubble ${message.role}`}
                >

                  {message.content
                    .split("\n")
                    .map((line, lineIndex) => (

                      <span key={lineIndex}>

                        {line}

                        {lineIndex <
                          message.content.split("\n").length - 1
                          && <br />
                        }

                      </span>

                    ))
                  }

                </div>

              </div>

            ))}


            {/* =========================================
                Loading
            ========================================= */}

            {loading && (

              <div className="message-row assistant">

                <div className="message-avatar">
                  AI
                </div>

                <div className="message-bubble assistant typing">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            )}


            <div ref={messagesEndRef}></div>

          </div>


          {/* =============================================
              Quick Actions
          ============================================= */}

          <div className="quick-actions">

            {quickActions.map((action) => (

              <button
                key={action}
                onClick={() => sendMessage(action)}
                disabled={loading}
              >
                {action}
              </button>

            ))}

          </div>


          {/* =============================================
              Input
          ============================================= */}

          <div className="input-area">

            <input
              type="text"
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask about products, pricing, demos..."
              disabled={loading}
            />


            <button
              className="send-button"
              onClick={() => sendMessage()}
              disabled={
                loading ||
                !input.trim()
              }
            >

              {loading
                ? "..."
                : "Send →"
              }

            </button>

          </div>


        </div>

      </main>

    </div>
  );
}


export default App;