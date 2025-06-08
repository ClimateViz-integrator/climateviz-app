package com.climateviz.api.services.client;


import com.climateviz.api.models.ChatRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.springframework.http.ResponseEntity;


@Service
public class ChatBotClient {

    private final WebClient webClient;

    public ChatBotClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    public Mono<ResponseEntity<byte[]>> sendChat(ChatRequest request, Long user_id, String jwtToken) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder.path("/chat_bot/")
                        .queryParam("user_id", user_id)
                        .build())
                .header("Authorization", "Bearer " + jwtToken)
                .bodyValue(request)
                .retrieve()
                .toEntity(byte[].class);
    }
}


