import { Injectable } from '@angular/core';
import { Http, URLSearchParams } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { TransactionAttemptList } from './attempt-list.model';
import 'rxjs/add/operator/map';

interface AttemptListQuery {
  trigger_tx?: string;
  trigger_currency?: 'waves' | 'coin';
  trigger_receiver?: number;
  anything: string;
}

@Injectable()
export class RestService {
  constructor(private http: Http) {}

  queryAttemptList(
    query: AttemptListQuery
  ): Observable<TransactionAttemptList[]> {
    const search = new URLSearchParams();

    if (query.trigger_tx) {
      search.set('trigger_tx', query.trigger_tx);
    }

    if (query.trigger_currency) {
      search.set('trigger_currency', query.trigger_currency);
    }

    if (query.trigger_receiver) {
      search.set('trigger_receiver', '' + query.trigger_receiver);
    }

    if (query.anything) {
      search.set('anything', query.anything);
    }

    return this.http
      .get('../api/v1/attempt-list', { search: search })
      .map(res => res.json());
  }

  public getCoinAddress(wavesAddress: string): Observable<string> {
    return this.http
      .get('../api/v1/coin-address/' + wavesAddress)
      .map(res => res.text());
  }

  public getAttemptListByID(id: string): Observable<TransactionAttemptList> {
    return this.http.get('../api/v1/attempt-list/' + id).map(res => res.json());
  }
}
