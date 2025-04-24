package com.climateviz.api.controllers;


import com.climateviz.api.models.ChatRequest;
import com.climateviz.api.models.ChatResponse;
import com.climateviz.api.services.client.ChatBotClient;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/chat")
public class ChatBotControllers {

    private final ChatBotClient chatBotClient;

    public ChatBotControllers(ChatBotClient chatBotClient) {
        this.chatBotClient = chatBotClient;
    }

    @PostMapping("/send")
    public Mono<ChatResponse> chat(@RequestBody ChatRequest request) {
        return chatBotClient.sendChat(request);
    }
}

