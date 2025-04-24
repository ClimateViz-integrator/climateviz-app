package com.climateviz.api.services.client;


import com.climateviz.api.models.ChatRequest;
import com.climateviz.api.models.ChatResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class ChatBotClient {

    private final WebClient webClient;

    public ChatBotClient(WebClient.Builder webClientBuilder) {
        // Asegúrate de usar la URL base donde se ejecuta tu servicio FastAPI
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    public Mono<ChatResponse> sendChat(ChatRequest request) {
        return webClient.post()
                .uri("/chat_bot/")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ChatResponse.class);
    }
}

