package com.climateviz.api.services.client;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import java.util.List;
import java.util.Map;

@Service
public class WeatherPredictionClient {

    private final WebClient webClient;

    public WeatherPredictionClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build(); 
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getWeatherPrediction(String city, int days, Long user_id, String jwtToken) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder.path("/predict_future_weather/")
                        .queryParam("city", city)
                        .queryParam("days", days)
                        .queryParam("user_id", user_id)
                        .build())
                .header("Authorization", "Bearer " + jwtToken) 
                .retrieve()
                .bodyToMono(List.class)
                .block(); 
    }
}
