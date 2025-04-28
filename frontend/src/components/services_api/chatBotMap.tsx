import React, { useState, useEffect, useRef } from "react";
import api from "../Api";
import styles from "../../pages/DashboardPublic/ChatBotPublic.module.css";
import BotIcon from "../../assets/chatbot.png";
import { Message } from "../../models/chatBot/message";

const ChatBotMap: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [inputText, setInputText] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const chatWindowRef = useRef<HTMLDivElement>(null);

  // Mantener scroll al último mensaje
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const toggleOpen = () => setIsOpen(prev => !prev);

  const getCurrentTime = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = inputText.trim();
    if (!trimmed) return;
  
    // Usuario envía mensaje
    setMessages(prev => [...prev, { 
      sender: "user", 
      text: trimmed,
      timestamp: getCurrentTime()
    }]);
    setInputText("");
    setIsLoading(true);
    setError(null);
  
    try {
     
      const resp = await api.post("chat/send", { message: trimmed });
      const botReply = resp.data.response;
      
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          sender: "bot", 
          text: botReply,
          timestamp: getCurrentTime()
        }]);
        setIsLoading(false);
      }, 500);
      
    } catch (err) {
      console.error(err);
      setError("Error al enviar el mensaje. Intenta de nuevo más tarde.");
      setIsLoading(false);
    }
  };
  
  return (
    <>
      {/* Botón flotante */}
      {!isOpen && (
        <button className={styles.chatToggleButton} onClick={toggleOpen}>
          <img src={BotIcon} alt="Chat Bot" className={styles.botIcon} />
        </button>
      )}
    
        
        {/* Ventana de chat */}
      {isOpen && (
        <div className={styles.chatWidget}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatHeaderInfo}>
              <img src={BotIcon} alt="Bot" className={styles.botIconSmall} />
              <div className={styles.chatHeaderText}>
                <h3>ClimateBot</h3>
                <p className={styles.statusText}>
                  {isLoading ? (
                    <span className={styles.typingIndicator}>escribiendo...</span>
                  ) : (
                    <span className={styles.onlineText}>en línea</span>
                  )}
                </p>
              </div>
            </div>
            <div className={styles.chatHeaderActions}>
              <button className={styles.chatCloseButton} onClick={toggleOpen}>
                <span>&times;</span>
              </button>
            </div>
          </div>

          {/* Fondo personalizado */}
          <div className={styles.chatBackground}></div>

          {/* Mensajes */}
          <div className={styles.chatWindow} ref={chatWindowRef}>
            <div className={styles.messagesContainer}>
              {messages.length === 0 && (
                <div className={styles.welcomeMessage}>
                  <div className={styles.welcomeIcon}>👋</div>
                  <p>
                    ¡Hola! Soy ClimateBot. Tu asistente en predicción del clima. 
                    Dime el nombre de la <strong className={styles.highlight}>ciudad</strong> y el número de <strong className={styles.highlight}>días</strong> para los cuales necesitas el pronóstico.
                  </p>
                  <p>Ejemplos de preguntas que puedes hacer:</p>
                  
                  <li>¿Cómo será el clima de <strong className={styles.highlight}>Manizales</strong> el <strong className={styles.highlight}>día</strong> de hoy?</li>
                  <li>¿Cuál será el clima de <strong className={styles.highlight}>Manizales</strong> en <strong className={styles.highlight}>2</strong> días?</li>
                  <li>¿Cómo estará el clima en <strong className={styles.highlight}>Bogotá</strong> dentro de <strong className={styles.highlight}>3</strong> días?</li>
              
                </div>
              
              )}
              
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`${styles.messageBubbleContainer} ${
                    msg.sender === "user" ? styles.userContainer : styles.botContainer
                  }`}
                >
                  {msg.sender === "bot" && (
                    <div className={styles.avatarContainer}>
                      <img src={BotIcon} alt="Bot" className={styles.avatarIcon} />
                    </div>
                  )}
                  <div
                    className={`${styles.messageBubble} ${
                      msg.sender === "user" ? styles.userBubble : styles.botBubble
                    }`}
                  >
                    <div className={styles.messageText}>{msg.text}</div>
                    <div className={styles.messageTime}>
                      {msg.timestamp}
                      {msg.sender === "user" && (
                        <span className={styles.checkMark}>✓✓</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className={`${styles.messageBubbleContainer} ${styles.botContainer}`}>
                  <div className={styles.avatarContainer}>
                    <img src={BotIcon} alt="Bot" className={styles.avatarIcon} />
                  </div>
                  <div className={`${styles.messageBubble} ${styles.botBubble}`}>
                    <div className={styles.typingAnimation}>
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={endRef} />
            </div>
          </div>

          {/* Error */}
          {error && <div className={styles.errorMessage}>{error}</div>}

          {/* Input y Envío */}
          <form onSubmit={handleSubmit} className={styles.chatInputForm}>
            <div className={styles.inputContainer}>
              <input
                type="text"
                placeholder="Escribe un mensaje..."
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                className={styles.futuristicInput}
                disabled={isLoading}
              />
              <button 
                type="submit" 
                className={styles.sendButton} 
                disabled={isLoading || !inputText.trim()}
              >
                <svg viewBox="0 0 24 24" width="24" height="24" className={styles.sendIcon}>
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
                </svg>
              </button>
            </div>
          </form>

          {/* Footer */}
          <div className={styles.chatFooter}>
            <span>Powered by <strong>ClimateViz</strong> AI</span>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatBotMap;
