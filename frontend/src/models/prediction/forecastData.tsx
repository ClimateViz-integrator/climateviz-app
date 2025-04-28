import { HourlyData } from "./hour";

export interface ForecastData {
    city: string;
    location: { lat: number; lon: number };
    hours: HourlyData[];
    selectedHourIndex?: number;
  }