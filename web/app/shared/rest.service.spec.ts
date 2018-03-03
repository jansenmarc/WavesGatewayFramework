import { async, inject, TestBed } from '@angular/core/testing';
import { RestService } from './rest.service';
import {
  BaseRequestOptions,
  ConnectionBackend,
  Http,
  RequestOptions
} from '@angular/http';
import { MockBackend } from '@angular/http/testing';

describe('RestServiceSpec', () => {
  beforeEach(
    async(() => {
      TestBed.configureTestingModule({
        providers: [
          { provide: ConnectionBackend, useClass: MockBackend },
          { provide: RequestOptions, useClass: BaseRequestOptions },
          Http,
          RestService
        ]
      });
    })
  );

  it(
    'should be created',
    inject([RestService], (restService: RestService) => {
      expect(restService).toBeDefined();
    })
  );
});
