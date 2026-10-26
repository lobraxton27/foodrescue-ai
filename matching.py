"""Explainable matching heuristic; this is not a trained AI model."""
from datetime import date
from math import asin, cos, radians, sin, sqrt

def distance_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, (lat1,lon1,lat2,lon2))
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return 6371 * 2 * asin(sqrt(min(1,a)))

def rank_recipients(donation, recipients, donor):
    qty = float(donation["quantity_kg"])
    try:
        days = (date.fromisoformat(str(donation["expiration_date"])[:10])-date.today()).days
        urgency = 100 if days <= 0 else 90 if days == 1 else 75 if days <= 3 else 55 if days <= 7 else 30
    except (ValueError, TypeError):
        urgency = 50
    results = []
    for recipient in recipients:
        capacity = float(recipient.get("capacity_kg") or 0)
        if capacity < qty:
            continue
        cap_score = min(100, (capacity / qty) * 50)
        coords = all(v is not None for v in (
            donor.get("latitude") if donor else None,
            donor.get("longitude") if donor else None,
            recipient.get("latitude"), recipient.get("longitude")
        ))
        if coords:
            distance = distance_km(float(donor["latitude"]),float(donor["longitude"]),
                                    float(recipient["latitude"]),float(recipient["longitude"]))
            distance_score = max(0,100-distance)
        else:
            distance, distance_score = None, 50
        score = .4*cap_score + .4*distance_score + .2*urgency
        results.append({**recipient,"score":round(score,1),
                        "distance_km":round(distance,1) if distance is not None else None,
                        "capacity_score":round(cap_score,1),"urgency_score":round(urgency,1)})
    return sorted(results,key=lambda x:x["score"],reverse=True)
