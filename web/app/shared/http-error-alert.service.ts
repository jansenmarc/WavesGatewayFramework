import { Injectable } from '@angular/core';

@Injectable()
export class HttpErrorAlertService {
  handleError(err: any) {
    switch (err.status) {
      case 404: {
        alert('The requested ressource does not exist');
        break;
      }
      case 500: {
        alert('The server encountered an unknown error');
        break;
      }
      case 400: {
        alert('The request was not valid');
        break;
      }
      case 0: {
        alert('The server is not reachable');
        break;
      }
      default: {
        alert('An unknown Error has occurred');
      }
    }
  }
}
