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
    public Mono<ResponseEntity<byte[]>> chat(@RequestBody ChatRequest request) {
        return chatBotClient.sendChat(request)
                .map(response -> {
                    HttpHeaders headers = new HttpHeaders();
                    
                    // Obtener el Content-Type de la respuesta original
                    String contentType = response.getHeaders().getFirst(HttpHeaders.CONTENT_TYPE);
                    
                    if (contentType != null && contentType.contains("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")) {
                        // Es un archivo Excel
                        headers.setContentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"));
                        
                        // Obtener el nombre del archivo si está disponible
                        String contentDisposition = response.getHeaders().getFirst(HttpHeaders.CONTENT_DISPOSITION);
                        if (contentDisposition != null) {
                            headers.set(HttpHeaders.CONTENT_DISPOSITION, contentDisposition);
                        } else {
                            // Generar un nombre por defecto
                            String timestamp = String.valueOf(System.currentTimeMillis());
                            headers.set(HttpHeaders.CONTENT_DISPOSITION, 
                                "attachment; filename=reporte_clima_" + timestamp + ".xlsx");
                        }
                        
                        return ResponseEntity.ok()
                                .headers(headers)
                                .body(response.getBody());
                    } else {
                        // Es una respuesta JSON normal
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
