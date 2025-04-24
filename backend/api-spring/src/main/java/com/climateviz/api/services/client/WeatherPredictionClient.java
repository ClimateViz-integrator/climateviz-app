package com.climateviz.api.services.client;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import java.util.List;
import java.util.Map;

@Service
public class WeatherPredictionClient {

    private final WebClient webClient;

    public WeatherPredictionClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build(); // Cambia la URL si tu API está en otro lado
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getWeatherPrediction(String city, int days) {
        return webClient.post()
                .uri(uriBuilder -> uriBuilder.path("/predict_future_weather/")
                        .queryParam("city", city)
                        .queryParam("days", days)
                        .build())
                .retrieve()
                .bodyToMono(List.class) // La respuesta es una lista de objetos JSON
                .block(); // Bloquea hasta obtener respuesta (para código síncrono)
    }
}
