package com.climateviz.api.services.client;


import com.climateviz.api.models.ChatRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import org.springframework.http.ResponseEntity;
import org.springframework.http.MediaType;


@Service
public class ChatBotClient {

    private final WebClient webClient;

    public ChatBotClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    public Mono<ResponseEntity<byte[]>> sendChat(ChatRequest request) {
        return webClient.post()
                .uri("/chat_bot/")
                .bodyValue(request)
                .accept(MediaType.APPLICATION_JSON, MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                .retrieve()
                .toEntity(byte[].class);
    }
}


