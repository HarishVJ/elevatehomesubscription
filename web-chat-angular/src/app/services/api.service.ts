import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { SearchRequest, SearchResponse } from '../models/product.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Health check endpoint
   */
  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }

  /**
   * Complete workflow: Research + Find Replacements
   */
  completeSearch(request: SearchRequest): Observable<SearchResponse> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<SearchResponse>(
      `${this.apiUrl}/complete`,
      request,
      { headers }
    );
  }

  /**
   * Research a product only
   */
  researchProduct(brand: string, model: string, applianceType: string): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post(
      `${this.apiUrl}/research`,
      { brand, model, appliance_type: applianceType },
      { headers }
    );
  }

  /**
   * Find replacements only
   */
  findReplacements(productSpec: any): Observable<any> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post(
      `${this.apiUrl}/replacements`,
      productSpec,
      { headers }
    );
  }
}
