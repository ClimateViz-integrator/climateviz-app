package com.climateviz.api.controllers;

import org.springframework.web.bind.annotation.*;

import com.climateviz.api.services.client.WeatherPredictionClient;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/weather")
public class WeatherControllers {

    private WeatherPredictionClient weatherPredictionClient = null;

    public WeatherControllers(WeatherPredictionClient weatherPredictionClient) {
        this.weatherPredictionClient = weatherPredictionClient;
    }
    
    //@GetMapping("/predict")
    /*public List<Map<String, Object>> predictWeather(
            @RequestParam String city,
            @RequestParam int days) {
        return weatherPredictionClient.getWeatherPrediction(city, days);
    }*/
    @PostMapping("/predict")
    public List<Map<String, Object>> predictWeather(@RequestBody Map<String, Object> request) {
        String city = (String) request.get("city");
        int days = Integer.parseInt(request.get("days").toString());
        return weatherPredictionClient.getWeatherPrediction(city, days);
    }
}

