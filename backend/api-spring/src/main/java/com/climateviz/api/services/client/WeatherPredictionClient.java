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
    public List<Map<String, Object>> getWeatherPrediction(String city, int days, Long userId, String jwtToken) {
        WebClient.RequestHeadersSpec<?> requestSpec = webClient.post()
                .uri(uriBuilder -> {
                    if (userId != null) {
                        return uriBuilder.path("/predict_future_weather/")
                                .queryParam("city", city)
                                .queryParam("days", days)
                                .queryParam("user_id", userId)
                                .build();
                    } else {
                        return uriBuilder.path("/predict_future_weather/")
                                .queryParam("city", city)
                                .queryParam("days", days)
                                .build();
                    }
                });

        // Solo agregar el header de autorización si hay token
        if (jwtToken != null && !jwtToken.isEmpty()) {
            requestSpec = requestSpec.header("Authorization", "Bearer " + jwtToken);
        }

        return requestSpec
                .retrieve()
                .bodyToMono(List.class)
                .block(); 
    }
}
