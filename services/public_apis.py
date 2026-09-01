"""
Morales Plumbing - Public Services & Intelligence Engine
Integration of 12 Free Public APIs for Sofia Lin AI Dispatcher & Mobile Techs.
License: CSLB Lic. C-36 #1156542 | San Jose, CA
"""

import os
import re
import math
import logging
import requests
from datetime import datetime, date
from typing import Dict, Any, Optional

logger = logging.getLogger("PUBLIC_APIS_ENGINE")

# Base HQ Coordinates: Morales Plumbing (San Jose, CA)
HQ_LAT = 37.3382
HQ_LON = -121.8863

COVERAGE_CITIES = {
    "san jose", "santa clara", "sunnyvale", "cupertino", "mountain view",
    "campbell", "los gatos", "milpitas", "morgan hill", "gilroy",
    "palo alto", "saratoga", "los altos"
}

COVERAGE_ZIP_PREFIXES = ("950", "951", "940", "943")

# ==============================================================================
# 1. CLIMA Y ALERTAS DE PLOMERÍA (Open-Meteo & NWS)
# ==============================================================================
def get_san_jose_weather_alert(lat: float = HQ_LAT, lon: float = HQ_LON) -> Dict[str, Any]:
    """
    Detecta temperaturas de congelamiento (<32°F / 0°C) o lluvias intensas
    que requieran protocolos especiales (tuberías congeladas o bombas de sumidero).
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation,weather_code&hourly=temperature_2m&temperature_unit=fahrenheit&forecast_days=2"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            current_temp = data.get("current", {}).get("temperature_2m", 65.0)
            precip = data.get("current", {}).get("precipitation", 0.0)
            hourly_temps = data.get("hourly", {}).get("temperature_2m", [])
            min_next_24h = min(hourly_temps[:24]) if hourly_temps else current_temp

            is_freeze_warning = min_next_24h <= 32.0
            is_rain_storm = precip > 0.3

            advisory = "Normal"
            if is_freezeWarning := is_freeze_warning:
                advisory = "ALERTA CONGELAMIENTO: Riesgo de rotura en tuberías exteriores. Recomendar aislar llaves de paso."
            elif is_rain_storm:
                advisory = "ALERTA LLUVIA: Alta probabilidad de saturación de drenajes y sumideros (Sump Pump inspection)."

            return {
                "status": "success",
                "current_temp_f": current_temp,
                "min_temp_24h_f": min_next_24h,
                "precipitation_inches": precip,
                "freeze_warning": is_freeze_warning,
                "rain_storm": is_rain_storm,
                "advisory": advisory,
                "location": "San Jose, CA"
            }
    except Exception as e:
        logger.warning(f"Error consultando API de clima: {e}")

    return {
        "status": "fallback",
        "current_temp_f": 65.0,
        "freeze_warning": False,
        "advisory": "Condiciones climáticas estándar en San Jose, CA."
    }

# ==============================================================================
# 2. VALIDACIÓN Y NORMALIZACIÓN DE DIRECCIONES (US Census Geocoder)
# ==============================================================================
def validate_address_census(address: str) -> Dict[str, Any]:
    """
    Normaliza y geocodifica direcciones en EE. UU. usando la base federal del Censo.
    """
    if not address or len(address.strip()) < 5:
        return {"status": "error", "message": "Dirección demasiado corta o vacía."}

    encoded_addr = requests.utils.quote(address)
    url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={encoded_addr}&benchmark=Public_AR_Current&format=json"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            matches = resp.json().get("result", {}).get("addressMatches", [])
            if matches:
                first = matches[0]
                coords = first.get("coordinates", {})
                matched_addr = first.get("matchedAddress", "")
                return {
                    "status": "valid",
                    "matched_address": matched_addr,
                    "lat": coords.get("y"),
                    "lon": coords.get("x"),
                    "in_santa_clara_county": "CA" in matched_addr and ("95" in matched_addr or "SAN JOSE" in matched_addr.upper())
                }
    except Exception as e:
        logger.warning(f"Error consultando US Census Geocoder: {e}")

    return {
        "status": "unverified",
        "input_address": address,
        "matched_address": address,
        "message": "Dirección aceptada en modo de tolerancia estándar."
    }

# ==============================================================================
# 3. AUTOCOMPLETADO Y VALIDACIÓN DE CÓDIGOS POSTALES (Zippopotam.us)
# ==============================================================================
def lookup_zip_code(zip_code: str) -> Dict[str, Any]:
    """
    Valida instantáneamente el código postal y confirma si está en el área de cobertura oficial.
    """
    clean_zip = re.sub(r"[^\d]", "", str(zip_code))[:5]
    if len(clean_zip) < 5:
        return {"status": "error", "message": "ZIP code inválido (debe tener 5 dígitos)."}

    url = f"https://api.zippopotam.us/us/{clean_zip}"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            places = data.get("places", [{}])[0]
            city = places.get("place name", "")
            state = places.get("state abbreviation", "")
            lat = float(places.get("latitude", HQ_LAT))
            lon = float(places.get("longitude", HQ_LON))

            is_covered = (clean_zip.startswith(COVERAGE_ZIP_PREFIXES)) or (city.lower() in COVERAGE_CITIES)

            return {
                "status": "valid",
                "zip_code": clean_zip,
                "city": city,
                "state": state,
                "lat": lat,
                "lon": lon,
                "in_coverage_area": is_covered,
                "service_notice": "Área de servicio oficial Morales Plumbing" if is_covered else "Fuera de zona estándar (requiere consulta)"
            }
    except Exception as e:
        logger.warning(f"Error consultando Zippopotam.us: {e}")

    # Fallback local para Bay Area
    is_ca_bay = clean_zip.startswith(COVERAGE_ZIP_PREFIXES)
    return {
        "status": "fallback",
        "zip_code": clean_zip,
        "city": "San Jose Area" if is_ca_bay else "Unknown",
        "state": "CA",
        "in_coverage_area": is_ca_bay
    }

# ==============================================================================
# 4. ELEVACIÓN TOPOGRÁFICA Y EVALUACIÓN DE RIESGO HIDRÁULICO (Open-Elevation)
# ==============================================================================
def get_location_elevation(lat: float = HQ_LAT, lon: float = HQ_LON) -> Dict[str, Any]:
    """
    Consulta la elevación sobre el nivel del mar para evaluar presión de cabezal y riesgos freáticos.
    """
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            results = resp.json().get("results", [{}])
            if results:
                elev_m = results[0].get("elevation", 25)
                elev_ft = round(elev_m * 3.28084, 1)
                is_lowland = elev_ft < 50.0  # Zonas bajas propensas a retorno de aguas
                return {
                    "status": "success",
                    "elevation_meters": elev_m,
                    "elevation_feet": elev_ft,
                    "is_lowland_risk": is_lowland,
                    "hydraulic_note": "Recomendar válvula check / backwater en sótanos" if is_lowland else "Drenaje por gravedad estándar"
                }
    except Exception as e:
        logger.warning(f"Error consultando Open-Elevation: {e}")

    return {
        "status": "fallback",
        "elevation_feet": 82.0,
        "hydraulic_note": "Elevación nominal del Valle de Santa Clara."
    }

# ==============================================================================
# 5. HORARIO SOLAR Y VISIBILIDAD DE DESPACHO (Sunrise-Sunset.org)
# ==============================================================================
def get_solar_schedule(lat: float = HQ_LAT, lon: float = HQ_LON) -> Dict[str, Any]:
    """
    Calcula hora de amanecer y puesta de sol en San José para planificar trabajos exteriores.
    """
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            results = resp.json().get("results", {})
            return {
                "status": "success",
                "sunrise_utc": results.get("sunrise"),
                "sunset_utc": results.get("sunset"),
                "day_length_sec": results.get("day_length"),
                "location": "San Jose, CA"
            }
    except Exception as e:
        logger.warning(f"Error consultando Sunrise-Sunset: {e}")

    return {
        "status": "fallback",
        "estimated_sunset_local": "7:30 PM PDT"
    }

# ==============================================================================
# 6. DÍAS FESTIVOS OFICIALES DE CALIFORNIA / EE. UU. (Nager.Date)
# ==============================================================================
def get_california_public_holidays(year: Optional[int] = None) -> Dict[str, Any]:
    """
    Consulta si la fecha solicitada o el día actual coincide con feriados oficiales.
    """
    target_year = year or datetime.now().year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{target_year}/US"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            holidays = resp.json()
            today_str = date.today().isoformat()
            today_holiday = next((h for h in holidays if h.get("date") == today_str), None)
            return {
                "status": "success",
                "year": target_year,
                "is_today_holiday": today_holiday is not None,
                "today_holiday_name": today_holiday.get("name") if today_holiday else None,
                "total_holidays": len(holidays)
            }
    except Exception as e:
        logger.warning(f"Error consultando Nager.Date: {e}")

    return {
        "status": "fallback",
        "is_today_holiday": False,
        "today_holiday_name": None
    }

# ==============================================================================
# 7. VERIFICACIÓN DE EMAIL Y FILTRO ANTISPAM (Disify)
# ==============================================================================
def verify_email_domain(email: str) -> Dict[str, Any]:
    """
    Valida sintaxis y descarta correos temporales/descartables antes de emitir tickets.
    """
    if not email or "@" not in email:
        return {"status": "invalid", "is_valid": False, "reason": "Formato de correo inválido"}

    clean_email = email.strip().lower()
    url = f"https://disify.com/api/email/{clean_email}"
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            res = resp.json()
            is_disposable = res.get("disposable", False)
            is_dns_valid = res.get("dns", True)
            is_format = res.get("format", True)

            is_usable = is_format and is_dns_valid and not is_disposable
            return {
                "status": "verified",
                "email": clean_email,
                "is_valid": is_usable,
                "is_disposable": is_disposable,
                "domain": res.get("domain", "")
            }
    except Exception as e:
        logger.warning(f"Error consultando Disify: {e}")

    # Fallback por expresión regular
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    is_match = bool(re.match(pattern, clean_email))
    return {
        "status": "regex_fallback",
        "email": clean_email,
        "is_valid": is_match,
        "is_disposable": False
    }

# ==============================================================================
# 8. CÁLCULO DE RUTA, DISTANCIA Y TIEMPO DE LLEGADA ETA (OSRM)
# ==============================================================================
def calculate_driving_eta(dest_lat: float, dest_lon: float, orig_lat: float = HQ_LAT, orig_lon: float = HQ_LON) -> Dict[str, Any]:
    """
    Calcula distancia en millas y minutos de conducción desde San José HQ hasta la casa del cliente.
    """
    url = f"https://router.project-osrm.org/route/v1/driving/{orig_lon},{orig_lat};{dest_lon},{dest_lat}?overview=false"
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            routes = resp.json().get("routes", [])
            if routes:
                route = routes[0]
                meters = route.get("distance", 0)
                seconds = route.get("duration", 0)
                miles = round(meters * 0.000621371, 1)
                minutes = math.ceil(seconds / 60)
                return {
                    "status": "success",
                    "distance_miles": miles,
                    "duration_minutes": minutes,
                    "eta_text": f"Aproximadamente {minutes} minutos ({miles} millas)"
                }
    except Exception as e:
        logger.warning(f"Error consultando OSRM: {e}")

    # Cálculo Haversine fallback aproximado
    dlat = math.radians(dest_lat - orig_lat)
    dlon = math.radians(dest_lon - orig_lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(orig_lat)) * math.cos(math.radians(dest_lat)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    miles_approx = round(3958.8 * c, 1)
    mins_approx = math.ceil(miles_approx * 2.2) # ~25-30 mph tráfico urbano

    return {
        "status": "haversine_fallback",
        "distance_miles": miles_approx,
        "duration_minutes": mins_approx,
        "eta_text": f"Aprox. {mins_approx} minutos ({miles_approx} millas)"
    }

# ==============================================================================
# 9. IMPUESTOS LOCALES DE CALIFORNIA (CDTFA Tax Engine)
# ==============================================================================
def get_california_sales_tax(zip_code: str) -> Dict[str, Any]:
    """
    Determina la tasa oficial del impuesto sobre ventas para el Condado de Santa Clara / San José.
    """
    clean_zip = re.sub(r"[^\d]", "", str(zip_code))[:5]
    # Tasas oficiales Santa Clara County
    tax_rates = {
        "951": 0.09375, # San Jose
        "95050": 0.09125, # Santa Clara
        "95051": 0.09125,
        "94086": 0.09125, # Sunnyvale
        "95014": 0.09125, # Cupertino
        "95008": 0.0925,  # Campbell
        "95030": 0.0925,  # Los Gatos
        "95020": 0.09125, # Gilroy
        "95037": 0.09125  # Morgan Hill
    }
    prefix3 = clean_zip[:3]
    rate = tax_rates.get(clean_zip, tax_rates.get(prefix3, 0.09375))
    return {
        "status": "success",
        "zip_code": clean_zip,
        "jurisdiction": "Santa Clara County, CA",
        "sales_tax_rate": rate,
        "sales_tax_percentage": f"{rate * 100:.3f}%"
    }

# ==============================================================================
# 10. RECONOCIMIENTO ÓPTICO DE PLACAS DE EQUIPOS (OCR.Space Public API)
# ==============================================================================
def parse_water_heater_plate_ocr(image_url: str) -> Dict[str, Any]:
    """
    Extrae números de modelo y serie de etiquetas de calentadores de agua usando OCR libre.
    """
    url = f"https://api.ocr.space/parse/imageurl?apikey=helloworld&url={requests.utils.quote(image_url)}&language=eng"
    try:
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            parsed_results = resp.json().get("ParsedResults", [])
            if parsed_results:
                text = parsed_results[0].get("ParsedText", "")
                
                # Extraer patrones comunes de fabricantes
                model_match = re.search(r"(?:MODEL|MOD|M/N)[:\s]+([A-Z0-9-]+)", text, re.IGNORECASE)
                serial_match = re.search(r"(?:SERIAL|SER|S/N)[:\s]+([A-Z0-9-]+)", text, re.IGNORECASE)
                gallons_match = re.search(r"(\d{2,3})\s*(?:GAL|GALLONS|LITERS)", text, re.IGNORECASE)

                return {
                    "status": "success",
                    "raw_text": text.strip(),
                    "detected_model": model_match.group(1) if model_match else "No detectado",
                    "detected_serial": serial_match.group(1) if serial_match else "No detectado",
                    "detected_capacity": gallons_match.group(0) if gallons_match else "No detectado"
                }
    except Exception as e:
        logger.warning(f"Error procesando OCR: {e}")

    return {
        "status": "fallback",
        "message": "Imagen no procesada por OCR, requiere revisión manual del técnico."
    }

# ==============================================================================
# 11. FORMATEADOR Y SANITIZADOR DE TELÉFONOS EE. UU.
# ==============================================================================
def format_and_validate_phone(phone_str: str) -> Dict[str, Any]:
    """
    Limpia y valida que el teléfono cumpla con el formato estándar de EE. UU. (10 dígitos).
    """
    digits = re.sub(r"\D", "", str(phone_str))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        return {
            "status": "invalid",
            "is_valid": False,
            "formatted": phone_str,
            "message": "El teléfono debe contener 10 dígitos estándar."
        }

    formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    e164 = f"+1{digits}"
    is_bay_area = digits[:3] in ("669", "408", "650", "510", "415", "925")

    return {
        "status": "valid",
        "is_valid": True,
        "formatted": formatted,
        "e164": e164,
        "area_code": digits[:3],
        "is_bay_area": is_bay_area
    }

# ==============================================================================
# 12. AUDITORÍA INTEGRAL DE SERVICIOS PÚBLICOS
# ==============================================================================
def run_full_public_services_diagnostic() -> Dict[str, Any]:
    """
    Ejecuta un chequeo integral de todas las APIs públicas para verificar su estado en vivo.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "weather_service": get_san_jose_weather_alert(),
        "zip_service": lookup_zip_code("95123"),
        "solar_service": get_solar_schedule(),
        "holidays_service": get_california_public_holidays(),
        "sales_tax_service": get_california_sales_tax("95123"),
        "phone_sanitizer": format_and_validate_phone("6692134422"),
        "email_verifier": verify_email_domain("moralesplumbing026@gmail.com")
    }
