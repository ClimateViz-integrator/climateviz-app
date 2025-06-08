package com.climateviz.api.controllers;

import com.climateviz.api.models.ChatRequest;
import com.climateviz.api.services.client.ChatBotClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/chat")
public class ChatBotControllers {

    private final ChatBotClient chatBotClient;
    private final ObjectMapper objectMapper;

    public ChatBotControllers(ChatBotClient chatBotClient, ObjectMapper objectMapper) {
        this.chatBotClient = chatBotClient;
        this.objectMapper = objectMapper;
    }

    @PostMapping("/send")
    public ResponseEntity<byte[]> chat(
            @RequestBody ChatRequest requestMessage,
            HttpServletRequest request) {

        Long userId = (Long) request.getAttribute("id");
        String authHeader = request.getHeader("Authorization");
        String token = null;
        boolean isAuthenticated = false;

        // Verificar si el usuario está autenticado
        if (userId != null && authHeader != null && authHeader.startsWith("Bearer ")) {
            token = authHeader.substring(7);
            isAuthenticated = true;
        }

        // Validar restricciones para usuarios no autenticados
        if (!isAuthenticated) {
            // Verificar si la solicitud requiere autenticación
            if (requiresAuthentication(requestMessage)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{\"error\": \"El usuario no esta registrado ó aun no ha iniciado sesión\", \"requiresAuth\": true}".getBytes());
            }
            // Para usuarios no autenticados, enviar userId como null
            userId = null;
        }

        try {
            ResponseEntity<byte[]> response = chatBotClient.sendChat(requestMessage, userId, token);

            HttpHeaders headers = new HttpHeaders();
            String contentType = response.getHeaders().getFirst(HttpHeaders.CONTENT_TYPE);

            if (contentType != null && contentType.contains("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")) {
                // Si es un reporte y el usuario no está autenticado, no debería llegar aquí
                // pero por seguridad adicional:
                if (!isAuthenticated) {
                    return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                            .contentType(MediaType.APPLICATION_JSON)
                            .body("{\"error\": \"Debe iniciar sesión para generar reportes\"}".getBytes());
                }

                headers.setContentType(MediaType.parseMediaType(contentType));
                String contentDisposition = response.getHeaders().getFirst(HttpHeaders.CONTENT_DISPOSITION);
                if (contentDisposition != null) {
                    headers.set(HttpHeaders.CONTENT_DISPOSITION, contentDisposition);
                } else {
                    String timestamp = String.valueOf(System.currentTimeMillis());
                    headers.set(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=reporte_clima_" + timestamp + ".xlsx");
                }

                return ResponseEntity.ok()
                        .headers(headers)
                        .body(response.getBody());
            } else {
                headers.setContentType(MediaType.APPLICATION_JSON);
                return ResponseEntity.ok()
                        .headers(headers)
                        .body(response.getBody());
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(("{\"error\": \"Error interno del servidor: " + e.getMessage() + "\"}").getBytes());
        }
    }

    /**
     * Método para determinar si una solicitud requiere autenticación
     * basado en el contenido del mensaje
     */
    private boolean requiresAuthentication(ChatRequest request) {
        String message = request.getMessage().toLowerCase();
        
        // Verificar si solicita un reporte
        if (message.contains("reporte") || message.contains("generar") || 
            message.contains("descargar") || message.contains("excel")) {
            return true;
        }
        
        // Verificar si solicita predicciones de 3+ días
        if (containsLongTermPrediction(message)) {
            return true;
        }
        
        return false;
    }

    /**
     * Método para detectar solicitudes de predicciones a largo plazo (3+ días)
     */
    private boolean containsLongTermPrediction(String message) {
        // Patrones que indican predicciones de 3+ días
        String[] longTermPatterns = {
            "3 días", "tres días", "4 días", "cuatro días", "5 días", "cinco días",
            "6 días", "seis días", "7 días", "siete días", "semana", "próxima semana",
            "siguiente semana", "10 días", "diez días", "15 días", "quince días",
            "mes", "próximo mes", "siguiente mes"
        };
        
        for (String pattern : longTermPatterns) {
            if (message.contains(pattern)) {
                return true;
            }
        }
        
        // También verificar números seguidos de "días"
        if (message.matches(".*\\b([3-9]|[1-9]\\d+)\\s*días?\\b.*")) {
            return true;
        }
        
        return false;
    }
}
