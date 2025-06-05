import { HourlyData } from "./hour";

export interface LocationData {
  lat: number;
  lon: number;
  name: string;
  tz_id: string;
  region: string;
  country: string;
  localtime: string;
  localtime_epoch: number;
}

export interface ForecastData {
  city: string;
  location: LocationData;
  hours: HourlyData[];
  selectedHourIndex?: number;
}
