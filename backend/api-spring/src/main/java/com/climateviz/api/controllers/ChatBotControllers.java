package com.climateviz.api.controllers;

import com.climateviz.api.models.ChatRequest;
import com.climateviz.api.services.client.ChatBotClient;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;

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
    public Mono<ResponseEntity<byte[]>> chat(
            @RequestBody ChatRequest request_message, 
            HttpServletRequest request) {
        
        // Extraer el user_id del token JWT
        Long userId = (Long) request.getAttribute("id");
        String authHeader = request.getHeader("Authorization");

        // Debug temporal
        System.out.println("ChatBot - User ID: " + userId);

        if (userId == null) {
            throw new RuntimeException("Usuario no autenticado");
        }
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Token de autorización requerido");
        }

        // Extraer el token JWT
         String token = authHeader.substring(7);

        return chatBotClient.sendChat(request_message, userId, token)
                .map(response -> {
                    HttpHeaders headers = new HttpHeaders();
                    
                    String contentType = response.getHeaders().getFirst(HttpHeaders.CONTENT_TYPE);
                    
                    if (contentType != null && contentType.contains("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")) {
                        headers.setContentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"));
                        
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
                })
                .onErrorReturn(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body("{\"error\": \"Error interno del servidor\"}".getBytes()));
    }
}
