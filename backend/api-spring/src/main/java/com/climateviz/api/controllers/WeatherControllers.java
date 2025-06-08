package com.climateviz.api.controllers;

import org.springframework.web.bind.annotation.*;

import com.climateviz.api.services.client.WeatherPredictionClient;

import jakarta.servlet.http.HttpServletRequest;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/weather")
public class WeatherControllers {

    private WeatherPredictionClient weatherPredictionClient = null;

    public WeatherControllers(WeatherPredictionClient weatherPredictionClient) {
        this.weatherPredictionClient = weatherPredictionClient;
    }

    @PostMapping("/predict")
    public List<Map<String, Object>> predictWeather(
            @RequestParam String city,
            @RequestParam int days,
            HttpServletRequest request) {
        
        Long userId = (Long) request.getAttribute("id");
        String authHeader = request.getHeader("Authorization");

        if (userId == null) {
            throw new RuntimeException("Usuario no autenticado");
        }

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new RuntimeException("Token de autorización requerido");
        }

        String token = authHeader.substring(7);

        try {
            return weatherPredictionClient.getWeatherPrediction(city, days, userId, token);
        } catch (Exception e) {
            throw new RuntimeException("Error al obtener predicción del clima: " + e.getMessage());
        }
    }



}
