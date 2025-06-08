package com.climateviz.api.controllers;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.climateviz.api.services.client.WeatherPredictionClient;

import jakarta.servlet.http.HttpServletRequest;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/weather")
public class WeatherControllers {

    private final WeatherPredictionClient weatherPredictionClient;

    public WeatherControllers(WeatherPredictionClient weatherPredictionClient) {
        this.weatherPredictionClient = weatherPredictionClient;
    }

    @PostMapping("/predict")
    public ResponseEntity<?> predictWeather(
            @RequestParam String city,
            @RequestParam int days,
            HttpServletRequest request) {
        
        Long userId = (Long) request.getAttribute("id");
        String authHeader = request.getHeader("Authorization");
        String token = null;
        boolean isAuthenticated = false;

        // Verificar si el usuario está autenticado
        if (userId != null && authHeader != null && authHeader.startsWith("Bearer ")) {
            token = authHeader.substring(7);
            isAuthenticated = true;
        }

        // Aplicar restricciones para usuarios no autenticados
        if (!isAuthenticated) {
            // Verificar si solicita predicciones de más de 2 días
            if (days > 2) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .contentType(MediaType.APPLICATION_JSON)
                        .body(Map.of(
                            "error", "El usuario no esta registrado ó aun no ha iniciado sesión"
                        ));
            }
            // Para usuarios no autenticados, enviar userId como null
            userId = null;
        }

        try {
            List<Map<String, Object>> prediction = weatherPredictionClient.getWeatherPrediction(city, days, userId, token);
            
            // Agregar información sobre el estado de autenticación en la respuesta
            Map<String, Object> response = Map.of(
                "data", prediction
            );
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error al obtener predicción del clima: " + e.getMessage()));
        }
    }
}
