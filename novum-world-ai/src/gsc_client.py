import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_top_performing_topic(site_url: str, credentials_path: str, days: int = 3) -> str:
    """
    Se conecta a Google Search Console y obtiene la query con más impresiones/clics
    en los últimos `days` días.
    """
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Credenciales de GSC no encontradas en {credentials_path}")
        
    scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
    service = build('searchconsole', 'v1', credentials=creds)
    
    # GSC data suele tener unos 2 días de retraso
    end_date = datetime.date.today() - datetime.timedelta(days=2)
    start_date = end_date - datetime.timedelta(days=days)
    
    request_body = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['query'],
        'rowLimit': 5
    }
    
    response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
    rows = response.get('rows', [])
    
    if not rows:
        return "la revolución de la Inteligencia Artificial" # Fallback temático
        
    # Ordenamos combinando clics e impresiones
    sorted_rows = sorted(rows, key=lambda x: (x.get('clicks', 0), x.get('impressions', 0)), reverse=True)
    top_query = sorted_rows[0]['keys'][0]
    
    return top_query
