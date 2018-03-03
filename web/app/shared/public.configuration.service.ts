import { Injectable } from '@angular/core';
import { PublicConfiguration } from './public-configuration.model';
import { Http } from '@angular/http';
import 'rxjs/add/operator/toPromise';

@Injectable()
export class PublicConfigurationService {
  configuration: PublicConfiguration;

  constructor(private http: Http) {}

  init(): Promise<any> {
    return this.http
      .get('../api/v1/public-config')
      .map(res => res.json())
      .toPromise()
      .then(public_config => {
        this.configuration = public_config;
      });
  }
}
