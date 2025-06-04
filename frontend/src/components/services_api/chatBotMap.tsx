import React, { useState, useEffect, useRef } from "react";
import api from "../Api";
import styles from "../../pages/DashboardPublic/ChatBotPublic.module.css";
import BotIcon from "../../assets/chatbot.png";
import { ExtendedMessage } from "../../models/chatBot/extendMessage";


const ChatBotMap: React.FC = () => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [inputText, setInputText] = useState<string>("");
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
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

  // Función para descargar archivo
  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  // Función para abrir archivo en nueva pestaña
  const openFile = (blob: Blob) => {
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
    // Limpiar la URL después de un tiempo para liberar memoria
    setTimeout(() => window.URL.revokeObjectURL(url), 1000);
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
      // Hacer la petición con responseType: 'blob' para manejar archivos
      const resp = await api.post("chat/send", 
        { message: trimmed }, 
        { 
          responseType: 'blob',
          headers: {
            'Accept': 'application/json, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          }
        }
      );
      
      // Verificar el Content-Type de la respuesta
      const contentType = resp.headers['content-type'];
      
      setTimeout(() => {
        if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
          // Es un archivo Excel
          const blob = new Blob([resp.data], { 
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
          });
          
          // Generar nombre de archivo con timestamp
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const filename = `reporte_clima_${timestamp}.xlsx`;
          
          // Agregar mensaje del bot con el archivo adjunto
          setMessages(prev => [...prev, { 
            sender: "bot", 
            text: "📊 He generado tu reporte de clima. Puedes descargarlo o abrirlo directamente:",
            timestamp: getCurrentTime(),
            fileData: {
              blob: blob,
              filename: filename,
              type: 'excel'
            }
          }]);
        } else {
          // Es una respuesta JSON normal
          // Convertir blob a texto para extraer la respuesta
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const jsonResponse = JSON.parse(reader.result as string);
              const botReply = jsonResponse.response || "Respuesta recibida";
              
              setMessages(prev => [...prev, { 
                sender: "bot", 
                text: botReply,
                timestamp: getCurrentTime()
              }]);
            } catch (parseError) {
              console.error("Error parsing JSON response:", parseError);
              setMessages(prev => [...prev, { 
                sender: "bot", 
                text: "Error al procesar la respuesta del servidor.",
                timestamp: getCurrentTime()
              }]);
            }
          };
          reader.readAsText(resp.data);
        }
        setIsLoading(false);
      }, 500);
      
    } catch (err: any) {
      console.error(err);
      
      // Si hay un error, intentar leer el mensaje de error del blob
      if (err.response && err.response.data instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const errorResponse = JSON.parse(reader.result as string);
            setError(errorResponse.detail || "Error al enviar el mensaje.");
          } catch {
            setError("Error al enviar el mensaje. Intenta de nuevo más tarde.");
          }
        };
        reader.readAsText(err.response.data);
      } else {
        setError("Error al enviar el mensaje. Intenta de nuevo más tarde.");
      }
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
                  <li>Genera un <strong className={styles.highlight}>reporte</strong> de los datos climaticos</li>
              
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
                    <div className={styles.messageText}>
                      {msg.text}
                      
                      {/* Mostrar botones de archivo si existe */}
                      {msg.fileData && (
                        <div className={styles.fileAttachment}>
                          <div className={styles.fileInfo}>
                            <div className={styles.fileIcon}>📄</div>
                            <div className={styles.fileDetails}>
                              <span className={styles.fileName}>{msg.fileData.filename}</span>
                              <span className={styles.fileType}>Archivo Excel</span>
                            </div>
                          </div>
                          <div className={styles.fileActions}>
                            <button 
                              className={`${styles.fileButton} ${styles.downloadButton}`}
                              onClick={() => downloadFile(msg.fileData!.blob, msg.fileData!.filename)}
                            >
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7,10 12,15 17,10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                              </svg>
                              Descarga
                            </button>
                            <button 
                              className={`${styles.fileButton} ${styles.openButton}`}
                              onClick={() => openFile(msg.fileData!.blob)}
                            >
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                                <polyline points="15,3 21,3 21,9"/>
                                <line x1="10" y1="14" x2="21" y2="3"/>
                              </svg>
                              Abrir
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
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