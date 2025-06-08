package com.climateviz.api.services.client;

import com.climateviz.api.models.ChatRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class ChatBotClient {

    private final WebClient webClient;

    public ChatBotClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    public ResponseEntity<byte[]> sendChat(ChatRequest request, Long userId, String jwtToken) {
        WebClient.RequestBodySpec requestSpec = webClient.post()
                .uri(uriBuilder -> {
                    if (userId != null) {
                        return uriBuilder.path("/chat_bot/")
                                .queryParam("user_id", userId)
                                .build();
                    } else {
                        return uriBuilder.path("/chat_bot/").build();
                    }
                });

        // Solo agregar el header de autorización si hay token
        if (jwtToken != null && !jwtToken.isEmpty()) {
            requestSpec = requestSpec.header("Authorization", "Bearer " + jwtToken);
        }

        return requestSpec
                .bodyValue(request)
                .retrieve()
                .toEntity(byte[].class)
                .block();
    }
}

